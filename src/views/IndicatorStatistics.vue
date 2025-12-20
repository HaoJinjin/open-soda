<template>
  <div class="indicator-statistics" :style="{ height: pageHeight + 'px' }">
    <header class="page-header">
      <h1 class="page-title">📊 指标统计分析</h1>
      <p class="page-subtitle">Indicator Statistics - 6大核心指标深度分析</p>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载统计数据...</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <p class="error-text">{{ error }}</p>
      <button @click="loadStatistics" class="retry-btn">重试</button>
    </div>

    <!-- 主内容 -->
    <div v-else class="content">
      <!-- 元数据卡片 -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon">📁</div>
          <div class="metric-content">
            <div class="metric-value">{{ metadata.total_projects }}</div>
            <div class="metric-label">总项目数</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">✅</div>
          <div class="metric-content">
            <div class="metric-value">{{ metadata.valid_projects }}</div>
            <div class="metric-label">有效项目数</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">📉</div>
          <div class="metric-content">
            <div class="metric-value">{{ metadata.missing_data_ratio }}</div>
            <div class="metric-label">缺失率</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">🎯</div>
          <div class="metric-content">
            <div class="metric-value">{{ metadata.analysis_indicators?.length || 0 }}</div>
            <div class="metric-label">分析指标数</div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-container">
        <!-- 相关性热力图 -->
        <div class="chart-box full-width">
          <h3 class="chart-title">🔥 指标相关性热力图</h3>
          <div ref="heatmapRef" class="chart"></div>
        </div>

        <!-- 指标分布图 -->
        <div class="chart-box full-width">
          <h3 class="chart-title">📊 指标统计分布（基于 {{ projectsDetail.length }} 个项目的实际数据）</h3>
          <div ref="distributionRef" class="chart-distribution"></div>
        </div>

        <!-- Top10 项目对比图 -->
        <div class="chart-box full-width">
          <h3 class="chart-title">🏆 Top 10 项目指标对比</h3>
          <div ref="top10ComparisonRef" class="chart"></div>
        </div>

        <!-- 指标详细统计表格 -->
        <div class="chart-box full-width">
          <h3 class="chart-title">📋 指标详细统计</h3>
          <div class="table-container">
            <table class="stats-table">
              <thead>
                <tr>
                  <th>指标名称</th>
                  <th>平均值</th>
                  <th>中位数</th>
                  <th>标准差</th>
                  <th>最小值</th>
                  <th>最大值</th>
                  <th>25%分位</th>
                  <th>75%分位</th>
                  <th>95%分位</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="stat in indicatorStats" :key="stat.indicator_column">
                  <td class="indicator-name">{{ stat.indicator_name }}</td>
                  <td>{{ formatNumber(stat.mean) }}</td>
                  <td>{{ formatNumber(stat.median) }}</td>
                  <td>{{ formatNumber(stat.std) }}</td>
                  <td>{{ formatNumber(stat.min) }}</td>
                  <td>{{ formatNumber(stat.max) }}</td>
                  <td>{{ formatNumber(stat.quantile_25) }}</td>
                  <td>{{ formatNumber(stat.quantile_75) }}</td>
                  <td>{{ formatNumber(stat.quantile_95) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

// 响应式数据
const loading = ref(true)
const error = ref('')
const metadata = ref<any>({})
const indicatorStats = ref<any[]>([])
const correlationMatrix = ref<any>({})
const top10Projects = ref<any[]>([])
const projectsDetail = ref<any[]>([])  // ✅ 新增：所有项目的详细数据

// 图表引用
const heatmapRef = ref<HTMLElement>()
const distributionRef = ref<HTMLElement>()
const top10ComparisonRef = ref<HTMLElement>()

// 加载统计数据
const loadStatistics = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await axios.get('http://localhost:8000/api/statistics/indicators')

    if (response.data.success) {
      const data = response.data.data

      metadata.value = data.metadata
      indicatorStats.value = data.indicator_statistics
      correlationMatrix.value = data.correlation_matrix
      top10Projects.value = data.top10_projects
      projectsDetail.value = data.projects_detail || []  // ✅ 新增：获取详细数据

      // 先关闭 loading，让 DOM 渲染
      loading.value = false

      // 等待 DOM 更新完成后再渲染图表
      await nextTick()
      renderCharts()
    } else {
      error.value = '加载失败：服务器返回 success=false'
      loading.value = false
    }
  } catch (err: any) {
    if (err.response) {
      error.value = `服务器错误 (${err.response.status}): ${err.response.data?.message || err.message}`
    } else if (err.request) {
      error.value = '无法连接到后端服务，请确保后端已启动 (http://localhost:8000)'
    } else {
      error.value = err.message || '未知错误'
    }
    loading.value = false
  }
}

