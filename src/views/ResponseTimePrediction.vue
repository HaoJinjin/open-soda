<template>
  <div class="response-time-prediction" :style="{ height: pageHeight + 'px' }">
    <header class="page-header">
      <h1 class="page-title">⏱️ {{ $t('menu.responseTimePrediction') }}</h1>
      <p class="page-subtitle">{{ $t('pages.responseTimePrediction.subtitle') }}</p>
    </header>

    <!-- 任务控制区 -->
    <div class="control-panel">
      <button
        @click="startPrediction"
        :disabled="taskStatus === 'running'"
        class="start-btn"
      >
        {{ taskStatus === 'running' ? $t('common.predicting') : $t('common.startPrediction') }}
      </button>

      <div v-if="taskStatus === 'running'" class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="progress-info">
          <span class="progress-percent">{{ progress }}%</span>
          <span class="progress-message">{{ statusMessage }}</span>
        </div>
      </div>

      <div v-if="taskStatus === 'error'" class="error-message">
        ❌ {{ errorMessage }}
      </div>

      <div v-if="taskStatus === 'completed'" class="success-message">
        ✅ {{ $t('common.predictionCompleted') }}！
      </div>
    </div>

    <!-- 结果展示区 -->
    <div v-if="taskStatus === 'completed' && result" class="content">
      <!-- 模型评估指标 -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon">🎯</div>
          <div class="metric-content">
            <div class="metric-value">{{ result.model_evaluation.XGBoost.r2_train }}</div>
            <div class="metric-label">R² {{ $t('pages.responseTimePrediction.trainSet') }}</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">📊</div>
          <div class="metric-content">
            <div class="metric-value">{{ result.model_evaluation.XGBoost.rmse }}</div>
            <div class="metric-label">RMSE</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">📈</div>
          <div class="metric-content">
            <div class="metric-value">{{ result.model_evaluation.XGBoost.mae }}</div>
            <div class="metric-label">MAE</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">🔢</div>
          <div class="metric-content">
            <div class="metric-value">{{ result.metadata.valid_samples }}</div>
            <div class="metric-label">{{ $t('pages.responseTimePrediction.validSamples') }}</div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-container">
        <!-- 历史趋势 + 未来预测 -->
        <div class="chart-box full-width">
          <h3 class="chart-title">📈 {{ $t('pages.responseTimePrediction.historyAndFuture') }}</h3>
          <div ref="trendPredictionRef" class="chart"></div>
        </div>

        <!-- 模型性能对比 -->
        <div class="chart-box">
          <h3 class="chart-title">🏆 {{ $t('pages.responseTimePrediction.modelPerformance') }}</h3>
          <div ref="modelComparisonRef" class="chart"></div>
        </div>

        <!-- 交叉验证结果 -->
        <div class="chart-box">
          <h3 class="chart-title">📊 {{ $t('pages.responseTimePrediction.crossValidation') }}</h3>
          <div ref="cvResultsRef" class="chart"></div>
        </div>

        <!-- 未来预测详情表格 -->
        <div class="chart-box full-width">
          <h3 class="chart-title">🔮 {{ $t('pages.responseTimePrediction.futurePredictionDetails') }}</h3>
          <div class="table-container">
            <table class="prediction-table">
              <thead>
                <tr>
                  <th>{{ $t('pages.responseTimePrediction.timePoint') }}</th>
                  <th>{{ $t('pages.responseTimePrediction.predictedResponseTime') }}</th>
                  <th>{{ $t('pages.responseTimePrediction.trend') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(time, index) in result.future_prediction.prediction_time_points" :key="index">
                  <td>{{ time }}</td>
                  <td class="predicted-value">{{ result.future_prediction.predicted_response_time[index] }}</td>
                  <td>
                    <span v-if="index > 0" :class="getTrendClass(index)">
                      {{ getTrendIcon(index) }}
                      {{ getTrendText(index) }}
                    </span>
                    <span v-else>-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 模型参数 -->
        <div class="chart-box full-width">
          <h3 class="chart-title">⚙️ {{ $t('pages.responseTimePrediction.optimalParameters') }}</h3>
          <div class="params-grid">
            <div 
              v-for="(value, key) in result.model_evaluation.XGBoost.best_params" 
              :key="key"
              class="param-item"
            >
              <span class="param-key">{{ key }}</span>
              <span class="param-value">{{ value }}</span>
            </div>
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
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 响应式数据
const taskStatus = ref('idle') // idle, running, completed, error
const progress = ref(0)
const statusMessage = ref('')
const errorMessage = ref('')
const result = ref<any>(null)

// 图表引用
const trendPredictionRef = ref<HTMLElement>()
const modelComparisonRef = ref<HTMLElement>()
const cvResultsRef = ref<HTMLElement>()

// 轮询定时器
let pollTimer: any = null

// 开始预测
const startPrediction = async () => {
  try {
    const response = await axios.post('http://localhost:8000/api/predict/response-time/start', {}, {
      timeout: 5000 // 5秒超时
    })

    if (response.data.success) {
      taskStatus.value = 'running'
      progress.value = 0
      statusMessage.value = t('common.taskStarted')

      // 开始轮询
      startPolling()
    } else {
      errorMessage.value = response.data.message || t('common.startFailed')
      taskStatus.value = 'error'
    }
  } catch (err: any) {
    // 后端不可用，读取本地默认数据
    console.warn(t('common.requestError'))
  }
}

// 开始轮询任务状态
const startPolling = () => {
  pollTimer = setInterval(async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/predict/response-time/status')

      if (response.data.success) {
        const data = response.data.data

        taskStatus.value = data.status
        progress.value = data.progress
        statusMessage.value = data.message

        if (data.status === 'completed') {
          stopPolling()
          await loadResult()
        } else if (data.status === 'error') {
          stopPolling()
          errorMessage.value = data.error || t('common.predictionFailed')
        }
      }
    } catch (err: any) {
      console.error(t('common.pollingError') + ':', err)
    }
  }, 2000) // 每2秒轮询一次
}

