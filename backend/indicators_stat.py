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
            "projects_detail": [],  # ✅ 新增：所有项目的详细数据（顶层字段，避免重复）
            "indicator_statistics": [],
            "correlation_matrix": corr_matrix.round(4).to_dict(),  # 相关性矩阵（用于热力图）
            "top10_projects": []
        }

        # 6. 添加所有项目的详细数据（新增）
        for idx, row in df_valid.iterrows():
            project_detail = {
                "project_index": int(idx),
                "project_name": df.iloc[idx]['projectname2']
            }
            # 添加所有指标的值
            for ind in target_indicators:
                project_detail[ind] = round(row[ind], 4)
            indicator_stats["projects_detail"].append(project_detail)

        # 7. 添加每个指标的统计信息
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

        # 8. 添加Top10项目的详细数据（修复标准化值为负数的问题）
        for i, (idx, row) in enumerate(top10_projects.iterrows()):
            project_data = {
                "project_name": row['project_name'],
                "original_index": int(idx),
                "indicator_values": {}
            }
            for ind in target_indicators:
                project_data["indicator_values"][ind] = round(row[ind], 4)

                # ✅ 修复：使用 Min-Max 标准化（0-1 范围），而不是 Z-score 标准化
                # 参考原版文件第 119 行的逻辑
                values = top10_projects[ind].values
                values_min = values.min()
                values_max = values.max()
                # 避免除以零
                if values_max - values_min > 1e-8:
                    scaled_value = (row[ind] - values_min) / (values_max - values_min)
                else:
                    scaled_value = 0.0

                project_data["indicator_values"][f"{ind}_scaled"] = round(scaled_value, 4)

            indicator_stats["top10_projects"].append(project_data)

        # 8. 返回结果
        return indicator_stats

    except Exception as e:
        raise Exception(f"获取指标统计信息失败: {str(e)}")


# ==================== 命令行脚本模式 ====================
# 只有直接运行此文件时才会执行以下代码，被导入时不会执行
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import seaborn as sns

    # 配置中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.figsize'] = (15, 10)
    plt.rcParams['figure.dpi'] = 100

    print("=" * 60)
    print("📊 开始生成指标统计信息和可视化图表...")
    print("=" * 60)

    try:
        # 调用封装的函数
        result = get_indicator_statistics()

        # 重新加载数据用于绘图
        csv_path = r'C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv'
        df = pd.read_csv(csv_path)

        target_indicators = result['metadata']['analysis_indicators']
        indicator_names = {
            'inactive_contributors': '非活跃贡献者',
            'issues_and_change_request_active': '活跃工单/PR',
            'issues_closed': '已关闭工单',
            'issues_new': '新增工单',
            'new_contributors': '新贡献者',
            'participants': '参与者总数'
        }

        df_valid = df[target_indicators].dropna()

        # ==================== 1. 生成热力图（相关性分析） ====================
        print("\n📈 生成热力图...")
        plt.figure(figsize=(10, 8))
        corr_matrix = df_valid.corr()

        # 绘制热力图
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))  # 上三角掩码
        cmap = plt.cm.RdBu_r
        sns.heatmap(
            corr_matrix,
            mask=mask,
            annot=True,
            fmt='.2f',
            cmap=cmap,
            vmin=-1,
            vmax=1,
            square=True,
            linewidths=0.5,
            cbar_kws={'label': '相关系数'}
        )

        plt.title('6个核心指标相关性热力图', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        heatmap_path = r'C:\Users\22390\Desktop\OpenSODA\backendData\indicators_heatmap.png'
        plt.savefig(heatmap_path, dpi=100, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 热力图已保存: {heatmap_path}")

        # ==================== 2. 生成分布直方图 ====================
        print("\n📊 生成分布直方图...")
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle('6个核心指标分布对比', fontsize=16, fontweight='bold')

        for idx, (indicator, ax) in enumerate(zip(target_indicators, axes.flatten())):
            # 计算分箱（避免数据过于分散）
            max_val = df_valid[indicator].quantile(0.95)  # 取95分位数作为上限
            data = df_valid[indicator][df_valid[indicator] <= max_val]

            # 绘制直方图
            ax.hist(data, bins=30, color='#2ca02c', alpha=0.7, edgecolor='black')

            # 添加统计信息
            mean_val = df_valid[indicator].mean()
            median_val = df_valid[indicator].median()
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'均值: {mean_val:.2f}')
            ax.axvline(median_val, color='blue', linestyle='--', linewidth=2, label=f'中位数: {median_val:.2f}')

            # 设置标签
            ax.set_title(indicator_names[indicator], fontsize=12, fontweight='bold')
            ax.set_xlabel('数值', fontsize=10)
            ax.set_ylabel('频次', fontsize=10)
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        histogram_path = r'C:\Users\22390\Desktop\OpenSODA\backendData\indicators_histogram.png'
        plt.savefig(histogram_path, dpi=100, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 分布直方图已保存: {histogram_path}")

        # ==================== 3. 生成Top10对比图 ====================
        print("\n📊 生成Top10对比图...")
        top10_projects = df_valid.iloc[:10].copy()
        top10_projects['project_name'] = df.iloc[top10_projects.index]['projectname2'].values

        plt.figure(figsize=(15, 8))
        y_pos = np.arange(len(top10_projects))
        width = 0.15  # 每个柱子的宽度
        colors = plt.cm.Set2(np.linspace(0, 1, 6))

        # 绘制每个指标的柱子
        for i, (indicator, color) in enumerate(zip(target_indicators, colors)):
            values = top10_projects[indicator].values
            # 标准化到0-1区间（Min-Max标准化，与原版一致）
            values_scaled = (values - values.min()) / (values.max() - values.min() + 1e-8)
            plt.barh(y_pos + i*width - width*2.5, values_scaled, width,
                     label=indicator_names[indicator], color=color, alpha=0.8)

        # 设置标签
        plt.yticks(y_pos, top10_projects['project_name'], fontsize=10)
        plt.xlabel('标准化数值（0-1）', fontsize=12)
        plt.title('Top10项目 6个核心指标对比（标准化）', fontsize=14, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        top10_path = r'C:\Users\22390\Desktop\OpenSODA\backendData\indicators_top10_bar.png'
        plt.savefig(top10_path, dpi=100, bbox_inches='tight')
        plt.close()
        print(f"  ✅ Top10对比图已保存: {top10_path}")

        # ==================== 4. 保存JSON文件 ====================
        print("\n💾 保存JSON文件...")
        json_path = r'C:\Users\22390\Desktop\OpenSODA\backendData\indicators_stat.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"  ✅ JSON文件已保存: {json_path}")

        # ==================== 5. 输出统计信息 ====================
        print(f"\n" + "=" * 60)
        print(f"✅ 成功！")
        print(f"  总项目数: {result['metadata']['total_projects']}")
        print(f"  有效项目数: {result['metadata']['valid_projects']}")
        print(f"  缺失数据比例: {result['metadata']['missing_data_ratio']}")
        print(f"  分析指标数: {len(result['metadata']['analysis_indicators'])}")
        print(f"  详细数据条数: {len(result['projects_detail'])}")
        print(f"  Top10项目数: {len(result['top10_projects'])}")
        print("\n" + "=" * 60)
        print("🎉 所有任务完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 失败: {str(e)}")
        import traceback
        traceback.print_exc()