<template>
  <div class="impact-analysis">
    <header class="page-header">
      <h1 class="page-title">影响力分析</h1>
      <p class="page-subtitle">Impact Analysis - 项目在社区中的影响力评估</p>
    </header>

    <!-- 核心指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">⭐</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalStars.toLocaleString() }}</div>
          <div class="metric-label">总星标数</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">👁️</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalAttention.toLocaleString() }}</div>
          <div class="metric-label">总关注度</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">🏆</div>
        <div class="metric-content">
          <div class="metric-value">{{ avgOpenRank.toFixed(2) }}</div>
          <div class="metric-label">平均OpenRank</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">🔱</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalForks.toLocaleString() }}</div>
          <div class="metric-label">总Fork数</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <div class="chart-box full-width">
        <h3 class="chart-title">🌟 Star排行榜 Top 20</h3>
        <div ref="starRankRef" class="chart"></div>
      </div>
      
      <div class="chart-box">
        <h3 class="chart-title">🏆 OpenRank Top 15</h3>
        <div ref="openRankRef" class="chart"></div>
      </div>
      
      <div class="chart-box">
        <h3 class="chart-title">💬 评论活跃度分布</h3>
        <div ref="commentsRef" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import * as echarts from "echarts"
import raw from "@/utils/converted_data.json"
import { parseNumber } from "@/utils/parse"

const projects = raw.map(p => ({
  ...p,
  stars: parseNumber(p.stars),
  attention: parseNumber(p.attention),
  openrank: parseNumber(p.openrank),
  technical_fork: parseNumber(p.technical_fork),
  issue_comments: parseNumber(p.issue_comments)
}))

// 计算核心指标
const totalStars = computed(() => 
  projects.reduce((s, p) => s + p.stars, 0)
)
const totalAttention = computed(() => 
  projects.reduce((s, p) => s + p.attention, 0)
)
const avgOpenRank = computed(() => 
  projects.reduce((s, p) => s + p.openrank, 0) / projects.length
)
const totalForks = computed(() => 
  projects.reduce((s, p) => s + p.technical_fork, 0)
)

const starRankRef = ref()
const openRankRef = ref()
const commentsRef = ref()

onMounted(() => {
  renderStarRank()
  renderOpenRank()
  renderComments()
})

function renderStarRank() {
  const chart = echarts.init(starRankRef.value)
  const top = [...projects].sort((a, b) => b.stars - a.stars).slice(0, 20)
  
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: top.map(p => p.projectname2 || p.projectname),
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb', rotate: 45, interval: 0, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      name: 'Stars',
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [{
      type: 'bar',
      data: top.map(p => p.stars),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
          { offset: 0, color: '#4facfe' },
          { offset: 1, color: '#00f2fe' }
        ])
      },
      barWidth: '60%',
      label: {
        show: true,
        position: 'top',
        color: '#00f2fe',
        fontSize: 10
      }
    }]
  })
}

function renderOpenRank() {
  const chart = echarts.init(openRankRef.value)
  const top = [...projects].sort((a, b) => b.openrank - a.openrank).slice(0, 15)

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    yAxis: {
      type: 'category',
      data: top.map(p => p.projectname2 || p.projectname),
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb', fontSize: 11 }
    },
    xAxis: {
      type: 'value',
      name: 'OpenRank',
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [{
      type: 'bar',
      data: top.map(p => p.openrank),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
          { offset: 0, color: '#f093fb' },
          { offset: 1, color: '#f5576c' }
        ])
      },
      barWidth: '60%'
    }]
  })
}

function renderComments() {
  const chart = echarts.init(commentsRef.value)

  // 按评论数分组
  const ranges = [
    { name: '0-50', min: 0, max: 50 },
    { name: '51-100', min: 51, max: 100 },
    { name: '101-200', min: 101, max: 200 },
    { name: '201-500', min: 201, max: 500 },
    { name: '500+', min: 501, max: Infinity }
  ]

  const data = ranges.map(range => ({
    name: range.name,
    value: projects.filter(p => p.issue_comments >= range.min && p.issue_comments <= range.max).length
  }))

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c} 个项目 ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      data: data,
      label: {
        color: '#a0d2eb',
        fontSize: 12,
        formatter: '{b}\n{c} 项目'
      },
      labelLine: {
        lineStyle: { color: '#00f2fe' }
      },
      itemStyle: {
        borderColor: '#0f2027',
        borderWidth: 2
      }
    }]
  })
}
</script>

<style scoped>
.impact-analysis {
  width: 100%;
  /* height: 100%; */
  background: #000000;
  background-image:
    radial-gradient(circle at 10% 20%, rgba(0, 242, 254, 0.05) 0%, transparent 40%),
    radial-gradient(circle at 90% 80%, rgba(0, 242, 254, 0.05) 0%, transparent 40%),
    linear-gradient(180deg, #000000 0%, #0a0a0a 50%, #000000 100%);
  padding: 15px;
  color: #fff;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.impact-analysis::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0, 242, 254, 0.03) 2px,
      rgba(0, 242, 254, 0.03) 4px
    );
  pointer-events: none;
  z-index: 0;
  opacity: 0.3;
}

.page-header {
  text-align: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 242, 254, 0.3);
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #00f2fe;
  margin-bottom: 5px;
  text-shadow: 0 0 15px rgba(0, 242, 254, 0.6);
}

.page-subtitle {
  font-size: 12px;
  color: #a0d2eb;
  letter-spacing: 1px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.metric-card {
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(0, 242, 254, 0.3);
  border-radius: 10px;
  padding: 12px 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
  box-shadow:
    0 2px 10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(0, 242, 254, 0.1);
  backdrop-filter: blur(10px);
}

.metric-card:hover {
  transform: translateY(-3px);
  box-shadow:
    0 4px 20px rgba(0, 242, 254, 0.3),
    0 0 30px rgba(0, 242, 254, 0.15),
    inset 0 1px 0 rgba(0, 242, 254, 0.2);
  background: rgba(0, 242, 254, 0.15);
  border-color: rgba(0, 242, 254, 0.5);
}

.metric-icon {
  font-size: 32px;
  filter: drop-shadow(0 0 8px rgba(0, 242, 254, 0.5));
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 22px;
  font-weight: 700;
  color: #00f2fe;
  margin-bottom: 3px;
  text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
}

.metric-label {
  font-size: 11px;
  color: #a0d2eb;
  letter-spacing: 0.5px;
}

.charts-container {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-auto-rows: 1fr;
  gap: 12px;
  min-height: 0;
  position: relative;
  z-index: 1;
}

.chart-box {
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(0, 242, 254, 0.25);
  border-radius: 10px;
  padding: 12px;
  box-shadow:
    0 2px 10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(0, 242, 254, 0.05);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  min-height: 0;
  transition: all 0.3s ease;
}

.chart-box:hover {
  border-color: rgba(0, 242, 254, 0.5);
  box-shadow:
    0 4px 20px rgba(0, 242, 254, 0.2),
    0 0 30px rgba(0, 242, 254, 0.1),
    inset 0 1px 0 rgba(0, 242, 254, 0.1);
  background: rgba(0, 0, 0, 0.85);
}

.chart-box.full-width {
  grid-column: 1 / -1;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #00f2fe;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 242, 254, 0.2);
  text-shadow: 0 0 8px rgba(0, 242, 254, 0.3);
  flex-shrink: 0;
}

.chart {
  flex: 1;
  width: 100%;
  min-height: 0;
}
</style>