// 停止轮询
const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}


// 加载预测结果
const loadResult = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/predict/response-time/result', {
      timeout: 5000
    })

    if (response.data.success) {
      result.value = response.data.data

      await nextTick()
      renderCharts()
    }
  } catch (err: any) {
    // 后端不可用，尝试加载本地默认数据
    console.warn(t('common.loadResultFailed'))
  }
}

// 渲染所有图表
const renderCharts = () => {
  renderTrendPrediction()
  renderModelComparison()
  renderCVResults()
}

// 1. 历史趋势 + 未来预测图
const renderTrendPrediction = () => {
  if (!trendPredictionRef.value || !result.value) return

  const chart = echarts.init(trendPredictionRef.value)

  // 历史数据
  const historicalData = result.value.historical_data_sample.map((item: any) => [
    item.time_str,
    item.response_time
  ])

  // 未来预测数据
  const futureData = result.value.future_prediction.prediction_time_points.map((time: string, index: number) => [
    time,
    result.value.future_prediction.predicted_response_time[index]
  ])

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: [t('pages.responseTimePrediction.historicalData'), t('pages.responseTimePrediction.futurePrediction')],
      textStyle: { color: '#fff' },
      top: '5%'
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '15%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      axisLabel: {
        color: '#fff',
        rotate: 30,
        fontSize: 10
      },
      axisLine: { lineStyle: { color: '#333' } }
    },
    yAxis: {
      type: 'value',
      name: t('pages.responseTimePrediction.responseTime'),
      nameTextStyle: { color: '#fff' },
      axisLabel: { color: '#999' },
      axisLine: { lineStyle: { color: '#333' } },
      splitLine: { lineStyle: { color: '#222' } }
    },
    series: [
      {
        name: t('pages.responseTimePrediction.historicalData'),
        type: 'line',
        data: historicalData,
        smooth: true,
        itemStyle: { color: '#00d4ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0)' }
          ])
        }
      },
      {
        name: t('pages.responseTimePrediction.futurePrediction'),
        type: 'line',
        data: futureData,
        smooth: true,
        lineStyle: { type: 'dashed', width: 2 },
        itemStyle: { color: '#ff6b6b' },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  })
}

// 2. 模型性能对比（仅显示XGBoost，因为只有这个模型）
const renderModelComparison = () => {
  if (!modelComparisonRef.value || !result.value) return

  const chart = echarts.init(modelComparisonRef.value)
  const xgboost = result.value.model_evaluation.XGBoost

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '15%',
      right: '10%',
      top: '10%',
      bottom: '10%'
    },
    xAxis: {
      type: 'value',
      axisLabel: { color: '#999' },
      axisLine: { lineStyle: { color: '#333' } },
      splitLine: { lineStyle: { color: '#222' } }
    },
    yAxis: {
      type: 'category',
      data: ['R² Train', 'R² Test', 'MAE', 'RMSE'],
      axisLabel: { color: '#fff' },
      axisLine: { lineStyle: { color: '#333' } }
    },
    series: [{
      type: 'bar',
      data: [
        xgboost.r2_train,
        xgboost.r2_test,
        xgboost.mae / 10, // 缩放以便显示
        xgboost.rmse / 10
      ],
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#00d4ff' },
          { offset: 1, color: '#0066ff' }
        ])
      },
      label: {
        show: true,
        position: 'right',
        color: '#fff',
        formatter: (params: any) => {
          if (params.dataIndex < 2) return params.value.toFixed(4)
          return (params.value * 10).toFixed(2)
        }
      }
    }]
  })
}

