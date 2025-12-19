<template>
  <div class="contributor-ecosystem">
    <header class="page-header">
      <h1 class="page-title">{{ t(page.contributor.title) }}</h1>
      <p class="page-subtitle">{{ t(page.contributor.subtitle) }}</p>
    </header>

    <!-- 核心指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">🚌</div>
        <div class="metric-content">
          <div class="metric-value">{{ avgBusFactor.toFixed(1) }}</div>
          <div class="metric-label">{{ t(page.contributor.stats.avgBusFactor) }}</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalParticipants.toLocaleString() }}</div>
          <div class="metric-label">{{ t(page.contributor.stats.totalParticipants) }}</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">🌟</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalNewContributors }}</div>
          <div class="metric-label">{{ t(page.contributor.stats.totalNewContributors) }}</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon">😴</div>
        <div class="metric-content">
          <div class="metric-value">{{ totalInactiveContributors }}</div>
          <div class="metric-label">{{ t(page.contributor.stats.inactiveContributors) }}</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <div class="chart-box full-width">
        <h3 class="chart-title">{{ t(page.contributor.charts.busFactorDistribution) }}</h3>
        <div ref="busFactorRef" class="chart"></div>
      </div>

      <div class="chart-box">
        <h3 class="chart-title"> {{ t(page.contributor.charts.emailEcosystem) }}</h3>
        <div ref="emailRef" class="chart"></div>
      </div>

      <div class="chart-box">
        <h3 class="chart-title"> {{ t(page.contributor.charts.participantsSizeDistribution) }}</h3>
        <div ref="participantsRef" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import * as echarts from "echarts"
import raw from "@/utils/converted_data.json"
import { parseMaybeJSON, parseNumber } from "@/utils/parse"
import { useTranslations } from "@/composables/useTranslations"
const { t, page } = useTranslations()

const projects = raw.map(p => ({
  ...p,
  bus_factor: parseNumber(p.bus_factor),
  participants: parseNumber(p.participants),
  new_contributors: parseNumber(p.new_contributors),
  inactive_contributors: parseNumber(p.inactive_contributors),
  contributor_email_suffixes: parseMaybeJSON(p.contributor_email_suffixes)
}))

// 计算核心指标
const avgBusFactor = computed(() => 
  projects.reduce((s, p) => s + p.bus_factor, 0) / projects.length
)
const totalParticipants = computed(() => 
  projects.reduce((s, p) => s + p.participants, 0)
)
const totalNewContributors = computed(() => 
  projects.reduce((s, p) => s + p.new_contributors, 0)
)
const totalInactiveContributors = computed(() => 
  projects.reduce((s, p) => s + p.inactive_contributors, 0)
)

const busFactorRef = ref()
const emailRef = ref()
const participantsRef = ref()

onMounted(() => {
  renderBusFactor()
  renderEmail()
  renderParticipants()
})

function renderBusFactor() {
  const chart = echarts.init(busFactorRef.value)
  const sorted = [...projects].sort((a, b) => b.bus_factor - a.bus_factor)
  
  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((_, i) => `项目${i + 1}`),
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb', interval: 20 }
    },
    yAxis: {
      type: 'value',
      name: '巴士因子',
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [{
      type: 'bar',
      data: sorted.map(p => p.bus_factor),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ])
      },
      barWidth: '80%'
    }]
  })
}

function renderEmail() {
  const chart = echarts.init(emailRef.value)
  const emailMap: any = {}
  
  projects.forEach(p => {
    if (Array.isArray(p.contributor_email_suffixes)) {
      p.contributor_email_suffixes.forEach(([domain, count]: any) => {
        emailMap[domain] = (emailMap[domain] || 0) + Number(count)
      })
    }
  })
  
  const data = Object.entries(emailMap)
    .map(([name, value]) => ({ name, value }))
    .sort((a: any, b: any) => b.value - a.value)
    .slice(0, 10)

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      data: data,
      label: {
        color: '#a0d2eb',
        fontSize: 12
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

function renderParticipants() {
  const chart = echarts.init(participantsRef.value)

  // 按参与者数量分组
  const ranges = [
    { name: '1-10', min: 1, max: 10 },
    { name: '11-50', min: 11, max: 50 },
    { name: '51-100', min: 51, max: 100 },
    { name: '101-200', min: 101, max: 200 },
    { name: '200+', min: 201, max: Infinity }
  ]

  const data = ranges.map(range => ({
    name: range.name,
    value: projects.filter(p => p.participants >= range.min && p.participants <= range.max).length
  }))

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c} 个项目 ({d}%)' },
    series: [{
      type: 'pie',
      radius: '70%',
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
.contributor-ecosystem {
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

.contributor-ecosystem::before {
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