// 渲染所有图表
const renderCharts = () => {
  renderHeatmap()
  renderDistribution()
  renderTop10Comparison()
}

// 1. 相关性热力图（下三角形式，避免重复）
const renderHeatmap = () => {
  if (!heatmapRef.value) return

  if (!correlationMatrix.value || Object.keys(correlationMatrix.value).length === 0) {
    return
  }

  const chart = echarts.init(heatmapRef.value)
  const indicators = Object.keys(correlationMatrix.value)

  const indicatorNames: any = {
    'inactive_contributors': '非活跃贡献者',
    'issues_and_change_request_active': '活跃工单/PR',
    'issues_closed': '已关闭工单',
    'issues_new': '新增工单',
    'new_contributors': '新贡献者',
    'participants': '参与者总数'
  }

  // ✅ 只保留下三角数据（i >= j），避免重复
  const heatmapData: any[] = []
  indicators.forEach((row, i) => {
    indicators.forEach((col, j) => {
      if (i >= j) {  // ✅ 只保留下三角（包括对角线）
        const value = correlationMatrix.value[row]?.[col]
        if (value !== undefined && value !== null) {
          heatmapData.push([j, i, value.toFixed(3)])  // 注意：[j, i] 而不是 [i, j]
        }
      }
    })
  })

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        return `${indicatorNames[indicators[params.data[1]]]} <br/> ${indicatorNames[indicators[params.data[0]]]} <br/> 相关系数: ${params.data[2]}`
      }
    },
    grid: {
      left: '15%',
      right: '10%',
      top: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: indicators.map(ind => indicatorNames[ind]),
      axisLabel: {
        color: '#fff',
        rotate: 45,
        fontSize: 11
      },
      axisLine: { lineStyle: { color: '#333' } }
    },
    yAxis: {
      type: 'category',
      data: indicators.map(ind => indicatorNames[ind]),
      axisLabel: { color: '#fff', fontSize: 11 },
      axisLine: { lineStyle: { color: '#333' } }
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      },
      textStyle: { color: '#fff' }
    },
    series: [{
      type: 'heatmap',
      data: heatmapData,
      label: {
        show: true,
        color: '#fff',
        fontSize: 10
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}

// 2. 指标分布图（使用 projects_detail 绘制真实的分布直方图）
const renderDistribution = () => {
  if (!distributionRef.value) return
  if (!projectsDetail.value || projectsDetail.value.length === 0) return

  const chart = echarts.init(distributionRef.value)

  const indicatorNames: any = {
    'inactive_contributors': '非活跃贡献者',
    'issues_and_change_request_active': '活跃工单/PR',
    'issues_closed': '已关闭工单',
    'issues_new': '新增工单',
    'new_contributors': '新贡献者',
    'participants': '参与者总数'
  }

  const indicators = metadata.value.analysis_indicators || []

  // 为每个指标创建一个系列（直方图）
  const series = indicators.map((indicator: string) => {
    // 获取该指标的所有数据
    const values = projectsDetail.value
      .map(p => p[indicator])
      .filter(v => v !== null && v !== undefined && !isNaN(v))

    if (values.length === 0) return null

    // 计算 95 分位数作为上限（过滤极端值）
    const sortedValues = [...values].sort((a, b) => a - b)
    const p95Index = Math.floor(sortedValues.length * 0.95)
    const maxVal = sortedValues[p95Index]

    // 过滤数据
    const filteredValues = values.filter(v => v <= maxVal)

    // 计算直方图分箱（30 个箱）
    const binCount = 30
    const minVal = Math.min(...filteredValues)
    const binWidth = (maxVal - minVal) / binCount

    const bins = new Array(binCount).fill(0)
    filteredValues.forEach(v => {
      const binIndex = Math.min(Math.floor((v - minVal) / binWidth), binCount - 1)
      bins[binIndex]++
    })

    // 计算统计值
    const mean = values.reduce((a, b) => a + b, 0) / values.length
    const median = sortedValues[Math.floor(sortedValues.length / 2)]

    return {
      indicator,
      indicatorName: indicatorNames[indicator],
      bins,
      binWidth,
      minVal,
      mean,
      median
    }
  }).filter(s => s !== null)

  // 使用多个子图（grid）来显示每个指标的分布
  const cols = 3

  const grids: any[] = []
  const xAxes: any[] = []
  const yAxes: any[] = []
  const seriesData: any[] = []
  const titles: any[] = []

  series.forEach((s: any, idx: number) => {
    const row = Math.floor(idx / cols)
    const col = idx % cols

    // ✅ 优化布局：增加行间距，避免标题重叠
    const gridLeft = 5 + col * 32 + '%'
    const gridTop = 8 + row * 48 + '%'  // 增加行间距（从 45% 改为 48%）
    const gridWidth = '28%'
    const gridHeight = '32%'  // 减小高度（从 35% 改为 32%）

    grids.push({
      left: gridLeft,
      top: gridTop,
      width: gridWidth,
      height: gridHeight
    })

    // ✅ 标题单独配置，避免重叠
    titles.push({
      text: s.indicatorName,
      left: gridLeft,
      top: `calc(${gridTop} - 50px)`,  // 标题在 grid 上方 25px
      textStyle: {
        color: '#00d4ff',  // 使用主题色
        fontSize: 13,
        fontWeight: 'bold'
      }
    })

    xAxes.push({
      gridIndex: idx,
      type: 'category',
      data: s.bins.map((_: any) => ''),  // 不显示具体数值
      axisLabel: { show: false },
      axisLine: { lineStyle: { color: '#333' } },
      axisTick: { show: false }
    })

    yAxes.push({
      gridIndex: idx,
      type: 'value',
      axisLabel: {
        color: '#999',
        fontSize: 10,
        formatter: (value: number) => value.toFixed(0)  // 只显示整数
      },
      axisLine: { lineStyle: { color: '#333' } },
      splitLine: { lineStyle: { color: '#222', type: 'dashed' } }  // 虚线网格
    })

    // ✅ 优化配色：使用渐变色
    const colors = [
      '#00d4ff',  // 非活跃贡献者
      '#0066ff',  // 活跃工单/PR
      '#ff6b6b',  // 已关闭工单
      '#ffaa00',  // 新增工单
      '#00ff88',  // 新贡献者
      '#ff44ff'   // 参与者总数
    ]

    seriesData.push({
      name: s.indicatorName,
      type: 'bar',
      xAxisIndex: idx,
      yAxisIndex: idx,
      data: s.bins,
      itemStyle: {
        color: colors[idx % 6],
        borderRadius: [2, 2, 0, 0]  // 圆角顶部
      },
      barWidth: '100%',
      label: {
        show: false
      },
      markLine: {
        symbol: 'none',
        silent: true,  // 不响应鼠标事件
        data: [
          {
            name: '均值',
            xAxis: Math.floor((s.mean - s.minVal) / s.binWidth),
            lineStyle: { color: '#ff4444', type: 'dashed', width: 2 },
            label: {
              show: true,
              position: 'end',
              formatter: '均值',
              color: '#ff4444',
              fontSize: 10
            }
          },
          {
            name: '中位数',
            xAxis: Math.floor((s.median - s.minVal) / s.binWidth),
            lineStyle: { color: '#4444ff', type: 'dashed', width: 2 },
            label: {
              show: true,
              position: 'end',
              formatter: '中位数',
              color: '#4444ff',
              fontSize: 10
            }
          }
        ]
      }
    })
  })

  chart.setOption({
    backgroundColor: 'transparent',
    title: titles,  // ✅ 使用单独配置的标题数组
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#333',
      textStyle: { color: '#fff' },
      formatter: (params: any) => {
        if (!params || params.length === 0) return ''
        const param = params[0]
        return `${param.seriesName}<br/>频次: ${param.value}`
      }
    },
    grid: grids,
    xAxis: xAxes,
    yAxis: yAxes,
    series: seriesData
  })
}

// 3. Top10 项目对比图
const renderTop10Comparison = () => {
  if (!top10ComparisonRef.value) return

  const chart = echarts.init(top10ComparisonRef.value)
  const indicators = metadata.value.analysis_indicators || []
  const indicatorNames: any = {
    'inactive_contributors': '非活跃贡献者',
    'issues_and_change_request_active': '活跃工单/PR',
    'issues_closed': '已关闭工单',
    'issues_new': '新增工单',
    'new_contributors': '新贡献者',
    'participants': '参与者总数'
  }

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: indicators.map((ind: string) => indicatorNames[ind]),
      textStyle: { color: '#fff' },
      top: '3%',
      type: 'scroll'
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '15%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: top10Projects.value.map(p => p.project_name),
      axisLabel: {
        color: '#fff',
        rotate: 30,
        fontSize: 10
      },
      axisLine: { lineStyle: { color: '#333' } }
    },
    yAxis: {
      type: 'value',
      name: '标准化值',
      nameTextStyle: { color: '#fff' },
      axisLabel: { color: '#999' },
      axisLine: { lineStyle: { color: '#333' } },
      splitLine: { lineStyle: { color: '#222' } }
    },
    series: indicators.map((ind: string, idx: number) => ({
      name: indicatorNames[ind],
      type: 'bar',
      stack: 'total',
      data: top10Projects.value.map(p => {
        const val = p.indicator_values[`${ind}_scaled`]
        return val !== null && val !== undefined ? parseFloat(formatNumber(val)) : 0
      }),
      itemStyle: {
        color: ['#00d4ff', '#0066ff', '#ff6b6b', '#ffaa00', '#00ff88', '#ff44ff'][idx % 6]
      }
    }))
  })
}

