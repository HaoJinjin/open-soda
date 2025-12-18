import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')


# ==================== 封装的统计函数 ====================
def get_indicator_statistics(csv_path: str = r'C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv') -> dict:
    """
    获取指标统计信息（不生成图片，只返回JSON数据）

    参数:
        csv_path: CSV文件路径（可选，有默认值）

    返回:
        包含指标统计信息的字典
        {
            "metadata": {...},              # 元数据信息
            "indicator_statistics": [...],  # 各指标统计数据
            "correlation_matrix": {...},    # 相关性矩阵（用于热力图）
            "top10_projects": [...]         # Top10项目数据（用于对比图）
        }
    """
    try:
        # 定义要分析的6个指标
        target_indicators = [
            'inactive_contributors',
            'issues_and_change_request_active',
            'issues_closed',
            'issues_new',
            'new_contributors',
            'participants'
        ]

        # 指标中文名称映射
        indicator_names = {
            'inactive_contributors': '非活跃贡献者',
            'issues_and_change_request_active': '活跃工单/PR',
            'issues_closed': '已关闭工单',
            'issues_new': '新增工单',
            'new_contributors': '新贡献者',
            'participants': '参与者总数'
        }

        # 1. 加载数据
        df = pd.read_csv(csv_path)

        # 2. 过滤有效数据（无缺失值）
        df_valid = df[target_indicators].dropna()

        # 3. 计算相关性矩阵
        corr_matrix = df_valid.corr()

        # 4. 获取Top10项目数据
        top10_projects = df_valid.iloc[:10].copy()
        top10_projects['project_name'] = df.iloc[top10_projects.index]['projectname2'].values

        # 5. 构建完整的JSON数据结构
        indicator_stats = {
            "metadata": {
                "data_source": "top_300_metrics.csv",
                "total_projects": len(df),
                "valid_projects": len(df_valid),
                "missing_data_ratio": f"{((len(df) - len(df_valid)) / len(df) * 100):.2f}%",
                "analysis_indicators": target_indicators
            },
            "indicator_statistics": [],
            "correlation_matrix": corr_matrix.round(4).to_dict(),  # 相关性矩阵（用于热力图）
            "top10_projects": []
        }

        # 6. 添加每个指标的统计信息
        for ind in target_indicators:
            stats = {
                "indicator_column": ind,
                "indicator_name": indicator_names[ind],
                "mean": round(df_valid[ind].mean(), 4),
                "median": round(df_valid[ind].median(), 4),
                "std": round(df_valid[ind].std(), 4),
                "min": round(df_valid[ind].min(), 4),
                "max": round(df_valid[ind].max(), 4),
                "quantile_25": round(df_valid[ind].quantile(0.25), 4),
                "quantile_75": round(df_valid[ind].quantile(0.75), 4),
                "quantile_95": round(df_valid[ind].quantile(0.95), 4)
            }
            indicator_stats["indicator_statistics"].append(stats)

        # 7. 添加Top10项目的详细数据
        for idx, row in top10_projects.iterrows():
            project_data = {
                "project_name": row['project_name'],
                "original_index": int(idx),
                "indicator_values": {}
            }
            for ind in target_indicators:
                project_data["indicator_values"][ind] = round(row[ind], 4)
                # 添加标准化值（便于对比）
                project_data["indicator_values"][f"{ind}_scaled"] = round(
                    (row[ind] - df_valid[ind].mean()) / df_valid[ind].std(), 4
                )
            indicator_stats["top10_projects"].append(project_data)

        # 8. 返回结果
        return indicator_stats

    except Exception as e:
        raise Exception(f"获取指标统计信息失败: {str(e)}")


# ==================== 命令行脚本模式 ====================
# 只有直接运行此文件时才会执行以下代码，被导入时不会执行
if __name__ == "__main__":
    print("=" * 60)
    print("📊 开始生成指标统计信息...")
    print("=" * 60)

    try:
        # 调用封装的函数
        result = get_indicator_statistics()

        # 保存JSON文件
        json_path = r'C:\Users\22390\Desktop\OpenSODA\backendData\indicators_stat.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print(f"\n✅ 成功！")
        print(f"  总项目数: {result['metadata']['total_projects']}")
        print(f"  有效项目数: {result['metadata']['valid_projects']}")
        print(f"  缺失数据比例: {result['metadata']['missing_data_ratio']}")
        print(f"  分析指标数: {len(result['metadata']['analysis_indicators'])}")
        print(f"  Top10项目数: {len(result['top10_projects'])}")
        print(f"\n💾 JSON文件已保存: {json_path}")
        print("\n" + "=" * 60)
        print("🎉 所有任务完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 失败: {str(e)}")
        import traceback
        traceback.print_exc()