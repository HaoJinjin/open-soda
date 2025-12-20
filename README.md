# OpenSODA 数据展示平台

OpenSODA 是一个开源数据分析和可视化平台，专注于展示和分析全球热门开源项目的关键指标。该平台通过多维度的数据分析，帮助用户深入了解开源项目的健康状况、发展趋势和社区活跃度。

## 项目概述

本项目基于 300 个热门开源项目的详细数据构建，涵盖了从项目活跃度、影响力、贡献者生态到 Issue 生命周期等多个维度的指标。通过直观的可视化界面，用户可以轻松探索和比较不同项目的各项关键指标。

## 快速开始
1. 克隆项目代码：`git clone https://github.com/HaoJinjin/open-soda.git`
2. 进入项目目录：`cd OpenSODA`
3. 安装依赖：`npm install`
4. 启动后端服务：`python backend/main.py`
5. 启动前端服务：`npm run dev`
6. 访问 http://localhost:5173查看项目

## 核心功能模块

### 1. 全局总览 (Overview)
- 项目整体数据概览
- 年度活跃度趋势分析
- Star/Fork 排行榜
- 实时项目排名展示

### 2. 活跃度分析 (Activity Analysis)
- 项目活跃度趋势分布
- 高活跃项目 Top 10 排名
- 新贡献者分布情况

### 3. 影响力分析 (Impact Analysis)
- 项目 Star 数量和关注度分析
- OpenRank 排名 Top 15
- 社区评论活跃度分布

### 4. 贡献者生态 (Contributor Ecosystem)
- 巴士因子(Bus Factor)分布
- 贡献者邮箱生态系统分析
- 参与者规模分布

### 5. Issue 生命周期 (Issue Lifecycle)
- Issue 新增与关闭对比
- Issue 响应时间和解决时长趋势
- 维护质量和响应速度评估

### 6. PR & 代码变更 (PR & Code Changes)
- 代码变更量 Top 20
- PR 接受率分布
- PR 评审活跃度

### 7. 社区关注度 (Community Attention)
- 项目关注度排行 Top 20
- Star 与 Fork 关系分析
- 社区互动热度图

### 8. 预测分析模块
#### Fork 预测 (Fork Prediction)
- 基于多种机器学习模型的 Fork 数量预测
- 模型性能对比分析
- 特征重要性排名
- 预测误差分布可视化

#### 响应时间预测 (Response Time Prediction)
- 未来 Issue 响应时间预测
- 历史趋势与未来预测对比
- 模型交叉验证结果展示

#### 指标统计分析 (Indicator Statistics)
- 6 大核心指标深度分析
- 指标相关性热力图
- 指标统计分布可视化

## 技术特点

- **多语言支持**: 完整的中英文界面切换
- **响应式设计**: 适配不同屏幕尺寸
- **数据驱动**: 基于真实开源项目数据
- **可视化丰富**: 使用 ECharts 实现多样化图表展示
- **预测建模**: 集成多种机器学习算法进行趋势预测

## 数据结构

项目基于包含 300 个热门开源项目的详细数据集，每个项目包含超过 30 项指标：

```json
{
  "projectname": "项目名称",
  "activity": "活跃度",
  "attention": "关注度",
  "bus_factor": "巴士因子",
  "change_requests": "变更请求数",
  "code_change_lines_add": "新增代码行数",
  "code_change_lines_remove": "删除代码行数",
  "inactive_contributors": "非活跃贡献者数",
  "issues_closed": "已关闭 Issue 数",
  "issues_new": "新增 Issue 数",
  "issue_comments": "Issue 评论数",
  "new_contributors": "新贡献者数",
  "participants": "参与者数",
  "stars": "Star 数",
  "technical_fork": "Fork 数",
  "...": "以及其他多项指标"
}