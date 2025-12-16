<template>
  <div class="community-attention">
    <header class="page-header">
      <h1 class="page-title">社区关注度</h1>
      <p class="page-subtitle">Community Attention - 项目受欢迎程度和社区参与度</p>
    </header>

    <!-- 核心指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">👁️</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalAttention.toLocaleString() }}</div>
          <div class="metric-label">总关注度</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">⭐</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalStars.toLocaleString() }}</div>
          <div class="metric-label">总星标数</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">🔱</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalForks.toLocaleString() }}</div>
          <div class="metric-label">总Fork数</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalParticipants.toLocaleString() }}</div>
          <div class="metric-label">总参与者</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <div class="chart-box full-width">
        <h3 class="chart-title">🔥 关注度排行 Top 20</h3>
        <div ref="attentionRankRef" class="chart"></div>
      </div>
      
      <div class="chart-box">
        <h3 class="chart-title">⭐ Star vs Fork 关系</h3>
        <div ref="starForkRef" class="chart"></div>
      </div>
      
      <div class="chart-box">
        <h3 class="chart-title">💬 社区互动热度</h3>
        <div ref="interactionRef" class="chart"></div>
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
  attention: parseNumber(p.attention),
  stars: parseNumber(p.stars),
  technical_fork: parseNumber(p.technical_fork),
  participants: parseNumber(p.participants),
  issue_comments: parseNumber(p.issue_comments),
  change_requests_reviews: parseNumber(p.change_requests_reviews)
}))

// 计算核心指标
const totalAttention = computed(() => 
  projects.reduce((s, p) => s + p.attention, 0)
)
const totalStars = computed(() => 
  projects.reduce((s, p) => s + p.stars, 0)
)
const totalForks = computed(() => 
  projects.reduce((s, p) => s + p.technical_fork, 0)
)
const totalParticipants = computed(() => 
  projects.reduce((s, p) => s + p.participants, 0)
)

const attentionRankRef = ref()
const starForkRef = ref()
const interactionRef = ref()

onMounted(() => {
  renderAttentionRank()
  renderStarFork()
  renderInteraction()
})

function renderAttentionRank() {
  const chart = echarts.init(attentionRankRef.value)
  const top = [...projects].sort((a, b) => b.attention - a.attention).slice(0, 20)
  
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
      name: '关注度',
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [{
      type: 'bar',
      data: top.map(p => p.attention),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
          { offset: 0, color: '#f093fb' },
          { offset: 1, color: '#f5576c' }
        ])
      },
      barWidth: '60%',
      label: {
        show: true,
        position: 'top',
        color: '#00f2fe',
        fontSize: 9
      }
    }]
  })
}

function renderStarFork() {
  const chart = echarts.init(starForkRef.value)
  const data = projects.filter(p => p.stars > 0 && p.technical_fork > 0)
  
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const p = data[params.dataIndex]
        return `${p.projectname2 || p.projectname}<br/>Stars: ${p.stars}<br/>Forks: ${p.technical_fork}`
      }
    },
    grid: { left: '10%', right: '10%', bottom: '10%', top: '10%', containLabel: true },
    xAxis: {
      type: 'value',
      name: 'Stars',
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    yAxis: {
      type: 'value',
      name: 'Forks',
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [{
      type: 'scatter',
      data: data.map(p => [p.stars, p.technical_fork]),
      symbolSize: 8,
      itemStyle: {
        color: '#00f2fe',
        opacity: 0.6
      }
    }]
  })
}

function renderInteraction() {
  const chart = echarts.init(interactionRef.value)
  const top = [...projects]
    .sort((a, b) => (b.issue_comments + b.change_requests_reviews) - (a.issue_comments + a.change_requests_reviews))
    .slice(0, 15)

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: {
      data: ['Issue评论', 'PR评审'],
      textStyle: { color: '#a0d2eb' },
      top: 10
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    yAxis: {
      type: 'category',
      data: top.map(p => p.projectname2 || p.projectname),
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb', fontSize: 11 }
    },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [
      {
        name: 'Issue评论',
        type: 'bar',
        stack: 'total',
        data: top.map(p => p.issue_comments),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
            { offset: 0, color: '#4facfe' },
            { offset: 1, color: '#00f2fe' }
          ])
        }
      },
      {
        name: 'PR评审',
        type: 'bar',
        stack: 'total',
        data: top.map(p => p.change_requests_reviews),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
            { offset: 0, color: '#43e97b' },
            { offset: 1, color: '#38f9d7' }
          ])
        }
      }
    ]
  })
}
</script>

<style scoped>
.community-attention {
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

.community-attention::before {
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