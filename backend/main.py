import csv
import json
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from backend.fork_prediction import predict_target_column

app = FastAPI()

# 配置CORS，允许前端请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks: Dict[str, Dict[str, Any]] = {}


class ConvertRequest(BaseModel):
    file_path: str


class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    result: Any = None


class PredictionRequest(BaseModel):
    target_column: str
    csv_path: str = r"C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv"


async def convert_csv_to_json(task_id: str, file_path: str) -> None:
    try:
        tasks[task_id]["status"] = "processing"

        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # 增加CSV字段大小限制到10MB
        csv.field_size_limit(10 * 1024 * 1024)

        with open(file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            if csv_reader.fieldnames is None:
                raise ValueError("CSV file is empty")

            total_rows = sum(1 for _ in open(file_path, 'r', encoding='utf-8')) - 1
            rows = []

            for idx, row in enumerate(csv_reader):
                rows.append(row)
                progress = int((idx + 1) / total_rows * 100)
                tasks[task_id]["progress"] = progress
                await asyncio.sleep(0)

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["message"] = "Conversion completed successfully"
        tasks[task_id]["result"] = {
            "data": rows,
            "row_count": len(rows)
        }
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = str(e)


@app.post("/convert", response_model=Dict[str, str])
async def start_conversion(request: ConvertRequest):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "message": "Waiting to start",
        "result": None
    }
    
    asyncio.create_task(convert_csv_to_json(task_id, request.file_path))
    
    return {"task_id": task_id}


@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        result=task["result"]
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/predict")
async def predict(request: PredictionRequest):
    """
    预测接口

    请求参数:
        - target_column: 目标列名称（必填）
        - csv_path: CSV文件路径（可选，默认使用配置的路径）

    返回:
        {
            "success": true,
            "data": {
                "predictions": {...},        // 预测结果
                "feature_importance": {...}  // 特征重要性
            }
        }
    """
    try:
        # 调用预测函数
        result = predict_target_column(
            csv_path=request.csv_path,
            target_column=request.target_column
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"预测失败: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
