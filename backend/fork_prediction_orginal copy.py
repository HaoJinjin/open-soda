import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')

# ==================== 基础配置 ====================
np.random.seed(42)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 100

# ==================== 1. 加载JSON数据 ====================
print("【1/8】加载数据（递归读取JSON文件夹）...")
csv_path = r"C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv"

def load_json_from_folder(folder_path):
    all_data = []
    for file_path in Path(folder_path).rglob('*.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            if isinstance(json_data, dict):
                all_data.append(json_data)
            elif isinstance(json_data, list):
                all_data.extend(json_data)
            print(f"  ✓ 加载文件: {file_path}")
        except Exception as e:
            print(f"  ⚠️  读取失败: {file_path}, 错误: {str(e)}")
    if not all_data:
        raise ValueError("❌ 未找到有效JSON数据")
    df = pd.DataFrame(all_data)
    print(f"\n✓ 加载完成：{df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"  列名列表：{list(df.columns)}")
    return df

try:
    df = load_json_from_folder(root_folder)
except Exception as e:
    print(e)
    exit()

# ==================== 2. 选择目标列并处理类型 ====================
print("\n【2/8】选择并处理目标列...")
# 展示列名供选择
cols = list(df.columns)
for idx, col in enumerate(cols):
    print(f"  [{idx}] {col}")

# 选择目标列
target_column = None
while not target_column:
    user_input = input("\n输入目标列序号/列名：").strip()
    if user_input.isdigit():
        idx = int(user_input)
        if 0 <= idx < len(cols):
            target_column = cols[idx]
        else:
            print(f"❌ 序号超出范围（0-{len(cols)-1}）")
    elif user_input in cols:
        target_column = user_input
    else:
        print(f"❌ 列名 '{user_input}' 不存在")

print(f"✓ 选中目标列：{target_column}")

# 处理目标列类型
def convert_to_numeric(col_data):
    """智能转换为数值型（兼容时间/数字）"""
    # 尝试转换为时间戳（如果是时间字符串）
    try:
        # 常见时间格式匹配
        time_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d', '%Y%m%d']
        for fmt in time_formats:
            try:
                return pd.to_datetime(col_data, format=fmt).astype('int64') // 10**9  # 转秒级时间戳
            except:
                continue
        # 自动识别时间格式
        return pd.to_datetime(col_data).astype('int64') // 10**9
    except:
        # 转换为普通数值
        return pd.to_numeric(col_data, errors='coerce')

# 转换目标列并清理空值
df['target_numeric'] = convert_to_numeric(df[target_column])
df_clean = df.dropna(subset=['target_numeric']).reset_index(drop=True)
print(f"✓ 目标列处理完成：{len(df_clean)} 条有效数据")
if len(df_clean) == 0:
    print("❌ 目标列无有效数值数据")
    exit()

# ==================== 3. 生成基础特征（无原始特征时） ====================
print("\n【3/8】生成特征...")
# 自动生成基础特征（基于现有列）
feature_cols = []

# 1. 对所有非目标列尝试转为数值特征
for col in df_clean.columns:
    if col not in [target_column, 'target_numeric']:
        try:
            # 尝试转换为数值
            df_clean[f'feat_{col}'] = pd.to_numeric(df_clean[col], errors='coerce')
            # 尝试转换时间为时间戳
            if pd.isna(df_clean[f'feat_{col}']).all():
                df_clean[f'feat_{col}'] = convert_to_numeric(df_clean[col])
            # 移除全空特征
            if not pd.isna(df_clean[f'feat_{col}']).all():
                df_clean[f'feat_{col}'] = df_clean[f'feat_{col}'].fillna(0)
                feature_cols.append(f'feat_{col}')
        except:
            continue

# 2. 如果无任何特征，生成简单序列特征
if not feature_cols:
    print("⚠️  无有效特征列，生成序列特征")
    df_clean['feat_index'] = df_clean.index  # 行索引特征
    df_clean['feat_random'] = np.random.rand(len(df_clean))  # 随机特征（兜底）
    feature_cols = ['feat_index', 'feat_random']

print(f"✓ 生成特征：{feature_cols}")

# ==================== 4. 数据准备 ====================
print("\n【4/8】数据拆分与标准化...")
X = df_clean[feature_cols]
y = df_clean['target_numeric']

# 拆分数据集
X_train, X_test, y_train, y_test, train_idx, test_idx = train_test_split(
    X, y, df_clean.index, test_size=0.3, random_state=42
)

# 标准化
scaler_X = RobustScaler()
scaler_y = RobustScaler()
X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()

print(f"✓ 拆分完成：训练集 {len(X_train)} 条，测试集 {len(X_test)} 条")

# ==================== 5. 模型训练 ====================
print("\n【5/8】训练模型...")
# 调整模型参数适配小特征集
rf_model = RandomForestRegressor(
    n_estimators=50,  # 减少树数量
    max_depth=5,      # 降低复杂度
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train_scaled)

# 预测并反标准化
y_pred_scaled = rf_model.predict(X_test_scaled)
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
y_true = y_test.values

# ==================== 6. 模型评估 ====================
print("\n【6/8】模型评估...")
# 计算评估指标（兼容大数）
r2 = r2_score(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mae = mean_absolute_error(y_true, y_pred)

# 格式化输出（科学计数法适配大数）
print(f"  R² 得分：{r2:.4f}")
print(f"  RMSE：{rmse:.2e}")  # 科学计数法
print(f"  MAE：{mae:.2e}")

# ==================== 7. 生成预测结果（还原原始格式） ====================
print("\n【7/8】生成预测结果...")
# 还原目标值为原始格式
def revert_numeric_to_original(numeric_val, original_data):
    """将数值型结果还原为原始格式"""
    # 如果是时间戳，转回时间字符串
    try:
        original_sample = original_data.dropna().iloc[0]
        # 检查原始数据是否为时间
        pd.to_datetime(original_sample)
        return datetime.fromtimestamp(int(numeric_val)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        # 普通数值
        return round(float(numeric_val), 2)

# 构建结果字典
results = {
    "metadata": {
        "target_column": target_column,
        "feature_columns": feature_cols,
        "total_samples": len(df),
        "valid_samples": len(df_clean),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "metrics": {
            "R2_score": round(r2, 4),
            "RMSE": f"{rmse:.2e}",
            "MAE": f"{mae:.2e}"
        }
    },
    "predictions": []
}

# 填充预测结果
for i, idx in enumerate(test_idx):
    # 原始项目名称（尽量获取）
    proj_name = ""
    for name_col in ['name', 'projectname', 'repo', 'repository']:
        if name_col in df_clean.columns and pd.notna(df_clean.loc[idx, name_col]):
            proj_name = str(df_clean.loc[idx, name_col])
            break
    if not proj_name:
        proj_name = f"项目_{idx}"
    
    # 还原真实值和预测值
    true_val = revert_numeric_to_original(y_true[i], df[target_column])
    pred_val = revert_numeric_to_original(y_pred[i], df[target_column])
    
    results["predictions"].append({
        "project_name": proj_name,
        "true_value": true_val,
        "predicted_value": pred_val,
        "absolute_error": round(abs(y_true[i] - y_pred[i]), 2),
        "relative_error_percent": round(abs((y_true[i] - y_pred[i])/(y_true[i]+1e-8))*100, 2)
    })

# ==================== 8. 保存结果 ====================
print("\n【8/8】保存结果...")
# 保存预测结果
output_pred = r'C:\Users\22390\Desktop\OpenSODA\backendData\prediction_results.json'
with open(output_pred, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

# 保存特征重要性
importance = pd.DataFrame({
    "feature_name": feature_cols,
    "importance": rf_model.feature_importances_
}).sort_values('importance', ascending=False)

importance_dict = {
    "feature_importance": importance.to_dict('records')
}
output_imp = r'C:\Users\22390\Desktop\OpenSODA\backendData\feature_importance.json'
with open(output_imp, 'w', encoding='utf-8') as f:
    json.dump(importance_dict, f, ensure_ascii=False, indent=4)

print(f"✓ 预测结果：{output_pred}")
print(f"✓ 特征重要性：{output_imp}")
print("\n🎉 任务完成！")