import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')

# ==================== 基础配置 ====================
np.random.seed(42)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['figure.dpi'] = 100


# ==================== 封装的预测函数 ====================
def predict_fork_count(csv_path: str = r"C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv") -> dict:
    """
    预测 Fork 数量（默认使用 technical_fork 列，即第32列）

    参数:
        csv_path: CSV文件路径（可选，有默认值）

    返回:
        包含预测结果和特征重要性的字典
        {
            "metadata": {...},           # 元数据信息（包含模型选择、性能指标等）
            "model_comparison": {...},   # 模型对比结果
            "predictions": [...],        # 预测结果列表
            "feature_importance": [...]  # 特征重要性列表
        }
    """
    # 固定使用第32列：technical_fork
    target_column = "technical_fork"

    return predict_target_column(csv_path, target_column)


def predict_target_column(csv_path: str, target_column: str) -> dict:
    """
    对指定的目标列进行预测（内部函数）- 多模型对比版本

    参数:
        csv_path: CSV文件路径
        target_column: 目标列名称

    返回:
        包含预测结果和特征重要性的字典
        {
            "metadata": {...},           # 元数据信息
            "model_comparison": {...},   # 模型对比结果
            "predictions": [...],        # 预测结果
            "feature_importance": [...]  # 特征重要性
        }
    """
    try:
        # 1. 加载数据
        df = pd.read_csv(csv_path, encoding='utf-8')

        # 2. 处理目标列
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

        df['target_numeric'] = convert_to_numeric(df[target_column])
        df_clean = df.dropna(subset=['target_numeric']).reset_index(drop=True)

        if len(df_clean) == 0:
            raise ValueError("目标列无有效数值数据")

        # 3. 特征工程（智能选择特征）
        potential_features = []

        # 候选特征列表
        candidate_features = [
            'bus_factor', 'change_requests', 'change_requests_accepted',
            'change_requests_reviews', 'code_change_lines_add',
            'code_change_lines_remove', 'inactive_contributors',
            'issues_closed', 'issues_new', 'issue_comments',
            'new_contributors'
        ]

        # 转换为数值特征并计算相关性
        for col in candidate_features:
            if col in df_clean.columns:
                try:
                    df_clean[f'feat_{col}'] = pd.to_numeric(df_clean[col], errors='coerce')
                    corr = df_clean[f'feat_{col}'].corr(df_clean['target_numeric'])
                    if abs(corr) < 0.95:  # 排除过高相关性（避免数据泄漏）
                        median_val = df_clean[f'feat_{col}'].median()
                        df_clean[f'feat_{col}'] = df_clean[f'feat_{col}'].fillna(median_val)
                        potential_features.append(f'feat_{col}')
                except:
                    continue

        # 如果特征太少，添加衍生特征
        if len(potential_features) < 3:
            if 'feat_code_change_lines_add' in df_clean.columns and 'feat_code_change_lines_remove' in df_clean.columns:
                df_clean['feat_code_change_ratio'] = (df_clean['feat_code_change_lines_add'] + 1) / (df_clean['feat_code_change_lines_remove'] + 1)
                potential_features.append('feat_code_change_ratio')

            if 'feat_issues_closed' in df_clean.columns and 'feat_issues_new' in df_clean.columns:
                df_clean['feat_issue_resolution_rate'] = (df_clean['feat_issues_closed'] + 1) / (df_clean['feat_issues_new'] + 1)
                potential_features.append('feat_issue_resolution_rate')

        feature_cols = potential_features if potential_features else ['feat_index']

        # 如果没有任何特征，使用索引
        if not potential_features:
            df_clean['feat_index'] = df_clean.index
            feature_cols = ['feat_index']

        # 4. 数据准备
        X = df_clean[feature_cols]
        y = df_clean['target_numeric']

        X_train, X_test, y_train, y_test, train_idx, test_idx = train_test_split(
            X, y, df_clean.index, test_size=0.3, random_state=42
        )

        # 标准化
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        X_train_scaled = scaler_X.fit_transform(X_train)
        X_test_scaled = scaler_X.transform(X_test)
        y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()

        # 5. 多模型训练与评估
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

        results = {}
        for name, model in models.items():
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
                'r2_train': float(r2_train),
                'r2_test': float(r2_test),
                'rmse_test': float(rmse_test),
                'mae_test': float(mae_test),
                'overfitting_gap': float(r2_train - r2_test),
                'y_pred': y_pred.tolist(),
                'y_true': y_true.tolist()
            }

        # 6. 选择最佳模型（基于测试集R²，同时惩罚过拟合）
        best_model_name = None
        best_score = -float('inf')

        for name, result in results.items():
            # 惩罚过拟合严重的模型
            penalty = 0
            if result['overfitting_gap'] > 0.2:
                penalty = 0.3  # 严重过拟合
            elif result['overfitting_gap'] > 0.1:
                penalty = 0.1  # 轻微过拟合

            score = result['r2_test'] - penalty

            if score > best_score:
                best_score = score
                best_model_name = name

        best_result = results[best_model_name]
        best_model = best_result['model']

        # 7. 特征重要性
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

        # 8. 格式化预测值
        def format_prediction_value(value, original_series):
            """格式化预测值"""
            try:
                if original_series.dropna().apply(lambda x: float(x).is_integer()).all():
                    return int(round(value))
                else:
                    return round(float(value), 4)
            except:
                return round(float(value), 4)

        # 9. 获取最佳模型的预测结果
        y_pred = np.array(best_result['y_pred'])
        y_true = np.array(best_result['y_true'])

        # 10. 构建结果字典
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
            "predictions": [],
            "feature_importance": []
        }

        # 添加模型比较信息
        for name, result in results.items():
            output_results["model_comparison"][name] = {
                "R2_train": float(result['r2_train']),
                "R2_test": float(result['r2_test']),
                "overfitting_gap": float(result['overfitting_gap']),
                "selected": bool(name == best_model_name)
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

        # 添加特征重要性
        if importance_df is not None:
            for _, row in importance_df.iterrows():
                output_results["feature_importance"].append({
                    "feature_name": str(row['feature_name']),
                    "importance": float(row['importance']),
                    "abs_importance": float(row['abs_importance'])
                })

        # 11. 返回结果
        return output_results

    except Exception as e:
        raise Exception(f"预测失败: {str(e)}")


# ==================== 命令行脚本模式 ====================
# 只有直接运行此文件时才会执行以下代码，被导入时不会执行
if __name__ == "__main__":
    # ==================== 1. 加载CSV数据 ====================
    print("【1/8】加载CSV数据...")
    csv_path = r"C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv"

    def load_csv_data(file_path):
        """加载CSV文件"""
        try:
            df = pd.read_csv(file_path)
            print(f"  ✓ 成功加载文件: {file_path}")
            print(f"  ✓ 数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
            print(f"  ✓ 列名列表: {list(df.columns)}")
            print(f"  ✓ 前5行预览:")
            print(df.head())
            return df
        except FileNotFoundError:
            print(f"❌ 文件未找到: {file_path}")
            print("请确认文件路径是否正确。当前路径下的文件列表:")
            folder = os.path.dirname(file_path)
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if f.endswith('.csv'):
                        print(f"  - {f}")
            exit()
        except Exception as e:
            print(f"❌ 加载CSV文件失败: {str(e)}")
            exit()

    try:
        df = load_csv_data(csv_path)
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
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()
    X_train_scaled = scaler_X.fit_transform(X_train)
    X_test_scaled = scaler_X.transform(X_test)
    y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()

    print(f"✓ 拆分完成：训练集 {len(X_train)} 条，测试集 {len(X_test)} 条")

    # ==================== 5. 多模型训练与评估 ====================
    print("\n【5/8】多模型训练与评估...")

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
            'r2_train': float(r2_train),
            'r2_test': float(r2_test),
            'rmse_test': float(rmse_test),
            'mae_test': float(mae_test),
            'overfitting_gap': float(r2_train - r2_test),
            'y_pred': y_pred.tolist(),
            'y_true': y_true.tolist()
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
            "selected": bool(name == best_model_name)
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
        "is_overfitted": bool(best_result['overfitting_gap'] > 0.15),
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