// 3. 交叉验证结果
const renderCVResults = () => {
  if (!cvResultsRef.value || !result.value) return

  const chart = echarts.init(cvResultsRef.value)
  const xgboost = result.value.model_evaluation.XGBoost

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      formatter: '{b}: {c}'
    },
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 1,
      splitNumber: 10,
      axisLine: {
        lineStyle: {
          width: 30,
          color: [
            [0.3, '#ff4444'],
            [0.7, '#ffaa00'],
            [1, '#00ff88']
          ]
        }
      },
      pointer: {
        itemStyle: { color: '#00d4ff' }
      },
      axisTick: {
        distance: -30,
        length: 8,
        lineStyle: { color: '#fff', width: 2 }
      },
      splitLine: {
        distance: -30,
        length: 30,
        lineStyle: { color: '#fff', width: 4 }
      },
      axisLabel: {
        color: '#fff',
        distance: 40,
        fontSize: 12
      },
      detail: {
        valueAnimation: true,
        formatter: '{value}',
        color: '#fff',
        fontSize: 24,
        offsetCenter: [0, '70%']
      },
      title: {
        offsetCenter: [0, '90%'],
        fontSize: 14,
        color: '#999'
      },
      data: [{
        value: xgboost.cv_mean,
        name: 'CV Mean R²'
      }]
    }]
  })
}

// 趋势判断辅助函数
const getTrendClass = (index: number) => {
  if (!result.value) return ''
  const current = result.value.future_prediction.predicted_response_time[index]
  const previous = result.value.future_prediction.predicted_response_time[index - 1]

  if (current > previous) return 'trend-up'
  if (current < previous) return 'trend-down'
  return 'trend-stable'
}

const getTrendIcon = (index: number) => {
  if (!result.value) return ''
  const current = result.value.future_prediction.predicted_response_time[index]
  const previous = result.value.future_prediction.predicted_response_time[index - 1]

  if (current > previous) return '↑'
  if (current < previous) return '↓'
  return '→'
}

const getTrendText = (index: number) => {
  if (!result.value) return ''
  const current = result.value.future_prediction.predicted_response_time[index]
  const previous = result.value.future_prediction.predicted_response_time[index - 1]
  const change = ((current - previous) / previous * 100).toFixed(2)

  if (current > previous) return t('pages.responseTimePrediction.increase') + ` ${change}%`
  if (current < previous) return t('pages.responseTimePrediction.decrease') + ` ${Math.abs(parseFloat(change))}%`
  return t('pages.responseTimePrediction.stable')
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
  stopPolling()
  window.removeEventListener('resize', updatePageHeight)
})
</script>

<style scoped>
.response-time-prediction {
  box-sizing: border-box;
  overflow-y: auto;
  width: 100%;
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

/* 控制面板 */
.control-panel {
  background: linear-gradient(135deg, #1a1a1a, #0a0a0a);
  border: 1px solid #333;
  border-radius: 10px;
  padding: 30px;
  margin-bottom: 30px;
  text-align: center;
}

.mode-notice {
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 20px;
  font-size: 14px;
  color: #00d4ff;
  text-align: left;
}

.start-btn {
  padding: 15px 50px;
  background: linear-gradient(135deg, #00d4ff, #0066ff);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.start-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
}

.start-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 进度条 */
.progress-container {
  margin-top: 30px;
}

.progress-bar {
  width: 100%;
  height: 30px;
  background: #1a1a1a;
  border-radius: 15px;
  overflow: hidden;
  border: 1px solid #333;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #0066ff);
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
}

.progress-percent {
  color: #00d4ff;
  font-weight: bold;
}

.progress-message {
  color: #999;
}

/* 消息提示 */
.error-message {
  margin-top: 20px;
  padding: 15px;
  background: rgba(255, 68, 68, 0.1);
  border: 1px solid #ff4444;
  border-radius: 5px;
  color: #ff4444;
}

.success-message {
  margin-top: 20px;
  padding: 15px;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid #00ff88;
  border-radius: 5px;
  color: #00ff88;
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
  grid-template-columns: repeat(2, 1fr);
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
  height: 400px;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
}

.prediction-table {
  width: 100%;
  border-collapse: collapse;
}

.prediction-table th,
.prediction-table td {
  padding: 12px;
  text-align: center;
  border-bottom: 1px solid #333;
}

.prediction-table th {
  background: #1a1a1a;
  color: #00d4ff;
  font-weight: bold;
}

.prediction-table td {
  color: #ccc;
}

.predicted-value {
  color: #00d4ff;
  font-weight: bold;
}

.trend-up {
  color: #ff4444;
}

.trend-down {
  color: #00ff88;
}

.trend-stable {
  color: #999;
}

/* 参数网格 */
.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.param-item {
  background: #0a0a0a;
  border: 1px solid #333;
  border-radius: 5px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-key {
  font-size: 12px;
  color: #999;
}

.param-value {
  font-size: 16px;
  color: #00d4ff;
  font-weight: bold;
}

@media (max-width: 1200px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-container {
    grid-template-columns: 1fr;
  }
}
</style>