// 格式化数字（处理字符串和数值）
const formatNumber = (value: any): string => {
  if (value === null || value === undefined) return '0.00'

  // 如果是字符串，尝试转换为数字
  if (typeof value === 'string') {
    const num = parseFloat(value)
    if (isNaN(num)) return value // 如果无法转换，返回原字符串
    return num.toFixed(2)
  }

  // 如果是数字，直接格式化
  if (typeof value === 'number') {
    return value.toFixed(2)
  }

  return String(value)
}

const pageHeight = ref(window.innerHeight)
// 更新页面高度
const updatePageHeight = () => {
  pageHeight.value = window.innerHeight
}


onMounted(() => {
  loadStatistics()
  window.addEventListener('resize', updatePageHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', updatePageHeight)
})
</script>

<style scoped>
.indicator-statistics {
  width: 100%;
      overflow-y: auto;
  box-sizing: border-box;
  padding: 20px;
  background: #000;
  min-height: 100vh;
  color: #fff;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-title {
  font-size: 32px;
  font-weight: bold;
  margin: 0 0 10px 0;
  background: linear-gradient(135deg, #00d4ff, #0066ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 加载和错误状态 */
.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #333;
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text, .error-text {
  margin-top: 20px;
  color: #999;
}

.error-icon {
  font-size: 48px;
}

.retry-btn {
  margin-top: 20px;
  padding: 10px 30px;
  background: linear-gradient(135deg, #00d4ff, #0066ff);
  border: none;
  border-radius: 5px;
  color: #fff;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  opacity: 0.8;
}

/* 指标卡片 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: linear-gradient(135deg, #1a1a1a, #0a0a0a);
  border: 1px solid #333;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.metric-icon {
  font-size: 32px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #00d4ff;
}

.metric-label {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

/* 图表容器 */
.charts-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.chart-box {
  background: linear-gradient(135deg, #1a1a1a, #0a0a0a);
  border: 1px solid #333;
  border-radius: 10px;
  padding: 20px;
}

.chart-box.full-width {
  grid-column: 1 / -1;
}

.chart-title {
  font-size: 16px;
  margin: 0 0 15px 0;
  color: #fff;
}

.chart {
  width: 100%;
  height: 450px;
}

.chart-distribution {
  width: 100%;
  height: 700px;  /* 更高，容纳 6 个子图（2 行 × 3 列） */
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
}

.stats-table th,
.stats-table td {
  padding: 12px;
  text-align: center;
  border-bottom: 1px solid #333;
}

.stats-table th {
  background: #1a1a1a;
  color: #00d4ff;
  font-weight: bold;
  font-size: 12px;
}

.stats-table td {
  color: #ccc;
  font-size: 12px;
}

.indicator-name {
  text-align: left;
  color: #fff;
  font-weight: 500;
}

@media (max-width: 1200px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>


