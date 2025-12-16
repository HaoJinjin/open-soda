<script setup>
import { ref, computed, onMounted } from 'vue'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js'
import { Line, Doughnut, Bar } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement)

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

// 解析JSON字符串数据
const parseJsonString = (jsonStr) => {
  try {
    return typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr
  } catch (e) {
    return jsonStr
  }
}

// 获取活动时间序列数据
const activityData = computed(() => {
  const data = parseJsonString(props.data.active_dates_and_times)
  return Array.isArray(data) ? data : []
})

// 获取问题年龄数据
const issueAgeData = computed(() => {
  const data = parseJsonString(props.data.issue_age)
  if (typeof data === 'object' && !Array.isArray(data)) {
    return {
      labels: Object.keys(data),
      values: Object.values(data).map(v => parseFloat(v))
    }
  }
  return { labels: [], values: [] }
})

// 获取贡献者排行数据
const contributorData = computed(() => {
  const data = parseJsonString(props.data.activity_details)
  if (Array.isArray(data)) {
    return {
      labels: data.slice(0, 10).map(item => item[0]),
      values: data.slice(0, 10).map(item => parseFloat(item[1]))
    }
  }
  return { labels: [], values: [] }
})

// 获取核心贡献者数据
const busFactor = computed(() => {
  const data = parseJsonString(props.data.bus_factor_detail)
  if (Array.isArray(data)) {
    return {
      labels: data.map(item => item[0]),
      values: data.map(item => item[1])
    }
  }
  return { labels: [], values: [] }
})

// 图表配置
const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      labels: { color: '#fff', font: { size: 12 } }
    }
  },
  scales: {
    y: {
      ticks: { color: '#888' },
      grid: { color: '#333' }
    },
    x: {
      ticks: { color: '#888' },
      grid: { color: '#333' }
    }
  }
}

const issueAgeChart = computed(() => ({
  labels: issueAgeData.value.labels,
  datasets: [{
    label: 'Issue Age (days)',
    data: issueAgeData.value.values,
    borderColor: '#10b981',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    tension: 0.4,
    fill: true,
    pointRadius: 4,
    pointBackgroundColor: '#10b981'
  }]
}))

const contributorChart = computed(() => ({
  labels: contributorData.value.labels,
  datasets: [{
    label: 'Activity Score',
    data: contributorData.value.values,
    backgroundColor: [
      '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
      '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#06b6d4'
    ],
    borderRadius: 8
  }]
}))

const busFactorChart = computed(() => ({
  labels: busFactor.value.labels,
  datasets: [{
    label: 'Commits',
    data: busFactor.value.values,
    backgroundColor: 'rgba(99, 102, 241, 0.8)',
    borderColor: '#6366f1',
    borderWidth: 2,
    borderRadius: 6
  }]
}))

// 关键指标卡片
const metrics = computed(() => [
  {
    label: 'Stars',
    value: parseInt(props.data.stars),
    icon: '⭐',
    color: 'from-yellow-500 to-orange-500'
  },
  {
    label: 'Activity',
    value: parseFloat(props.data.activity).toFixed(2),
    icon: '📊',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    label: 'Attention',
    value: parseInt(props.data.attention),
    icon: '👁️',
    color: 'from-purple-500 to-pink-500'
  },
  {
    label: 'Contributors',
    value: parseInt(props.data.participants),
    icon: '👥',
    color: 'from-green-500 to-emerald-500'
  },
  {
    label: 'Open Issues',
    value: parseInt(props.data.issues_and_change_request_active),
    icon: '🔔',
    color: 'from-red-500 to-pink-500'
  },
  {
    label: 'OpenRank',
    value: parseFloat(props.data.openrank).toFixed(2),
    icon: '🏆',
    color: 'from-indigo-500 to-blue-500'
  }
])

// 代码变更统计
const codeStats = computed(() => [
  {
    label: 'Lines Added',
    value: parseInt(props.data.code_change_lines_add),
    color: '#10b981'
  },
  {
    label: 'Lines Removed',
    value: parseInt(props.data.code_change_lines_remove),
    color: '#ef4444'
  }
])

// 样式计算
const getMetricColor = (color) => `bg-gradient-to-br ${color}`
</script>

