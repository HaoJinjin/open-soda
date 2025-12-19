<template>
  <div class="screen"  :style="{ height: pageHeight + 'px' }">
    <!-- 紧凑型 Header -->
    <header class="header">
      <div class="header-content">
        <div class="header-left">
          <span class="header-icon">🌐</span>
          <div class="header-text">
            <h1 class="main-title">{{ t(page.overview.title) }}</h1>
            <p class="subtitle">{{ t(page.overview.subtitle) }}</p>
          </div>
        </div>
        <div class="header-stats">
          <div class="mini-stat">
            <span class="mini-value">{{ projects.length }}</span>
            <span class="mini-label">{{ t(page.overview.stats.projects) }}</span>
          </div>
          <div class="mini-stat">
            <span class="mini-value">{{ avgStar.toFixed(0) }}</span>
            <span class="mini-label">{{ t(page.overview.stats.avgStars) }}</span>
          </div>
          <div class="mini-stat">
            <span class="mini-value">{{ avgActivity.toFixed(1) }}</span>
            <span class="mini-label">{{ t(page.overview.stats.activity) }}</span>
          </div>
          <div class="mini-stat">
            <span class="mini-value">{{ (totalParticipants / 1000).toFixed(1) }}K</span>
            <span class="mini-label">{{ t(page.overview.stats.contributors) }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域：左侧图表 + 右侧排行榜 -->
    <div class="main-content">
      <!-- 左侧图表区域 -->
      <div class="charts-section">
      <!-- 第一行：两个图表 -->
      <div class="chart-row">
        <div class="chart-container">
          <h3 class="chart-title">{{ t(page.overview.charts.activityTrend) }}</h3>
          <div ref="activityRef" class="chart"></div>
        </div>
        <div class="chart-container">
          <h3 class="chart-title">{{ t(page.overview.charts.starTop10) }}</h3>
          <div ref="starRef" class="chart"></div>
        </div>
      </div>

      <!-- 第二行：两个图表 -->
      <div class="chart-row">
        <div class="chart-container">
          <h3 class="chart-title">{{ t(page.overview.charts.emailEcosystem) }}</h3>
          <div ref="emailRef" class="chart"></div>
        </div>
        <div class="chart-container">
          <h3 class="chart-title">{{ t(page.overview.charts.forkTop10) }}</h3>
          <div ref="forkRef" class="chart"></div>
        </div>
      </div>

      <!-- 第三行：Issue趋势 -->
      <div class="chart-row single">
        <div class="chart-container">
          <h3 class="chart-title">{{ t(page.overview.charts.issueResponseTrend) }}</h3>
          <div ref="issueRef" class="chart"></div>
        </div>
      </div>
    </div>

    <!-- 右侧滚动排行榜 -->
    <div class="ranking-panel">
      <div class="ranking-header">
        <span class="ranking-icon">🏆</span>
        <span class="ranking-title">{{ t(page.overview.ranking.title) }}</span>
      </div>

      <!-- Star 排行榜 -->
      <div class="ranking-section">
        <div class="ranking-section-title">{{ t(page.overview.ranking.starRanking) }}</div>
        <div class="ranking-list">
          <div
            v-for="(project, index) in topStarProjects"
            :key="index"
            class="ranking-item"
            :class="{ 'top-three': index < 3 }"
          >
            <div class="rank-number" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
            <div class="rank-info">
              <div class="rank-name">{{ project.projectname2 || project.projectname }}</div>
              <div class="rank-value">⭐ {{ project.stars.toLocaleString() }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 活跃度排行榜 -->
      <div class="ranking-section">
        <div class="ranking-section-title">{{ t(page.overview.ranking.activityRanking) }}</div>
        <div class="ranking-list">
          <div
            v-for="(project, index) in topActivityProjects"
            :key="index"
            class="ranking-item"
            :class="{ 'top-three': index < 3 }"
          >
            <div class="rank-number" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
            <div class="rank-info">
              <div class="rank-name">{{ project.projectname2 || project.projectname }}</div>
              <div class="rank-value">📊 {{ project.activity.toFixed(2) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Fork 排行榜 -->
      <div class="ranking-section">
        <div class="ranking-section-title">{{ t(page.overview.ranking.forkRanking) }}</div>
        <div class="ranking-list">
          <div
            v-for="(project, index) in topForkProjects"
            :key="index"
            class="ranking-item"
            :class="{ 'top-three': index < 3 }"
          >
            <div class="rank-number" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
            <div class="rank-info">
              <div class="rank-name">{{ project.projectname2 || project.projectname }}</div>
              <div class="rank-value">🔱 {{ project.forks.toLocaleString() }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted ,onUnmounted} from "vue"
import * as echarts from "echarts"
import raw from "@/utils/converted_data.json"
import { parseMaybeJSON, parseNumber } from "@/utils/parse"
import { useTranslations } from "@/composables/useTranslations"

const { t, page } = useTranslations()

const projects = raw.map(p => ({
  ...p,
  stars: parseNumber(p.stars),
  activity: parseNumber(p.activity),
  participants: parseNumber(p.participants),
  forks: parseNumber(p.technical_fork),
  active: parseMaybeJSON(p.active_dates_and_times),
  emails: parseMaybeJSON(p.contributor_email_suffixes)
}))

/* ===== 核心指标 ===== */
const avgStar = projects.reduce((s, p) => s + p.stars, 0) / projects.length
const avgActivity = projects.reduce((s, p) => s + p.activity, 0) / projects.length
const totalParticipants = projects.reduce((s, p) => s + p.participants, 0)

/* ===== 排行榜数据 ===== */
const topStarProjects = [...projects].sort((a, b) => b.stars - a.stars).slice(0, 10)
const topActivityProjects = [...projects].sort((a, b) => b.activity - a.activity).slice(0, 10)
const topForkProjects = [...projects].sort((a, b) => b.forks - a.forks).slice(0, 10)

/* ===== refs ===== */
const activityRef = ref()
const starRef = ref()
const emailRef = ref()
const forkRef = ref()
const issueRef = ref()

onMounted(() => {
  renderActivity()
  renderStarRank()
  renderEmail()
  renderForkRank()
  renderIssueTrend()
})
function renderActivity() {
  const chart = echarts.init(activityRef.value)
  const days = projects[0].active

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#00f2fe',
      borderWidth: 1,
      textStyle: { color: '#fff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: "category",
      data: days.map((_, i) => `Day ${i + 1}`),
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: {
        color: '#a0d2eb',
        interval: Math.floor(days.length / 10)
      },
      splitLine: { show: false }
    },
    yAxis: {
      type: "value",
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [{
      type: "line",
      smooth: true,
      data: days,
      lineStyle: {
        color: '#00f2fe',
        width: 3,
        shadowColor: 'rgba(0, 242, 254, 0.5)',
        shadowBlur: 10
      },
      itemStyle: {
        color: '#00f2fe',
        borderColor: '#fff',
        borderWidth: 2
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "rgba(0, 242, 254, 0.5)" },
          { offset: 1, color: "rgba(0, 242, 254, 0.05)" }
        ])
      }
    }]
  })
}
function renderStarRank() {
  const chart = echarts.init(starRef.value)
  const top = [...projects].sort((a, b) => b.stars - a.stars).slice(0, 10)

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#00f2fe',
      borderWidth: 1,
      textStyle: { color: '#fff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    yAxis: {
      type: "category",
      data: top.map(i => i.projectname2 || i.projectname),
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb', fontSize: 12 },
      splitLine: { show: false }
    },
    xAxis: {
      type: "value",
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [{
      type: "bar",
      data: top.map(i => i.stars),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
          { offset: 0, color: "#4facfe" },
          { offset: 1, color: "#00f2fe" }
        ]),
        shadowColor: 'rgba(0, 242, 254, 0.5)',
        shadowBlur: 10
      },
      barWidth: '60%',
      label: {
        show: true,
        position: 'right',
        color: '#00f2fe',
        fontSize: 11
      }
    }]
  })
}
function renderEmail() {
  const chart = echarts.init(emailRef.value)
  const map: any = {}

  projects.forEach(p => {
    p.emails?.forEach(([k, v]: any) => {
      map[k] = (map[k] || 0) + Number(v)
    })
  })

  const data = Object.entries(map)
    .map(([k, v]) => ({ name: k, value: v }))
    .sort((a: any, b: any) => b.value - a.value)
    .slice(0, 10)

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#00f2fe',
      borderWidth: 1,
      textStyle: { color: '#fff' }
    },
    series: [{
      type: "pie",
      radius: ["40%", "70%"],
      center: ['50%', '50%'],
      data: data,
      label: {
        color: '#a0d2eb',
        fontSize: 12,
        formatter: '{b}\n{d}%'
      },
      labelLine: {
        lineStyle: { color: '#00f2fe' }
      },
      itemStyle: {
        borderColor: '#0f2027',
        borderWidth: 2,
        shadowColor: 'rgba(0, 242, 254, 0.3)',
        shadowBlur: 10
      }
    }]
  })
}
function renderForkRank() {
  const chart = echarts.init(forkRef.value)
  const top = [...projects].sort((a, b) => b.forks - a.forks).slice(0, 10)

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#00f2fe',
      borderWidth: 1,
      textStyle: { color: '#fff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: "category",
      data: top.map(i => i.projectname2 || i.projectname),
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: {
        color: '#a0d2eb',
        rotate: 30,
        fontSize: 11
      },
      splitLine: { show: false }
    },
    yAxis: {
      type: "value",
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [{
      type: "bar",
      data: top.map(i => i.forks),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
          { offset: 0, color: "#667eea" },
          { offset: 1, color: "#764ba2" }
        ]),
        shadowColor: 'rgba(102, 126, 234, 0.5)',
        shadowBlur: 10
      },
      barWidth: '60%',
      label: {
        show: true,
        position: 'top',
        color: '#00f2fe',
        fontSize: 11
      }
    }]
  })
}

