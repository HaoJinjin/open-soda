import csv
import json
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 导入封装的预测函数
from fork_prediction import run_fork_prediction
from indicators_stat import get_indicator_statistics
from predict_response_time_xgboost import predict_response_time

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

# 响应时间预测任务状态（全局变量）
response_time_task_status = {
    "status": "idle",  # idle, running, completed, error
    "progress": 0,
    "message": "",
    "result": None,
    "error": None
}


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


# ==================== 新增的3个预测接口 ====================

@app.post("/api/predict/fork")
async def api_predict_fork():
    """
    预测 Fork 数量（使用 technical_fork 列）
    返回:
        {
            "success": true,
            "data": {
                {
                "metadata": {...},
                "model_comparison": {...},
                "feature_importance": {...},
                "predictions": [...],
                "summary": {...}
                }
            }
        }
    """
    try:
        result = run_fork_prediction(
        csv_path="backendData/top_300_metrics.csv"
    )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fork预测失败: {str(e)}"
        )


@app.get("/api/statistics/indicators")
async def api_get_indicators_stats():
    try:
        result = get_indicator_statistics()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取指标统计失败: {str(e)}"
        )


# ==================== 响应时间预测接口（支持后台任务和轮询） ====================

def run_response_time_prediction():
    """后台任务：运行响应时间预测"""
    global response_time_task_status

    def progress_callback(progress, message):
        """进度回调函数"""
        response_time_task_status["progress"] = progress
        response_time_task_status["message"] = message

    try:
        response_time_task_status["status"] = "running"
        response_time_task_status["progress"] = 0
        response_time_task_status["message"] = "开始预测..."
        response_time_task_status["error"] = None

        # 调用预测函数
        result = predict_response_time(progress_callback=progress_callback)

        response_time_task_status["status"] = "completed"
        response_time_task_status["progress"] = 100
        response_time_task_status["message"] = "预测完成！"
        response_time_task_status["result"] = result

    except Exception as e:
        response_time_task_status["status"] = "error"
        response_time_task_status["error"] = str(e)
        response_time_task_status["message"] = f"预测失败: {str(e)}"


@app.post("/api/predict/response-time/start")
async def api_start_response_time_prediction(background_tasks: BackgroundTasks):
    """
    启动响应时间预测（后台任务）

    返回:
        {
            "success": true,
            "message": "任务已启动"
        }
    """
    global response_time_task_status

    if response_time_task_status["status"] == "running":
        return {
            "success": False,
            "message": "任务正在运行中，请稍后再试"
        }

    # 重置任务状态
    response_time_task_status = {
        "status": "idle",
        "progress": 0,
        "message": "",
        "result": None,
        "error": None
    }

    # 添加后台任务
    background_tasks.add_task(run_response_time_prediction)

    return {
        "success": True,
        "message": "任务已启动"
    }


@app.get("/api/predict/response-time/status")
async def api_get_response_time_status():
    """
    查询响应时间预测任务进度

    返回:
        {
            "success": true,
            "data": {
                "status": "idle|running|completed|error",
                "progress": 0-100,
                "message": "当前步骤描述"
            }
        }
    """
    return {
        "success": True,
        "data": {
            "status": response_time_task_status["status"],
            "progress": response_time_task_status["progress"],
            "message": response_time_task_status["message"],
            "error": response_time_task_status["error"]
        }
    }


@app.get("/api/predict/response-time/result")
async def api_get_response_time_result():
    """
    获取响应时间预测结果

    返回:
        {
            "success": true,
            "data": {
                "metadata": {...},
                "model_evaluation": {...},
                "future_prediction": {...},
                "historical_data_sample": [...]
            }
        }
    """
    if response_time_task_status["status"] != "completed":
        return {
            "success": False,
            "message": f"任务未完成，当前状态: {response_time_task_status['status']}"
        }

    return {
        "success": True,
        "data": response_time_task_status["result"]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
