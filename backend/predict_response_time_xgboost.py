import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')


# ==================== 封装的预测函数 ====================
def predict_response_time(csv_path: str = r'C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv',
                         progress_callback=None) -> dict:
    """
    预测 Change Request 响应时间（支持进度回调）

    参数:
        csv_path: CSV文件路径（可选，有默认值）
        progress_callback: 进度回调函数，接收 (progress, message) 参数
                          progress: 0-100 的整数
                          message: 当前步骤描述

    返回:
        包含预测结果的字典
        {
            "metadata": {...},           # 元数据信息
            "model_evaluation": {...},   # 模型评估指标
            "future_prediction": {...},  # 未来预测结果
            "historical_data_sample": [...] # 历史数据样本
        }
    """
    def update_progress(progress, message):
        """更新进度"""
        if progress_callback:
            progress_callback(progress, message)

    try:
        # 【1/7】加载数据
        update_progress(14, "【1/7】加载数据...")
        df = pd.read_csv(csv_path)

        # 【2/7】跳过时序可视化（不生成图片）
        update_progress(28, "【2/7】解析时序数据...")

        # 【3/7】构建预测数据集
        update_progress(42, "【3/7】构建预测数据集...")
        pred_data = []
        project_meta = {}

        for idx, row in df.iterrows():
            proj_id = idx
            proj_name = row.get('projectname2', f'项目_{idx}')
            project_meta[proj_id] = proj_name

            # 解析响应时间数据
            times, values = parse_time_series_dict(row.get('change_request_response_time', ''))
            if len(times) < 3:
                continue

            # 注意：times 中的元素已经是 '2022-08' 这样的字符串格式
            for time_str, response_time in zip(times, values):
                time_features = time_to_features(time_str)
                pred_data.append({
                    'project_id': proj_id,
                    'time_str': time_str,
                    'response_time': response_time,
                    **time_features
                })

        pred_df = pd.DataFrame(pred_data)
        pred_df = add_temporal_features(pred_df)

        # 【4/7】数据清洗与预处理
        update_progress(56, "【4/7】数据清洗与预处理...")
        y = pred_df['response_time'].values
        Q1, Q3 = np.percentile(y, [25, 75])
        IQR = Q3 - Q1
        mask = (y >= Q1 - 2 * IQR) & (y <= Q3 + 2 * IQR)
        pred_df_clean = pred_df[mask].reset_index(drop=True)

        # 特征和目标
        feature_cols = ['year', 'month', 'quarter', 'month_order', 'is_quarter_end',
                       'is_year_end', 'is_peak_season', 'month_sin', 'month_cos',
                       'response_time_ma_3', 'response_time_ma_6',
                       'response_time_std_3', 'response_time_std_6',
                       'response_time_diff_1', 'response_time_lag_1', 'response_time_lag_2']

        X = pred_df_clean[feature_cols].values
        y = pred_df_clean['response_time'].values

        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 标准化
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # 【5/7】模型训练与调优
        update_progress(70, "【5/7】模型训练与调优...")

        # XGBoost 模型
        xgb_model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        xgb_model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )

        # 预测
        y_pred_train = xgb_model.predict(X_train_scaled)
        y_pred_test = xgb_model.predict(X_test_scaled)

        # 评估指标
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        mae = mean_absolute_error(y_test, y_pred_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))

        # 交叉验证
        tscv = TimeSeriesSplit(n_splits=5)
        cv_scores = cross_val_score(xgb_model, X_train_scaled, y_train, cv=tscv, scoring='r2')

        # MAPE
        mape = np.mean(np.abs((y_test - y_pred_test) / (y_test + 1e-10))) * 100

        # 【6/7】模型评估与未来预测
        update_progress(85, "【6/7】模型评估与未来预测...")

        # 未来预测（未来6个月）
        last_time_str = pred_df_clean['time_str'].iloc[-1]
        last_year, last_month = map(int, last_time_str.split('-'))

        future_predictions = []
        future_time_labels = []

        for i in range(1, 7):
            future_month = last_month + i
            future_year = last_year
            while future_month > 12:
                future_month -= 12
                future_year += 1

            future_time_str = f'{future_year}-{future_month:02d}'
            future_time_labels.append(future_time_str)

            # 构建未来特征
            future_features = time_to_features(future_time_str)
            future_X = np.array([[
                future_features['year'],
                future_features['month'],
                future_features['quarter'],
                future_features['month_order'],
                future_features['is_quarter_end'],
                future_features['is_year_end'],
                future_features['is_peak_season'],
                future_features['month_sin'],
                future_features['month_cos'],
                y[-1],  # 使用最后的响应时间作为移动平均
                y[-1],
                0, 0, 0,
                y[-1],
                y[-2] if len(y) > 1 else y[-1]
            ]])

            future_X_scaled = scaler.transform(future_X)
            future_pred = xgb_model.predict(future_X_scaled)[0]
            future_predictions.append(round(float(future_pred), 2))

        # 【7/7】保存JSON格式结果
        update_progress(100, "【7/7】保存JSON格式结果...")

        # 构建返回结果
        result = {
            "metadata": {
                "data_source": "top_300_metrics.csv",
                "target_metric": "change_request_response_time",
                "total_projects": len(df),
                "valid_samples": len(pred_df_clean),
                "feature_columns": feature_cols,
                "best_model": "XGBoost"
            },
            "model_evaluation": {
                "XGBoost": {
                    "r2_train": round(r2_train, 4),
                    "r2_test": round(r2_test, 4),
                    "mae": round(mae, 2),
                    "rmse": round(rmse, 2),
                    "cv_mean": round(cv_scores.mean(), 4),
                    "cv_std": round(cv_scores.std(), 4),
                    "best_params": {
                        "n_estimators": 200,
                        "max_depth": 5,
                        "learning_rate": 0.05
                    },
                    "mape": round(mape, 2)
                }
            },
            "future_prediction": {
                "prediction_time_points": future_time_labels,
                "predicted_response_time": future_predictions,
                "prediction_explanation": "预测未来6个月的Change Request响应时间（基于最优XGBoost模型）"
            },
            "historical_data_sample": []
        }

        # 添加历史数据样本（最近20条）
        sample_data = pred_df_clean.tail(20)
        for _, row in sample_data.iterrows():
            result["historical_data_sample"].append({
                "time_str": row['time_str'],
                "response_time": round(float(row['response_time']), 2),
                "year": int(row['year']),
                "month": int(row['month'])
            })

        update_progress(100, "完成！")
        return result

    except Exception as e:
        raise Exception(f"预测失败: {str(e)}")