function renderIssueTrend() {
  const chart = echarts.init(issueRef.value)
  const months = ["2022-08", "2022-09", "2022-10", "2022-11", "2022-12", "2023-01", "2023-02", "2023-03"]
  const data = [6, 15, 29, 23, 17, 14, 11, 4]

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#00f2fe',
      borderWidth: 1,
      textStyle: { color: '#fff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: "category",
      data: months,
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: {
        color: '#a0d2eb',
        rotate: 30
      },
      splitLine: { show: false }
    },
    yAxis: {
      type: "value",
      name: '天数',
      axisLine: { lineStyle: { color: '#00f2fe' } },
      axisLabel: { color: '#a0d2eb' },
      splitLine: { lineStyle: { color: 'rgba(0, 242, 254, 0.1)' } }
    },
    series: [{
      type: "line",
      data: data,
      smooth: true,
      lineStyle: {
        color: '#43e97b',
        width: 3,
        shadowColor: 'rgba(67, 233, 123, 0.5)',
        shadowBlur: 10
      },
      itemStyle: {
        color: '#43e97b',
        borderColor: '#fff',
        borderWidth: 2
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "rgba(67, 233, 123, 0.5)" },
          { offset: 1, color: "rgba(67, 233, 123, 0.05)" }
        ])
      }
    }]
  })
}
const pageHeight = ref(window.innerHeight)
// 更新页面高度
const updatePageHeight = () => {
  pageHeight.value = window.innerHeight
}

