<template>
  <div class="code-changes">
    <header class="page-header">
      <h1 class="page-title">{{ t(page.code.title) }}</h1>
      <p class="page-subtitle">{{ t(page.code.subtitle) }}</p>
    </header>

    <!-- 核心指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">🔀</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalPRs.toLocaleString() }}</div>
          <div class="metric-label">{{ t(page.code.stats.totalPRs) }}</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">✅</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalAcceptedPRs.toLocaleString() }}</div>
          <div class="metric-label">{{ t(page.code.stats.acceptedPRs) }}</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">➕</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalLinesAdded.toLocaleString() }}</div>
          <div class="metric-label">{{ t(page.code.stats.linesAdded) }}</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">➖</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalLinesRemoved.toLocaleString() }}</div>
          <div class="metric-label">{{ t(page.code.stats.linesRemoved) }}</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <div class="chart-box full-width">
        <h3 class="chart-title">{{ t(page.code.charts.codeChangeTop) }}</h3>
        <div ref="codeChangeRef" class="chart"></div>
      </div>

      <div class="chart-box">
        <h3 class="chart-title">{{ t(page.code.charts.prAcceptanceRate) }}</h3>
        <div ref="prAcceptanceRef" class="chart"></div>
      </div>

      <div class="chart-box">
        <h3 class="chart-title"> {{ t(page.code.charts.prReviewActivity) }}</h3>
        <div ref="prReviewsRef" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import * as echarts from "echarts"
import raw from "@/utils/converted_data.json"
import { parseNumber } from "@/utils/parse"
import { useTranslations } from "@/composables/useTranslations"
const { t, page } = useTranslations()

const projects = raw.map(p => ({
  ...p,
  change_requests: parseNumber(p.change_requests),
  change_requests_accepted: parseNumber(p.change_requests_accepted),
  change_requests_reviews: parseNumber(p.change_requests_reviews),
  code_change_lines_add: parseNumber(p.code_change_lines_add),
  code_change_lines_remove: parseNumber(p.code_change_lines_remove),
  code_change_lines_sum: parseNumber(p.code_change_lines_sum)
}))

// 计算核心指标
const totalPRs = computed(() => 
  projects.reduce((s, p) => s + p.change_requests, 0)
)
const totalAcceptedPRs = computed(() => 
  projects.reduce((s, p) => s + p.change_requests_accepted, 0)
)
const totalLinesAdded = computed(() => 
  projects.reduce((s, p) => s + p.code_change_lines_add, 0)
)
const totalLinesRemoved = computed(() => 
  projects.reduce((s, p) => s + p.code_change_lines_remove, 0)
)

const codeChangeRef = ref()
const prAcceptanceRef = ref()
const prReviewsRef = ref()

onMounted(() => {
  renderCodeChange()
  renderPRAcceptance()
  renderPRReviews()
})

function renderCodeChange() {
  const chart = echarts.init(codeChangeRef.value)
  const top = [...projects]
    .sort((a, b) => Math.abs(b.code_change_lines_sum) - Math.abs(a.code_change_lines_sum))
    .slice(0, 20)
  
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: {
      data: ['新增', '删除'],
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
        name: '新增',
        type: 'bar',
        stack: 'total',
        data: top.map(p => p.code_change_lines_add),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
            { offset: 0, color: '#43e97b' },
            { offset: 1, color: '#38f9d7' }
          ])
        }
      },
      {
        name: '删除',
        type: 'bar',
        stack: 'total',
        data: top.map(p => -p.code_change_lines_remove),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
            { offset: 0, color: '#fa709a' },
            { offset: 1, color: '#fee140' }
          ])
        }
      }
    ]
  })
}

function renderPRAcceptance() {
  const chart = echarts.init(prAcceptanceRef.value)

  // 计算PR接受率分布
  const ranges = [
    { name: '0-20%', min: 0, max: 0.2 },
    { name: '21-40%', min: 0.21, max: 0.4 },
    { name: '41-60%', min: 0.41, max: 0.6 },
    { name: '61-80%', min: 0.61, max: 0.8 },
    { name: '81-100%', min: 0.81, max: 1 }
  ]

  const data = ranges.map(range => {
    const count = projects.filter(p => {
      if (p.change_requests === 0) return false
      const rate = p.change_requests_accepted / p.change_requests
      return rate >= range.min && rate <= range.max
    }).length
    return { name: range.name, value: count }
  })

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

function renderPRReviews() {
  const chart = echarts.init(prReviewsRef.value)
  const top = [...projects]
    .sort((a, b) => b.change_requests_reviews - a.change_requests_reviews)
    .slice(0, 15)

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
      name: '评审数',
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [{
      type: 'bar',
      data: top.map(p => p.change_requests_reviews),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ])
      },
      barWidth: '60%'
    }]
  })
}
</script>

<style scoped>
.code-changes {
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

.code-changes::before {
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

