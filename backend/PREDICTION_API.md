# 智能预测 API 使用文档

## 📋 概述

本 API 提供基于随机森林算法的机器学习预测功能，可以对 CSV 数据集中的任意数值列进行预测分析。

## 🚀 快速开始

### 1. 启动后端服务

```bash
cd backend
python main.py
```

服务将在 `http://localhost:8000` 启动

### 2. 启动前端服务

```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 3. 访问预测页面

在浏览器中打开前端地址，点击侧边栏的 **"🔮 智能预测"** 菜单项

## 📡 API 接口

### POST /predict

对指定的目标列进行机器学习预测

**请求地址：** `http://localhost:8000/predict`

**请求方法：** POST

**请求头：**
```
Content-Type: application/json
```

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 | 默认值 |
|--------|------|------|------|--------|
| target_column | string | 是 | 要预测的目标列名称 | - |
| csv_path | string | 否 | CSV文件路径 | `C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv` |

**请求示例：**

```json
{
  "target_column": "forks"
}
```

或指定自定义 CSV 路径：

```json
{
  "target_column": "stars",
  "csv_path": "/path/to/your/data.csv"
}
```

**响应格式：**

```json
{
  "success": true,
  "data": {
    "predictions": {
      "metadata": {
        "target_column": "forks",
        "feature_columns": ["feat_stars", "feat_watchers", ...],
        "total_samples": 300,
        "valid_samples": 300,
        "train_samples": 210,
        "test_samples": 90,
        "metrics": {
          "R2_score": 0.8523,
          "RMSE": "1.23e+02",
          "MAE": "8.45e+01"
        }
      },
      "predictions": [
        {
          "project_name": "项目名称",
          "true_value": 1234,
          "predicted_value": 1189,
          "absolute_error": 45,
          "relative_error_percent": 3.65
        },
        ...
      ]
    },
    "feature_importance": {
      "feature_importance": [
        {
          "feature_name": "feat_stars",
          "importance": 0.4523
        },
        {
          "feature_name": "feat_watchers",
          "importance": 0.2341
        },
        ...
      ]
    }
  }
}
```

**错误响应：**

```json
{
  "detail": "预测失败: 目标列无有效数值数据"
}
```

## 🎯 功能特性

### 1. 预测结果 (predictions)

- **元数据 (metadata)**
  - 目标列名称
  - 使用的特征列
  - 样本数量统计
  - 模型评估指标（R²、RMSE、MAE）

- **预测列表 (predictions)**
  - 项目名称
  - 真实值
  - 预测值
  - 绝对误差
  - 相对误差百分比

### 2. 特征重要性 (feature_importance)

- 按重要性降序排列的特征列表
- 每个特征的重要性分数（0-1之间）
- 可用于理解哪些因素对预测结果影响最大

## 📊 支持的目标列

根据你的数据集，可以预测以下列（示例）：

- `stars` - 星标数
- `forks` - Fork数
- `watchers` - 关注者数
- `contributors` - 贡献者数
- `issues` - Issue数量
- `pull_requests` - PR数量
- `commits` - 提交数
- `activity` - 活跃度
- 以及其他任何数值型列

## 🔧 技术实现

### 算法
- **模型：** 随机森林回归 (Random Forest Regressor)
- **特征工程：** 自动从CSV中提取数值特征
- **数据预处理：** RobustScaler 标准化
- **数据拆分：** 70% 训练集 / 30% 测试集

### 评估指标
- **R² Score：** 决定系数，衡量模型拟合优度
- **RMSE：** 均方根误差，预测值与真实值的平均偏差
- **MAE：** 平均绝对误差，预测误差的平均值

## 💡 使用建议

1. **选择合适的目标列**
   - 确保目标列包含足够的数值数据
   - 避免选择包含大量缺失值的列

2. **理解预测结果**
   - R² 越接近 1，模型拟合越好
   - RMSE 和 MAE 越小，预测越准确
   - 查看相对误差百分比评估预测质量

3. **分析特征重要性**
   - 重要性高的特征对预测影响大
   - 可用于业务洞察和决策支持

## 🐛 常见问题

**Q: 预测失败，提示"目标列无有效数值数据"**
A: 检查选择的列是否包含数值数据，或者数据是否有太多缺失值

**Q: 预测结果不准确**
A: 可能原因：
- 数据量太小
- 特征与目标列相关性低
- 数据质量问题

**Q: 后端服务无法启动**
A: 确保已安装所有依赖：
```bash
pip install pandas numpy scikit-learn fastapi uvicorn
```

## 📝 示例代码

### JavaScript/Axios

```javascript
import axios from 'axios'

const predict = async (targetColumn) => {
  try {
    const response = await axios.post('http://localhost:8000/predict', {
      target_column: targetColumn
    })
    
    if (response.data.success) {
      console.log('预测结果:', response.data.data.predictions)
      console.log('特征重要性:', response.data.data.feature_importance)
    }
  } catch (error) {
    console.error('预测失败:', error.response?.data?.detail)
  }
}

// 使用
predict('forks')
```

### Python/Requests

```python
import requests

def predict(target_column):
    url = 'http://localhost:8000/predict'
    data = {'target_column': target_column}
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print('预测结果:', result['data']['predictions'])
            print('特征重要性:', result['data']['feature_importance'])
    else:
        print('预测失败:', response.json()['detail'])

# 使用
predict('forks')
```

## 📞 技术支持

如有问题，请查看：
- 后端日志输出
- 浏览器控制台错误信息
- 确认数据文件路径正确

