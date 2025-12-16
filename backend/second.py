import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import warnings
warnings.filterwarnings('ignore')

# 配置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['figure.dpi'] = 100

# ==================== 1. 加载数据 ====================
# 定义要分析的6个指标
target_indicators = [
    'inactive_contributors',
    'issues_and_change_request_active',
    'issues_closed',
    'issues_new',
    'new_contributors',
    'participants'
]

# 加载数据
df = pd.read_csv(r'C:\Users\22390\Desktop\OpenSODA\backendData\top_300_metrics.csv')

# 过滤有效数据（无缺失值）
df_valid = df[target_indicators].dropna()
print(f"✓ 有效数据量：{len(df_valid)} 条（原始 {len(df)} 条）")

# 数据标准化（用于热力图和柱状图对比）
df_scaled = (df_valid - df_valid.mean()) / df_valid.std()

# ==================== 2. 绘制热力图（相关性分析） ====================
plt.figure(figsize=(10, 8))
# 计算相关系数
corr_matrix = df_valid.corr()

# 绘制热力图
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))  # 上三角掩码
cmap = plt.cm.RdBu_r
heatmap = sns.heatmap(
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
plt.savefig(r'C:\Users\22390\Desktop\OpenSODA\backendData', dpi=100, bbox_inches='tight')
plt.close()
print("✓ 热力图已保存：indicators_heatmap.png")

# ==================== 3. 绘制柱状图（多维度对比） ====================
# 方案1：每个指标的分布柱状图（子图形式）
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('6个核心指标分布对比', fontsize=16, fontweight='bold')

# 调整指标名称显示
indicator_names = {
    'inactive_contributors': '非活跃贡献者',
    'issues_and_change_request_active': '活跃工单/PR',
    'issues_closed': '已关闭工单',
    'issues_new': '新增工单',
    'new_contributors': '新贡献者',
    'participants': '参与者总数'
}

# 绘制每个指标的柱状图
for idx, (indicator, ax) in enumerate(zip(target_indicators, axes.flatten())):
    # 计算分箱（避免数据过于分散）
    max_val = df_valid[indicator].quantile(0.95)  # 取95分位数作为上限（过滤极端值）
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
plt.savefig(r'C:\Users\22390\Desktop\OpenSODA\backendData', dpi=100, bbox_inches='tight')
plt.close()

# 方案2：项目维度的Top10对比柱状图（横向堆叠）
# 取前10个项目的标准化数据
top10_projects = df_valid.iloc[:10].copy()
top10_projects['project_name'] = df.iloc[top10_projects.index]['projectname2'].values

# 绘制横向堆叠柱状图
plt.figure(figsize=(15, 8))
y_pos = np.arange(len(top10_projects))
width = 0.15  # 每个柱子的宽度
colors = plt.cm.Set2(np.linspace(0, 1, 6))

# 绘制每个指标的柱子
for i, (indicator, color) in enumerate(zip(target_indicators, colors)):
    values = top10_projects[indicator].values
    # 标准化到0-1区间（方便对比）
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
plt.savefig(r'C:\Users\22390\Desktop\OpenSODA\backendData', dpi=100, bbox_inches='tight')
plt.close()

# ==================== 4. 生成JSON格式统计信息（核心修改） ====================
# 构建完整的JSON数据结构
indicator_stats = {
    "metadata": {
        "data_source": "top_300_metrics.csv",
        "total_projects": len(df),
        "valid_projects": len(df_valid),
        "missing_data_ratio": f"{((len(df) - len(df_valid)) / len(df) * 100):.2f}%",
        "analysis_indicators": target_indicators
    },
    "indicator_statistics": [],
    "correlation_matrix": corr_matrix.round(4).to_dict(),  # 相关性矩阵
    "top10_projects": []
}

# 添加每个指标的统计信息
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
        "quantile_95": round(df_valid[ind].quantile(0.95), 4)  # 新增95分位数
    }
    indicator_stats["indicator_statistics"].append(stats)

# 添加Top10项目的详细数据
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

# 保存JSON文件
json_path = r'C:\Users\22390\Desktop\OpenSODA\backendData\indicators_stat.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(indicator_stats, f, ensure_ascii=False, indent=4)

print("✓ 指标分布直方图已保存：indicators_histogram.png")
print("✓ Top10项目对比图已保存：indicators_top10_bar.png")
print(f"✓ 指标统计信息已保存为JSON：{json_path}")
print("\n🎉 所有可视化任务完成！")