<template>
  <div class="dashboard">
    <!-- 标题 -->
    <div class="title-section">
      <h1 class="main-title">{{ data.projectname }}</h1>
      <p class="sub-title">{{ data.projectname2 }}</p>
    </div>

    <!-- 关键指标卡片 -->
    <div class="metrics-grid">
      <div
        v-for="metric in metrics"
        :key="metric.label"
        :class="getMetricColor(metric.color)"
        class="metric-card"
      >
        <div class="metric-icon">{{ metric.icon }}</div>
        <div class="metric-content">
          <div class="metric-value">{{ metric.value }}</div>
          <div class="metric-label">{{ metric.label }}</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-container full-width">
        <h2 class="chart-title">📈 Issue Age Trend</h2>
        <div class="chart-wrapper">
          <Line
            v-if="issueAgeChart.labels.length"
            :data="issueAgeChart"
            :options="lineChartOptions"
          />
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-container">
          <h2 class="chart-title">👥 Top Contributors</h2>
          <div class="chart-wrapper">
            <Bar
              v-if="contributorChart.labels.length"
              :data="contributorChart"
              :options="lineChartOptions"
            />
          </div>
        </div>

        <div class="chart-container">
          <h2 class="chart-title">🔑 Core Maintainers</h2>
          <div class="chart-wrapper">
            <Bar
              v-if="busFactorChart.labels.length"
              :data="busFactorChart"
              :options="lineChartOptions"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-box">
          <div class="stat-icon">📝</div>
          <div class="stat-info">
            <div class="stat-label">Issues Created</div>
            <div class="stat-value">{{ parseInt(data.issues_new) }}</div>
          </div>
        </div>

        <div class="stat-box">
          <div class="stat-icon">✅</div>
          <div class="stat-info">
            <div class="stat-label">Issues Closed</div>
            <div class="stat-value">{{ parseInt(data.issues_closed) }}</div>
          </div>
        </div>

        <div class="stat-box">
          <div class="stat-icon">🔀</div>
          <div class="stat-info">
            <div class="stat-label">Pull Requests</div>
            <div class="stat-value">{{ parseInt(data.change_requests) }}</div>
          </div>
        </div>

        <div class="stat-box">
          <div class="stat-icon">🎯</div>
          <div class="stat-info">
            <div class="stat-label">PR Accepted</div>
            <div class="stat-value">{{ parseInt(data.change_requests_accepted) }}</div>
          </div>
        </div>

        <div class="stat-box">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-label">Code Added</div>
            <div class="stat-value">{{ parseInt(data.code_change_lines_add) }}</div>
          </div>
        </div>

        <div class="stat-box">
          <div class="stat-icon">🗑️</div>
          <div class="stat-info">
            <div class="stat-label">Code Removed</div>
            <div class="stat-value">{{ parseInt(data.code_change_lines_remove) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新贡献者 -->
    <div class="contributors-section">
      <h2 class="section-title">🌟 New Contributors</h2>
      <div class="contributors-list">
        <div
          v-for="(contributor, idx) in parseJsonString(data.new_contributors_detail)"
          :key="idx"
          class="contributor-tag"
        >
          {{ contributor }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  color: #fff;
  padding: 2rem;
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 标题 */
.title-section {
  text-align: center;
  margin-bottom: 2rem;
  animation: slideDown 0.6s ease-out;
}

.main-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6, #10b981, #f59e0b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.sub-title {
  font-size: 1.2rem;
  color: #94a3b8;
  font-weight: 300;
}

/* 指标网格 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  animation: fadeInUp 0.6s ease-out;
}

.metric-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.2);
}

.metric-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
}

.metric-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 0.25rem;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 2rem;
}

.chart-container {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  animation: fadeInUp 0.7s ease-out;
}

.chart-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #e0e7ff;
}

.chart-wrapper {
  position: relative;
  height: 300px;
  width: 100%;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.full-width {
  grid-column: 1 / -1;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-box {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  animation: fadeInUp 0.7s ease-out;
}

.stat-box:hover {
  background: rgba(30, 41, 59, 0.9);
  border-color: rgba(59, 130, 246, 0.5);
  transform: translateY(-4px);
}

.stat-icon {
  font-size: 2rem;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #3b82f6;
}

/* 新贡献者 */
.contributors-section {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  animation: fadeInUp 0.8s ease-out;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #e0e7ff;
}

.contributors-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.contributor-tag {
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.contributor-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }

  .main-title {
    font-size: 1.8rem;
  }

  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .chart-wrapper {
    height: 250px;
  }
}

/* 动画 */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 深色主题滚动条 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
}

::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.7);
}
</style>
