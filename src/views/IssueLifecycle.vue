<template>
  <div class="issue-lifecycle">
    <header class="page-header">
      <h1 class="page-title">Issue 生命周期</h1>
      <p class="page-subtitle">Issue Lifecycle - 维护质量和响应速度评估</p>
    </header>

    <!-- 核心指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">📝</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalNewIssues.toLocaleString() }}</div>
          <div class="metric-label">新增Issue总数</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">✅</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalClosedIssues.toLocaleString() }}</div>
          <div class="metric-label">已关闭Issue</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">🔄</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalActiveIssues.toLocaleString() }}</div>
          <div class="metric-label">活跃Issue/PR</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">💬</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalComments.toLocaleString() }}</div>
          <div class="metric-label">Issue评论总数</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <div class="chart-box full-width">
        <h3 class="chart-title">📊 Issue新增vs关闭对比</h3>
        <div ref="issueCompareRef" class="chart"></div>
      </div>
      
      <div class="chart-box">
        <h3 class="chart-title">⏱️ Issue响应时间趋势</h3>
        <div ref="responseTimeRef" class="chart"></div>
      </div>
      
      <div class="chart-box">
        <h3 class="chart-title">🔧 Issue解决时长趋势</h3>
        <div ref="resolutionTimeRef" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import * as echarts from "echarts"
import raw from "@/utils/converted_data.json"
import { parseMaybeJSON, parseNumber } from "@/utils/parse"

const projects = raw.map(p => ({
  ...p,
  issues_new: parseNumber(p.issues_new),
  issues_closed: parseNumber(p.issues_closed),
  issues_and_change_request_active: parseNumber(p.issues_and_change_request_active),
  issue_comments: parseNumber(p.issue_comments),
  issue_response_time: parseMaybeJSON(p.issue_response_time),
  issue_resolution_duration: parseMaybeJSON(p.issue_resolution_duration)
}))

// 计算核心指标
const totalNewIssues = computed(() => 
  projects.reduce((s, p) => s + p.issues_new, 0)
)
const totalClosedIssues = computed(() => 
  projects.reduce((s, p) => s + p.issues_closed, 0)
)
const totalActiveIssues = computed(() => 
  projects.reduce((s, p) => s + p.issues_and_change_request_active, 0)
)
const totalComments = computed(() => 
  projects.reduce((s, p) => s + p.issue_comments, 0)
)

const issueCompareRef = ref()
const responseTimeRef = ref()
const resolutionTimeRef = ref()

onMounted(() => {
  renderIssueCompare()
  renderResponseTime()
  renderResolutionTime()
})

function renderIssueCompare() {
  const chart = echarts.init(issueCompareRef.value)
  const top = [...projects]
    .sort((a, b) => (b.issues_new + b.issues_closed) - (a.issues_new + a.issues_closed))
    .slice(0, 20)
  
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: {
      data: ['新增Issue', '已关闭Issue'],
      textStyle: { color: '#a0d2eb' },
      top: 10
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: top.map(p => p.projectname2 || p.projectname),
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb', rotate: 45, interval: 0, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [
      {
        name: '新增Issue',
        type: 'bar',
        data: top.map(p => p.issues_new),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
            { offset: 0, color: '#4facfe' },
            { offset: 1, color: '#00f2fe' }
          ])
        }
      },
      {
        name: '已关闭Issue',
        type: 'bar',
        data: top.map(p => p.issues_closed),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
            { offset: 0, color: '#43e97b' },
            { offset: 1, color: '#38f9d7' }
          ])
        }
      }
    ]
  })
}

function renderResponseTime() {
  const chart = echarts.init(responseTimeRef.value)

  // 使用第一个项目的数据作为示例
  const sampleData = projects[0].issue_response_time
  if (sampleData && typeof sampleData === 'object') {
    const months = Object.keys(sampleData)
    const values = Object.values(sampleData).map(v => Number(v))

    chart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: months,
        axisLine: { lineStyle: { color: '#00f2fe' } },
        axisLabel: { color: '#a0d2eb', rotate: 30 }
      },
      yAxis: {
        type: 'value',
        name: '天数',
        axisLine: { lineStyle: { color: '#00f2fe' } },
        axisLabel: { color: '#a0d2eb' },
        splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
      },
      series: [{
        type: 'line',
        data: values,
        smooth: true,
        lineStyle: { color: '#4facfe', width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(79, 172, 254, 0.5)' },
            { offset: 1, color: 'rgba(79, 172, 254, 0.05)' }
          ])
        },
        itemStyle: { color: '#00f2fe' }
      }]
    })
  }
}

function renderResolutionTime() {
  const chart = echarts.init(resolutionTimeRef.value)

  // 使用第一个项目的数据作为示例
  const sampleData = projects[0].issue_resolution_duration
  if (sampleData && typeof sampleData === 'object') {
    const months = Object.keys(sampleData)
    const values = Object.values(sampleData).map(v => Number(v))

    chart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: months,
        axisLine: { lineStyle: { color: '#00f2fe' } },
        axisLabel: { color: '#a0d2eb', rotate: 30 }
      },
      yAxis: {
        type: 'value',
        name: '天数',
        axisLine: { lineStyle: { color: '#00f2fe' } },
        axisLabel: { color: '#a0d2eb' },
        splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
      },
      series: [{
        type: 'line',
        data: values,
        smooth: true,
        lineStyle: { color: '#43e97b', width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(67, 233, 123, 0.5)' },
            { offset: 1, color: 'rgba(67, 233, 123, 0.05)' }
          ])
        },
        itemStyle: { color: '#38f9d7' }
      }]
    })
  }
}
</script>

<style scoped>
.issue-lifecycle {
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

.issue-lifecycle::before {
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