# ==================== 工具函数 ====================
def parse_time_series_dict(dict_str):
    """解析时序字典，返回(时间列表, 值列表)"""
    try:
        if pd.isna(dict_str) or dict_str == '':
            return [], []
        data_dict = eval(dict_str)
        # 按时间排序
        sorted_items = sorted(data_dict.items(), key=lambda x: x[0])
        times = [item[0] for item in sorted_items]
        values = [float(item[1]) for item in sorted_items]
        return times, values
    except:
        return [], []

def time_to_features(time_str):
    """时间字符串分解为特征：年、月、季度、月份序、是否年末/季度末等"""
    year, month = map(int, time_str.split('-'))
    quarter = (month - 1) // 3 + 1
    month_order = (year - 2015) * 12 + month  # 以2015年为基准的累计月份
    is_quarter_end = 1 if month in [3,6,9,12] else 0
    is_year_end = 1 if month == 12 else 0
    is_peak_season = 1 if month in [1,2,9,10,11,12] else 0  # 业务高峰期
    month_sin = np.sin(2 * np.pi * month / 12)  # 月份周期性特征
    month_cos = np.cos(2 * np.pi * month / 12)
    return {
        'year': year,
        'month': month,
        'quarter': quarter,
        'month_order': month_order,
        'is_quarter_end': is_quarter_end,
        'is_year_end': is_year_end,
        'is_peak_season': is_peak_season,
        'month_sin': month_sin,
        'month_cos': month_cos
    }

def add_temporal_features(df):
    """添加时序衍生特征：移动平均、差分、滞后特征"""
    # 按项目和时间排序
    df = df.sort_values(['project_id', 'month_order']).reset_index(drop=True)

    # 分组添加特征（按项目）
    for window in [3, 6]:
        # 移动平均
        df[f'response_time_ma_{window}'] = df.groupby('project_id')['response_time'].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )
        # 移动标准差
        df[f'response_time_std_{window}'] = df.groupby('project_id')['response_time'].transform(
            lambda x: x.rolling(window=window, min_periods=1).std().fillna(0)
        )

    # 一阶差分（变化趋势）
    df['response_time_diff_1'] = df.groupby('project_id')['response_time'].diff(1).fillna(0)
    # 滞后特征（前1期、前2期值）
    df['response_time_lag_1'] = df.groupby('project_id')['response_time'].shift(1).fillna(0)
    df['response_time_lag_2'] = df.groupby('project_id')['response_time'].shift(2).fillna(0)

    return df


# ==================== 脚本模式（用于直接运行测试） ====================
if __name__ == "__main__":
    print("测试响应时间预测函数...")

    def progress_callback(progress, message):
        print(f"[{progress}%] {message}")

    try:
        result = predict_response_time(progress_callback=progress_callback)
        print("\n✅ 预测成功！")
        print(f"📊 有效样本数: {result['metadata']['valid_samples']}")
        print(f"🎯 R² 测试集: {result['model_evaluation']['XGBoost']['r2_test']}")
        print(f"📈 RMSE: {result['model_evaluation']['XGBoost']['rmse']}")
        print(f"🔮 未来预测: {result['future_prediction']['prediction_time_points']}")
        print(f"   预测值: {result['future_prediction']['predicted_response_time']}")

        # 保存结果到 JSON
        import json
        json_path = r'C:\Users\22390\Desktop\OpenSODA\backendData\response_time_prediction_result.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"\n💾 结果已保存到: {json_path}")

    except Exception as e:
        print(f"\n❌ 预测失败: {e}")
        import traceback
        traceback.print_exc()