// 监听窗口大小变化
onMounted(() => {
  window.addEventListener('resize', updatePageHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', updatePageHeight)
})
</script>
<style scoped>
.screen {
  background: #000000;
  background-image:
    radial-gradient(circle at 10% 20%, rgba(0, 242, 254, 0.05) 0%, transparent 40%),
    radial-gradient(circle at 90% 80%, rgba(0, 242, 254, 0.05) 0%, transparent 40%),
    linear-gradient(180deg, #000000 0%, #0a0a0a 50%, #000000 100%);
  width: 100%;
  /* height: 97vh; */
  padding: 15px;
  color: #fff;
  overflow-y: auto;
  position: relative;
  display: flex;
  flex-direction: column;
  box-sizing: border-box  ;
}

.screen::before {
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

/* 紧凑型 Header */
.header {
  position: relative;
  z-index: 1;
  margin-bottom: 15px;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(0, 242, 254, 0.3);
  border-radius: 12px;
  padding: 12px 20px;
  backdrop-filter: blur(10px);
  box-shadow:
    0 0 20px rgba(0, 242, 254, 0.1),
    inset 0 1px 0 rgba(0, 242, 254, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-icon {
  font-size: 32px;
  filter: drop-shadow(0 0 10px rgba(0, 242, 254, 0.6));
  animation: rotate 8s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.main-title {
  font-size: 24px;
  font-weight: 700;
  color: #00f2fe;
  margin: 0;
  text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
  letter-spacing: 2px;
}

.subtitle {
  font-size: 12px;
  color: #a0d2eb;
  letter-spacing: 1px;
  margin: 0;
}

.header-stats {
  display: flex;
  gap: 25px;
}

.mini-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.mini-value {
  font-size: 20px;
  font-weight: 700;
  color: #00f2fe;
  text-shadow: 0 0 8px rgba(0, 242, 254, 0.5);
}

.mini-label {
  font-size: 11px;
  color: #a0d2eb;
  letter-spacing: 0.5px;
}

/* 主内容区域 */
.main-content {
  display: flex;
  gap: 15px;
  flex: 1;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

/* 左侧图表区域 */
.charts-section {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}

.charts-section::-webkit-scrollbar {
  width: 6px;
}

.charts-section::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.charts-section::-webkit-scrollbar-thumb {
  background: rgba(0, 242, 254, 0.3);
  border-radius: 3px;
}

.charts-section::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 242, 254, 0.5);
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 15px;
}

.chart-row.single {
  grid-template-columns: 1fr;
}

.chart-container {
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(0, 242, 254, 0.25);
  border-radius: 12px;
  padding: 15px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow:
    0 2px 10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(0, 242, 254, 0.05);
}

.chart-container:hover {
  border-color: rgba(0, 242, 254, 0.5);
  box-shadow:
    0 4px 20px rgba(0, 242, 254, 0.2),
    0 0 30px rgba(0, 242, 254, 0.1),
    inset 0 1px 0 rgba(0, 242, 254, 0.1);
  background: rgba(0, 0, 0, 0.85);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #00f2fe;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 242, 254, 0.2);
  text-shadow: 0 0 8px rgba(0, 242, 254, 0.3);
}

.chart {
  height: 280px;
  width: 100%;
}

/* 右侧排行榜面板 */
.ranking-panel {
  width: 320px;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(0, 242, 254, 0.3);
  border-radius: 12px;
  padding: 15px;
  overflow-y: auto;
  backdrop-filter: blur(10px);
  box-shadow:
    0 2px 15px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(0, 242, 254, 0.1);
}

.ranking-panel::-webkit-scrollbar {
  width: 6px;
}

.ranking-panel::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.ranking-panel::-webkit-scrollbar-thumb {
  background: rgba(0, 242, 254, 0.3);
  border-radius: 3px;
}

.ranking-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 242, 254, 0.5);
}

.ranking-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(0, 242, 254, 0.3);
}

.ranking-icon {
  font-size: 24px;
  filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.6));
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.ranking-title {
  font-size: 18px;
  font-weight: 700;
  color: #00f2fe;
  text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
  letter-spacing: 1px;
}

.ranking-section {
  margin-bottom: 20px;
}

.ranking-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #00f2fe;
  margin-bottom: 10px;
  padding: 8px 12px;
  background: rgba(0, 242, 254, 0.15);
  border-left: 3px solid #00f2fe;
  border-radius: 4px;
  box-shadow:
    0 0 10px rgba(0, 242, 254, 0.2),
    inset 0 1px 0 rgba(0, 242, 254, 0.1);
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(0, 242, 254, 0.2);
  border-radius: 8px;
  transition: all 0.3s ease;
  animation: slideIn 0.5s ease-out;
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(0, 242, 254, 0.05);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.ranking-item:hover {
  background: rgba(0, 242, 254, 0.15);
  border-color: rgba(0, 242, 254, 0.5);
  transform: translateX(-5px);
  box-shadow:
    0 4px 15px rgba(0, 242, 254, 0.3),
    0 0 20px rgba(0, 242, 254, 0.15),
    inset 0 1px 0 rgba(0, 242, 254, 0.1);
}

.ranking-item.top-three {
  border-color: rgba(255, 215, 0, 0.4);
  background: rgba(255, 215, 0, 0.08);
  box-shadow:
    0 2px 10px rgba(255, 215, 0, 0.2),
    inset 0 1px 0 rgba(255, 215, 0, 0.1);
}

.ranking-item.top-three:hover {
  border-color: rgba(255, 215, 0, 0.6);
  background: rgba(255, 215, 0, 0.15);
  box-shadow:
    0 4px 20px rgba(255, 215, 0, 0.4),
    0 0 25px rgba(255, 215, 0, 0.2),
    inset 0 1px 0 rgba(255, 215, 0, 0.2);
}

.rank-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  background: rgba(0, 242, 254, 0.2);
  color: #00f2fe;
  border-radius: 50%;
  flex-shrink: 0;
}

