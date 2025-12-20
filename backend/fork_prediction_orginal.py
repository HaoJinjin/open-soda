import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
import warnings
warnings.filterwarnings('ignore')

# ==================== 基础配置 ====================
np.random.seed(42)

# ==================== 1. 加载CSV数据 ====================
print("【1/8】加载CSV数据...")
csv_path = r"C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv"

def load_csv_data(file_path,):
    """加载CSV文件"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"  ✓ 加载文件: {file_path}")
        print(f"  数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
        return df
    except FileNotFoundError:
        raise ValueError(f"❌ 文件不存在: {file_path}")
    except Exception as e:
        raise ValueError(f"❌ 读取CSV失败: {str(e)}")

try:
    df = load_csv_data(csv_path)
except Exception as e:
    print(e)
    exit()

# ==================== 2. 选择目标列并处理类型 ====================
print("\n【2/8】选择并处理目标列...")
target_column = 'technical_fork'
print(f"✓ 使用目标列：{target_column}")

def convert_to_numeric(col_data):
    """智能转换为数值型"""
    try:
        numeric = pd.to_numeric(col_data, errors='coerce')
        if numeric.isna().mean() < 0.5:
            return numeric
    except:
        pass
    
    try:
        time_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d', '%Y%m%d']
        for fmt in time_formats:
            try:
                return pd.to_datetime(col_data, format=fmt, errors='raise').astype('int64') // 10**9
            except:
                continue
        return pd.to_datetime(col_data, errors='coerce').astype('int64') // 10**9
    except:
        return pd.to_numeric(col_data, errors='coerce')

# 转换目标列
df['target_numeric'] = convert_to_numeric(df[target_column])
df_clean = df.dropna(subset=['target_numeric']).reset_index(drop=True)
print(f"✓ 有效数据: {len(df_clean)} 条")

# 目标列统计
print(f"\n目标列统计信息：")
print(f"  均值: {df_clean['target_numeric'].mean():.2f}")
print(f"  标准差: {df_clean['target_numeric'].std():.2f}")
print(f"  最小值: {df_clean['target_numeric'].min():.2f}")
print(f"  最大值: {df_clean['target_numeric'].max():.2f}")

# ==================== 3. 特征工程 ====================
print("\n【3/8】特征工程...")

# 排除可能泄漏的特征
potential_features = []

# 选择特征
candidate_features = [
    'bus_factor', 'change_requests', 'change_requests_accepted',
    'change_requests_reviews', 'code_change_lines_add',
    'code_change_lines_remove', 'inactive_contributors',
    'issues_closed', 'issues_new', 'issue_comments',
    'new_contributors'
]

# 转换为数值特征
for col in candidate_features:
    if col in df_clean.columns:
        try:
            df_clean[f'feat_{col}'] = pd.to_numeric(df_clean[col], errors='coerce')
            corr = df_clean[f'feat_{col}'].corr(df_clean['target_numeric'])
            if abs(corr) < 0.95:  # 排除过高相关性
                median_val = df_clean[f'feat_{col}'].median()
                df_clean[f'feat_{col}'] = df_clean[f'feat_{col}'].fillna(median_val)
                potential_features.append(f'feat_{col}')
                print(f"  {col}: 相关性={corr:.3f}")
        except:
            continue

# 如果特征太少，添加衍生特征
if len(potential_features) < 3:
    print("  生成衍生特征...")
    if 'feat_code_change_lines_add' in df_clean.columns and 'feat_code_change_lines_remove' in df_clean.columns:
        df_clean['feat_code_change_ratio'] = (df_clean['feat_code_change_lines_add'] + 1) / (df_clean['feat_code_change_lines_remove'] + 1)
        potential_features.append('feat_code_change_ratio')
    
    if 'feat_issues_closed' in df_clean.columns and 'feat_issues_new' in df_clean.columns:
        df_clean['feat_issue_resolution_rate'] = (df_clean['feat_issues_closed'] + 1) / (df_clean['feat_issues_new'] + 1)
        potential_features.append('feat_issue_resolution_rate')

feature_cols = potential_features
print(f"✓ 使用特征: {len(feature_cols)} 个")

# ==================== 4. 数据准备 ====================
print("\n【4/8】数据拆分与标准化...")
X = df_clean[feature_cols]
y = df_clean['target_numeric']

# 拆分数据集
X_train, X_test, y_train, y_test, train_idx, test_idx = train_test_split(
    X, y, df_clean.index, test_size=0.3, random_state=42
)

# 标准化
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()

print(f"✓ 拆分完成：训练集 {len(X_train)} 条，测试集 {len(X_test)} 条")

# ==================== 5. 模型训练与评估 ====================
print("\n【5/8】模型训练与评估...")

# 定义模型
models = {
    'Ridge回归': Ridge(alpha=1.0, random_state=42),
    'Lasso回归': Lasso(alpha=0.1, random_state=42),
    '梯度提升': GradientBoostingRegressor(
        n_estimators=50, 
        max_depth=3, 
        learning_rate=0.1, 
        random_state=42,
        subsample=0.8
    ),
    '支持向量机': SVR(kernel='linear', C=1.0, epsilon=0.1),
}

# 训练和评估每个模型
results = {}
for name, model in models.items():
    print(f"\n  训练 {name}...")
    
    # 训练模型
    model.fit(X_train_scaled, y_train_scaled)
    
    # 预测
    y_pred_scaled = model.predict(X_test_scaled)
    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
    y_true = y_test.values
    
    # 训练集预测（用于检测过拟合）
    y_train_pred_scaled = model.predict(X_train_scaled)
    y_train_pred = scaler_y.inverse_transform(y_train_pred_scaled.reshape(-1, 1)).flatten()
    
    # 计算指标
    r2_train = r2_score(y_train, y_train_pred)
    r2_test = r2_score(y_true, y_pred)
    rmse_test = np.sqrt(mean_squared_error(y_true, y_pred))
    mae_test = mean_absolute_error(y_true, y_pred)
    
    results[name] = {
        'model': model,
        'r2_train': float(r2_train),  # 转换为Python float
        'r2_test': float(r2_test),    # 转换为Python float
        'rmse_test': float(rmse_test), # 转换为Python float
        'mae_test': float(mae_test),   # 转换为Python float
        'overfitting_gap': float(r2_train - r2_test),  # 转换为Python float
        'y_pred': y_pred.tolist(),    # numpy数组转列表
        'y_true': y_true.tolist()     # numpy数组转列表
    }
    
    print(f"    训练集R²: {r2_train:.4f}")
    print(f"    测试集R²: {r2_test:.4f}")
    print(f"    过拟合差距: {r2_train - r2_test:.4f}")
    print(f"    RMSE: {rmse_test:.2e}")
    print(f"    MAE: {mae_test:.2e}")

# 选择最佳模型（基于测试集R²，同时考虑过拟合）
best_model_name = None
best_score = -float('inf')

for name, result in results.items():
    # 惩罚过拟合严重的模型
    penalty = 0
    if result['overfitting_gap'] > 0.2:
        penalty = 0.3  # 严重过拟合，大幅惩罚
    elif result['overfitting_gap'] > 0.1:
        penalty = 0.1  # 轻微过拟合，轻微惩罚
    
    score = result['r2_test'] - penalty
    
    if score > best_score:
        best_score = score
        best_model_name = name

print(f"\n✓ 选择最佳模型：{best_model_name}")
best_result = results[best_model_name]
best_model = best_result['model']

# ==================== 6. 特征重要性 ====================
print("\n【6/8】特征重要性分析...")

importance_df = None
if hasattr(best_model, 'coef_'):
    # 线性模型
    importance = best_model.coef_
    if isinstance(importance, np.ndarray):
        importance = importance.tolist()
    
    importance_df = pd.DataFrame({
        "feature_name": feature_cols,
        "importance": importance,
        "abs_importance": [abs(x) for x in importance]
    }).sort_values('abs_importance', ascending=False)
    
elif hasattr(best_model, 'feature_importances_'):
    # 树模型
    importance = best_model.feature_importances_.tolist()
    importance_df = pd.DataFrame({
        "feature_name": feature_cols,
        "importance": importance,
        "abs_importance": importance
    }).sort_values('abs_importance', ascending=False)

if importance_df is not None:
    print(f"\n📈 特征重要性排名：")
    for i, row in importance_df.iterrows():
        print(f"  {row['feature_name']:30s}: {row['importance']:.6f}")
else:
    print("⚠️  该模型不支持特征重要性分析")

# ==================== 7. 生成预测结果 ====================
print("\n【7/8】生成预测结果...")

def format_prediction_value(value, original_series):
    """格式化预测值"""
    try:
        if original_series.dropna().apply(lambda x: float(x).is_integer()).all():
            return int(round(value))
        else:
            return round(float(value), 4)
    except:
        return round(float(value), 4)

# 获取最佳模型的预测结果
y_pred = np.array(best_result['y_pred'])
y_true = np.array(best_result['y_true'])

# 构建结果字典 - 确保所有值都是JSON可序列化的
output_results = {
    "metadata": {
        "target_column": target_column,
        "model_used": best_model_name,
        "feature_columns": feature_cols,
        "total_samples": int(len(df)),
        "valid_samples": int(len(df_clean)),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "performance_metrics": {
            "R2_train": float(best_result['r2_train']),
            "R2_test": float(best_result['r2_test']),
            "RMSE_test": float(best_result['rmse_test']),
            "MAE_test": float(best_result['mae_test']),
            "overfitting_gap": float(best_result['overfitting_gap'])
        },
        "model_selection_note": "选择标准：测试集R²最高，同时惩罚过拟合严重的模型"
    },
    "model_comparison": {},
    "predictions": []
}

# 添加模型比较信息
for name, result in results.items():
    output_results["model_comparison"][name] = {
        "R2_train": float(result['r2_train']),
        "R2_test": float(result['r2_test']),
        "overfitting_gap": float(result['overfitting_gap']),
        "selected": bool(name == best_model_name)  # 转换为Python bool
    }

# 填充预测结果
for i, idx in enumerate(test_idx):
    # 获取项目名称
    proj_name = ""
    for name_col in ['projectname', 'projectname2']:
        if name_col in df_clean.columns and pd.notna(df_clean.loc[idx, name_col]):
            proj_name = str(df_clean.loc[idx, name_col])
            break
    if not proj_name:
        proj_name = f"项目_{idx}"
    
    # 格式化值
    true_val = format_prediction_value(y_true[i], df[target_column])
    pred_val = format_prediction_value(y_pred[i], df[target_column])
    
    absolute_error = abs(float(y_true[i]) - float(y_pred[i]))
    relative_error = abs((float(y_true[i]) - float(y_pred[i])) / (abs(float(y_true[i])) + 1e-8)) * 100
    
    output_results["predictions"].append({
        "project_name": proj_name,
        "true_value": float(true_val) if isinstance(true_val, (int, float)) else true_val,
        "predicted_value": float(pred_val) if isinstance(pred_val, (int, float)) else pred_val,
        "absolute_error": round(float(absolute_error), 4),
        "relative_error_percent": round(float(relative_error), 2)
    })

# ==================== 8. 保存结果 ====================
print("\n【8/8】保存结果...")

# 创建输出目录
output_dir = r'C:\Users\22390\Desktop\OpenSODA\backendData'
os.makedirs(output_dir, exist_ok=True)

# 保存预测结果
output_pred = os.path.join(output_dir, 'prediction_results_fixed.json')
with open(output_pred, 'w', encoding='utf-8') as f:
    json.dump(output_results, f, ensure_ascii=False, indent=4)

print(f"✓ 预测结果：{output_pred}")

# 保存特征重要性
if importance_df is not None:
    # 转换importance_df中的值为Python原生类型
    importance_records = []
    for _, row in importance_df.iterrows():
        record = {
            "feature_name": str(row['feature_name']),
            "importance": float(row['importance']),
            "abs_importance": float(row['abs_importance'])
        }
        importance_records.append(record)
    
    importance_dict = {
        "model": best_model_name,
        "feature_importance": importance_records
    }
    output_imp = os.path.join(output_dir, 'feature_importance_fixed.json')
    with open(output_imp, 'w', encoding='utf-8') as f:
        json.dump(importance_dict, f, ensure_ascii=False, indent=4)
    print(f"✓ 特征重要性：{output_imp}")

# 保存模型评估摘要
summary = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "target_column": target_column,
    "best_model": best_model_name,
    "test_r2": float(best_result['r2_test']),
    "test_rmse": float(best_result['rmse_test']),
    "overfitting_gap": float(best_result['overfitting_gap']),
    "is_overfitted": bool(best_result['overfitting_gap'] > 0.15),  # 转换为Python bool
    "features_used": int(len(feature_cols))
}
output_summary = os.path.join(output_dir, 'model_summary_fixed.json')
with open(output_summary, 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=4)

print(f"✓ 模型摘要：{output_summary}")

# 输出最终报告
print(f"\n🎉 任务完成！")
print(f"\n📋 最终报告：")
print(f"  最佳模型: {best_model_name}")
print(f"  测试集R²: {best_result['r2_test']:.4f}")
print(f"  训练集R²: {best_result['r2_train']:.4f}")
print(f"  过拟合差距: {best_result['overfitting_gap']:.4f}")
print(f"  是否过拟合: {'是' if best_result['overfitting_gap'] > 0.15 else '否'}")

# 输出所有模型比较
print(f"\n📊 模型比较：")
print(f"  {'模型名称':<15} {'训练R²':<10} {'测试R²':<10} {'过拟合差距':<12} {'选择'}")
print("-" * 60)
for name, result in results.items():
    selected = "✓" if name == best_model_name else ""
    print(f"  {name:<15} {result['r2_train']:.4f}     {result['r2_test']:.4f}     {result['overfitting_gap']:.4f}        {selected}")

# 解释结果
print(f"\n📝 结果解释：")
if best_result['r2_test'] > 0.7:
    print("  ✅ 模型表现优秀")
elif best_result['r2_test'] > 0.5:
    print("  ⚠️  模型表现一般")
elif best_result['r2_test'] > 0.3:
    print("  ⚠️  模型表现较差")
else:
    print("  ❌ 模型表现非常差")

if best_result['overfitting_gap'] > 0.2:
    print("  ❌ 严重过拟合：建议减少特征或增加正则化")
elif best_result['overfitting_gap'] > 0.1:
    print("  ⚠️  轻微过拟合：模型泛化能力一般")
else:
    print("  ✅ 过拟合风险低：模型泛化能力良好")

# 检查是否仍然过拟合
if best_result['r2_test'] > 0.95:
    print(f"\n⚠️  警告：模型可能仍然过拟合或存在数据泄漏！")
    print(f"  可能原因：")
    print(f"  1. 特征与目标列高度相关")
    print(f"  2. 数据量太小（仅{len(df_clean)}条）")
    print(f"  3. 特征工程需要调整")



