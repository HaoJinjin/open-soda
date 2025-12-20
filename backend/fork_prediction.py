import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
import warnings
warnings.filterwarnings("ignore")


def run_fork_prediction(csv_path: str, target_column: str = "technical_fork") -> dict:
    np.random.seed(42)

    # ==================== 1. 加载 CSV ====================
    df = pd.read_csv(csv_path, encoding="utf-8")

    # ==================== 2. 目标列处理 ====================
    def convert_to_numeric(col):
        numeric = pd.to_numeric(col, errors="coerce")
        if numeric.notna().mean() > 0.5:
            return numeric
        return pd.to_numeric(col, errors="coerce")

    df["target_numeric"] = convert_to_numeric(df[target_column])
    df_clean = df.dropna(subset=["target_numeric"]).reset_index(drop=True)

    # ==================== 3. 特征工程 ====================
    candidate_features = [
        "bus_factor", "change_requests", "change_requests_accepted",
        "change_requests_reviews", "code_change_lines_add",
        "code_change_lines_remove", "inactive_contributors",
        "issues_closed", "issues_new", "issue_comments",
        "new_contributors"
    ]

    feature_cols = []
    for col in candidate_features:
        if col in df_clean.columns:
            df_clean[f"feat_{col}"] = pd.to_numeric(df_clean[col], errors="coerce")
            corr = df_clean[f"feat_{col}"].corr(df_clean["target_numeric"])
            if abs(corr) < 0.95:
                df_clean[f"feat_{col}"].fillna(
                    df_clean[f"feat_{col}"].median(), inplace=True
                )
                feature_cols.append(f"feat_{col}")

    X = df_clean[feature_cols]
    y = df_clean["target_numeric"]

    # ==================== 4. 数据拆分 & 标准化 ====================
    X_train, X_test, y_train, y_test, train_idx, test_idx = train_test_split(
        X, y, df_clean.index, test_size=0.3, random_state=42
    )

    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    X_train_s = scaler_X.fit_transform(X_train)
    X_test_s = scaler_X.transform(X_test)
    y_train_s = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()

    # ==================== 5. 模型训练 ====================
    models = {
        "Ridge": Ridge(alpha=1.0),
        "Lasso": Lasso(alpha=0.1),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=50),
        "SVR": SVR(kernel="linear")
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train_s, y_train_s)

        y_pred_s = model.predict(X_test_s)
        y_pred = scaler_y.inverse_transform(
            y_pred_s.reshape(-1, 1)
        ).flatten()

        y_train_pred = scaler_y.inverse_transform(
            model.predict(X_train_s).reshape(-1, 1)
        ).flatten()

        results[name] = {
            "model": model,
            "r2_train": float(r2_score(y_train, y_train_pred)),
            "r2_test": float(r2_score(y_test, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "overfitting_gap": float(
                r2_score(y_train, y_train_pred) - r2_score(y_test, y_pred)
            ),
            "y_true": y_test.tolist(),
            "y_pred": y_pred.tolist()
        }

    # ==================== 6. 选择最佳模型 ====================
    best_name = max(
        results.keys(),
        key=lambda k: results[k]["r2_test"] -
        (0.3 if results[k]["overfitting_gap"] > 0.2 else 0)
    )

    best_model = results[best_name]["model"]

    # ==================== 7. 特征重要性 ====================
    feature_importance = []
    if hasattr(best_model, "coef_"):
        for f, v in zip(feature_cols, best_model.coef_):
            feature_importance.append({
                "feature_name": f,
                "importance": float(v),
                "abs_importance": abs(float(v))
            })
    elif hasattr(best_model, "feature_importances_"):
        for f, v in zip(feature_cols, best_model.feature_importances_):
            feature_importance.append({
                "feature_name": f,
                "importance": float(v),
                "abs_importance": float(v)
            })

    feature_importance.sort(
        key=lambda x: x["abs_importance"], reverse=True
    )

    # ==================== 8. 构建统一返回 JSON ====================
    return {
        "metadata": {
            "target_column": target_column,
            "best_model": best_name,
            "features_used": feature_cols,
            "total_samples": int(len(df)),
            "valid_samples": int(len(df_clean)),
            "timestamp": datetime.now().isoformat()
        },
        "model_comparison": {
            name: {
                "r2_train": r["r2_train"],
                "r2_test": r["r2_test"],
                "rmse": r["rmse"],
                "mae": r["mae"],
                "overfitting_gap": r["overfitting_gap"],
                "selected": name == best_name
            }
            for name, r in results.items()
        },
        "feature_importance": {
            "model": best_name,
            "feature_importance": feature_importance
        },
        "predictions": [
            {
                "true_value": float(t),
                "predicted_value": float(p),
                "absolute_error": round(abs(t - p), 4)
            }
            for t, p in zip(
                results[best_name]["y_true"],
                results[best_name]["y_pred"]
            )
        ]
    }