.rank-number.rank-1 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: #000;
  box-shadow: 0 0 15px rgba(255, 215, 0, 0.6);
  font-size: 16px;
}

.rank-number.rank-2 {
  background: linear-gradient(135deg, #C0C0C0, #A8A8A8);
  color: #000;
  box-shadow: 0 0 12px rgba(192, 192, 192, 0.6);
}

.rank-number.rank-3 {
  background: linear-gradient(135deg, #CD7F32, #B8860B);
  color: #fff;
  box-shadow: 0 0 12px rgba(205, 127, 50, 0.6);
}

.rank-info {
  flex: 1;
  min-width: 0;
}

.rank-name {
  font-size: 13px;
  color: #fff;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 3px;
}

.rank-value {
  font-size: 12px;
  color: #00f2fe;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .ranking-panel {
    width: 280px;
  }

  .chart {
    height: 240px;
  }
}

@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }

  .ranking-panel {
    width: 100%;
    max-height: 300px;
  }

  .header-stats {
    gap: 15px;
  }

  .mini-value {
    font-size: 18px;
  }
}

@media (max-width: 768px) {
  .screen {
    padding: 10px;
  }

  .header-content {
    flex-direction: column;
    gap: 15px;
  }

  .header-stats {
    width: 100%;
    justify-content: space-around;
  }

  .chart-row {
    grid-template-columns: 1fr;
  }

  .main-title {
    font-size: 20px;
  }

  .subtitle {
    font-size: 11px;
  }
}
</style>