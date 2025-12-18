# 🚀 OpenSODA 预测 API 文档

## 📋 目录

1. [Fork 预测接口](#1-fork-预测接口)
2. [指标统计接口](#2-指标统计接口)
3. [响应时间预测接口](#3-响应时间预测接口)

---

## 1. Fork 预测接口

### `POST /api/predict/fork`

预测项目的 Fork 数量（使用 technical_fork 列）

**请求参数：** 无

**响应示例：**
```json
{
  "success": true,
  "data": {
    "predictions": {
      "metadata": {
        "target_column": "technical_fork",
        "feature_columns": [...],
        "total_samples": 300,
        "valid_samples": 281,
        "train_samples": 224,
        "test_samples": 57,
        "metrics": {
          "R2_score": 0.9234,
          "RMSE": "1.23e+02",
          "MAE": "8.45e+01"
        }
      },
      "predictions": [
        {
          "project_name": "stable-diffusion-webui",
          "true_value": 35.0,
          "predicted_value": 33.5,
          "absolute_error": 1.5,
          "relative_error_percent": 4.29
        },
        ...
      ]
    },
    "feature_importance": {
      "feature_importance": [
        {
          "feature_name": "stars",
          "importance": 0.3456
        },
        ...
      ]
    }
  }
}
```

**前端调用示例：**
```javascript
const response = await axios.post('http://localhost:8000/api/predict/fork')
console.log(response.data.data.predictions)
console.log(response.data.data.feature_importance)
```

---

## 2. 指标统计接口

### `GET /api/statistics/indicators`

获取6个核心指标的统计信息（用于前端渲染热力图、分布图、Top10对比图）

**请求参数：** 无

**响应示例：**
```json
{
  "success": true,
  "data": {
    "metadata": {
      "data_source": "top_300_metrics.csv",
      "total_projects": 300,
      "valid_projects": 281,
      "missing_data_ratio": "6.33%",
      "analysis_indicators": [
        "inactive_contributors",
        "issues_and_change_request_active",
        "issues_closed",
        "issues_new",
        "new_contributors",
        "participants"
      ]
    },
    "indicator_statistics": [
      {
        "indicator_column": "inactive_contributors",
        "indicator_name": "非活跃贡献者",
        "mean": 27.0569,
        "median": 3.0,
        "std": 307.7765,
        "min": 1.0,
        "max": 5155.0,
        "quantile_25": 1.0,
        "quantile_75": 8.0,
        "quantile_95": 29.0
      },
      ...
    ],
    "correlation_matrix": {
      "inactive_contributors": {
        "inactive_contributors": 1.0,
        "issues_and_change_request_active": 0.844,
        ...
      },
      ...
    },
    "top10_projects": [
      {
        "project_name": "stable-diffusion-webui",
        "original_index": 0,
        "indicator_values": {
          "inactive_contributors": 4.0,
          "inactive_contributors_scaled": -0.0749,
          ...
        }
      },
      ...
    ]
  }
}
```

**前端调用示例：**
```javascript
const response = await axios.get('http://localhost:8000/api/statistics/indicators')
const data = response.data.data

// 1. 渲染热力图（使用 correlation_matrix）
const heatmapData = []
const indicators = Object.keys(data.correlation_matrix)
indicators.forEach((row, i) => {
  indicators.forEach((col, j) => {
    heatmapData.push([i, j, data.correlation_matrix[row][col]])
  })
})

// 2. 渲染分布直方图（使用 indicator_statistics）
const chartData = data.indicator_statistics.map(item => ({
  name: item.indicator_name,
  mean: item.mean,
  median: item.median
}))

// 3. 渲染Top10对比图（使用 top10_projects）
const projects = data.top10_projects.map(p => p.project_name)
const seriesData = data.metadata.analysis_indicators.map(ind => ({
  name: ind,
  data: data.top10_projects.map(p => p.indicator_values[ind])
}))
```

---

## 3. 响应时间预测接口

由于预测时间较长，使用**异步任务 + 轮询**机制。

### 3.1 `POST /api/predict/response-time/start`

启动响应时间预测任务（后台运行）

**请求参数：** 无

**响应示例：**
```json
{
  "success": true,
  "message": "任务已启动"
}
```

### 3.2 `GET /api/predict/response-time/status`

查询任务进度（轮询此接口）

**请求参数：** 无

**响应示例：**
```json
{
  "success": true,
  "data": {
    "status": "running",  // idle, running, completed, error
    "progress": 56,       // 0-100
    "message": "【4/7】数据清洗与预处理...",
    "error": null
  }
}
```

### 3.3 `GET /api/predict/response-time/result`

获取预测结果（任务完成后调用）

**请求参数：** 无

**响应示例：**
```json
{
  "success": true,
  "data": {
    "metadata": {
      "data_source": "top_300_metrics.csv",
      "target_metric": "change_request_response_time",
      "total_projects": 300,
      "valid_samples": 18426,
      "feature_columns": [...],
      "best_model": "XGBoost"
    },
    "model_evaluation": {
      "XGBoost": {
        "r2_train": 0.9988,
        "r2_test": 0.979,
        "mae": 0.69,
        "rmse": 1.92,
        "cv_mean": 0.975,
        "cv_std": 0.0062,
        "mape": 260204877.82
      }
    },
    "future_prediction": {
      "prediction_time_points": ["2023-04", "2023-05", ...],
      "predicted_response_time": [1.61, 1.61, ...],
      "prediction_explanation": "预测未来6个月的Change Request响应时间"
    },
    "historical_data_sample": [
      {
        "time_str": "2022-08",
        "response_time": 0.0,
        "year": 2022,
        "month": 8
      },
      ...
    ]
  }
}
```

**前端完整调用流程：**
```javascript
// 1. 启动任务
await axios.post('http://localhost:8000/api/predict/response-time/start')

// 2. 轮询查询进度
const pollStatus = setInterval(async () => {
  const statusRes = await axios.get('http://localhost:8000/api/predict/response-time/status')
  const { status, progress, message } = statusRes.data.data
  
  console.log(`进度: ${progress}% - ${message}`)
  
  if (status === 'completed') {
    clearInterval(pollStatus)
    
    // 3. 获取结果
    const resultRes = await axios.get('http://localhost:8000/api/predict/response-time/result')
    console.log(resultRes.data.data)
    
    // 4. 渲染图表
    renderCharts(resultRes.data.data)
  } else if (status === 'error') {
    clearInterval(pollStatus)
    console.error('预测失败')
  }
}, 2000) // 每2秒轮询一次
```

---

## 🎨 前端数据可视化建议

### 1. Fork 预测页面
- **预测结果表格**：显示项目名称、真实值、预测值、误差
- **特征重要性柱状图**：横向柱状图展示 Top 10 特征
- **模型评估指标卡片**：R²、RMSE、MAE

### 2. 指标统计页面
- **相关性热力图**：使用 `correlation_matrix` 数据
- **指标分布直方图**：6个子图，每个指标一个
- **Top10项目对比图**：堆叠柱状图或雷达图

### 3. 响应时间预测页面
- **进度条**：显示实时进度和步骤信息
- **历史趋势图**：折线图展示历史数据
- **未来预测图**：虚线展示未来6个月预测
- **模型评估卡片**：展示 XGBoost 模型指标

---

## 🔧 启动服务

```bash
cd C:\Users\22390\Desktop\OpenSODA
python backend/main.py
```

服务将在 `http://localhost:8000` 启动

---

## ✅ 总结

| 接口 | 方法 | 路径 | 用途 | 是否异步 |
|------|------|------|------|---------|
| Fork预测 | POST | `/api/predict/fork` | 预测Fork数量 | ❌ 同步 |
| 指标统计 | GET | `/api/statistics/indicators` | 获取统计信息 | ❌ 同步 |
| 启动响应时间预测 | POST | `/api/predict/response-time/start` | 启动后台任务 | ✅ 异步 |
| 查询预测进度 | GET | `/api/predict/response-time/status` | 轮询进度 | ✅ 异步 |
| 获取预测结果 | GET | `/api/predict/response-time/result` | 获取最终结果 | ✅ 异步 |

🎉 **所有接口已就绪，可以开始前端开发了！**

