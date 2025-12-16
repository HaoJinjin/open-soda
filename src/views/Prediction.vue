<template>
  <div class="prediction-page" :style="{ height: pageHeight + 'px' }">
    <header class="page-header">
      <h1 class="page-title">🔮 智能预测</h1>
      <p class="page-subtitle">Machine Learning Prediction - 基于随机森林的指标预测</p>
    </header>

    <!-- 预测配置 -->
    <div class="prediction-config">
      <div class="config-card">
        <h3 class="config-title">📊 选择预测目标</h3>
        <div class="form-group">
          <label>目标列：</label>
          <select v-model="selectedColumn" class="select-input">
            <option value="">-- 请选择要预测的指标 --</option>
            <option v-for="col in availableColumns" :key="col" :value="col">
              {{ col }}
            </option>
          </select>
        </div>
        <button 
          @click="startPrediction" 
          :disabled="!selectedColumn || loading"
          class="predict-btn"
        >
          <span v-if="loading">⏳ 预测中...</span>
          <span v-else>🚀 开始预测</span>
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在训练模型并生成预测结果...</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-container">
      <p>❌ {{ error }}</p>
    </div>

    <!-- 预测结果 -->
    <div v-if="predictionResult && !loading" class="results-container">
      <!-- 模型指标 -->
      <div class="metrics-section">
        <h3 class="section-title">📈 模型评估指标</h3>
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-content">
              <div class="metric-value">{{ predictionResult.predictions.metadata.metrics.R2_score }}</div>
              <div class="metric-label">R² 得分</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">📏</div>
            <div class="metric-content">
              <div class="metric-value">{{ predictionResult.predictions.metadata.metrics.RMSE }}</div>
              <div class="metric-label">RMSE</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-content">
              <div class="metric-value">{{ predictionResult.predictions.metadata.metrics.MAE }}</div>
              <div class="metric-label">MAE</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">🔢</div>
            <div class="metric-content">
              <div class="metric-value">{{ predictionResult.predictions.metadata.test_samples }}</div>
              <div class="metric-label">测试样本数</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 特征重要性 -->
      <div class="importance-section">
        <h3 class="section-title">⭐ 特征重要性排名</h3>
        <div class="importance-list">
          <div 
            v-for="(item, index) in predictionResult.feature_importance.feature_importance.slice(0, 10)" 
            :key="index"
            class="importance-item"
          >
            <span class="rank">{{ index + 1 }}</span>
            <span class="feature-name">{{ item.feature_name }}</span>
            <div class="importance-bar">
              <div 
                class="importance-fill" 
                :style="{ width: (item.importance * 100) + '%' }"
              ></div>
            </div>
            <span class="importance-value">{{ (item.importance * 100).toFixed(2) }}%</span>
          </div>
        </div>
      </div>

      <!-- 预测结果表格 -->
      <div class="predictions-section">
        <h3 class="section-title">📋 预测结果（前20条）</h3>
        <div class="table-container">
          <table class="predictions-table">
            <thead>
              <tr>
                <th>项目名称</th>
                <th>真实值</th>
                <th>预测值</th>
                <th>绝对误差</th>
                <th>相对误差</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(pred, index) in predictionResult.predictions.predictions.slice(0, 20)" :key="index">
                <td>{{ pred.project_name }}</td>
                <td>{{ pred.true_value }}</td>
                <td>{{ pred.predicted_value }}</td>
                <td>{{ pred.absolute_error }}</td>
                <td>{{ pred.relative_error_percent }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const selectedColumn = ref('')
const loading = ref(false)
const error = ref('')
const predictionResult = ref<any>(null)
const pageHeight = ref(window.innerHeight)

// 可用的列（根据你的数据集）
const availableColumns = [
  'stars', 'forks', 'watchers', 'contributors',
  'issues', 'pull_requests', 'commits', 'activity'
]

const startPrediction = async () => {
  if (!selectedColumn.value) return

  loading.value = true
  error.value = ''
  predictionResult.value = null

  try {
    const response = await axios.post('http://localhost:8000/predict', {
      target_column: selectedColumn.value
    })

    if (response.data.success) {
      predictionResult.value = response.data.data
    } else {
      error.value = '预测失败，请重试'
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || '网络错误，请检查后端服务是否启动'
  } finally {
    loading.value = false
  }
}

// 更新页面高度
const updatePageHeight = () => {
  pageHeight.value = window.innerHeight
  console.log('页面高度更新为：', pageHeight.value)
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
.prediction-page {
  width: 100%;
  display: flex;
  flex-direction: column;
  background: #000000;
  background-image:
    radial-gradient(circle at 10% 20%, rgba(0, 242, 254, 0.05) 0%, transparent 40%),
    radial-gradient(circle at 90% 80%, rgba(0, 242, 254, 0.05) 0%, transparent 40%),
    linear-gradient(180deg, #000000 0%, #0a0a0a 50%, #000000 100%);
  padding: 15px;
  color: #fff;
  overflow-y: auto;
  position: relative;
  box-sizing: border-box;
}


.prediction-page::-webkit-scrollbar {
  width: 6px;
}

.prediction-page::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.prediction-page::-webkit-scrollbar-thumb {
  background: rgba(0, 242, 254, 0.3);
  border-radius: 3px;
}

.prediction-page::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 242, 254, 0.5);
}

.prediction-page::before {
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
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 242, 254, 0.3);
  position: relative;
  z-index: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #00f2fe;
  margin-bottom: 8px;
  text-shadow: 0 0 15px rgba(0, 242, 254, 0.6);
}

.page-subtitle {
  font-size: 13px;
  color: #a0d2eb;
  letter-spacing: 1px;
}

.prediction-config {
  position: relative;
  z-index: 1;
  margin-bottom: 20px;
}

.config-card {
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(0, 242, 254, 0.3);
  border-radius: 10px;
  padding: 20px;
  backdrop-filter: blur(10px);
  box-shadow:
    0 2px 10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(0, 242, 254, 0.1);
}

.config-title {
  font-size: 18px;
  color: #00f2fe;
  margin-bottom: 15px;
  text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  color: #a0d2eb;
  margin-bottom: 8px;
  font-size: 14px;
}

.select-input {
  width: 100%;
  padding: 10px 15px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 242, 254, 0.3);
  border-radius: 5px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.select-input:focus {
  border-color: rgba(0, 242, 254, 0.6);
  box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
}

.select-input option {
  background: #1a1a1a;
  color: #fff;
}

.predict-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #00f2fe, #4facfe);
  border: none;
  border-radius: 5px;
  color: #000;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
}

.predict-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 242, 254, 0.5);
}

.predict-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-container,
.error-container {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 40px;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(0, 242, 254, 0.3);
  border-radius: 10px;
  margin: 20px 0;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(0, 242, 254, 0.2);
  border-top-color: #00f2fe;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-container {
  color: #ff6b6b;
  border-color: rgba(255, 107, 107, 0.3);
}

.results-container {
  position: relative;
  z-index: 1;
}

.metrics-section,
.importance-section,
.predictions-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  color: #00f2fe;
  margin-bottom: 15px;
  text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.metric-card {
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(0, 242, 254, 0.3);
  border-radius: 10px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
  box-shadow:
    0 2px 10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(0, 242, 254, 0.1);
}

.metric-card:hover {
  transform: translateY(-3px);
  box-shadow:
    0 4px 20px rgba(0, 242, 254, 0.3),
    0 0 30px rgba(0, 242, 254, 0.15);
  border-color: rgba(0, 242, 254, 0.5);
}

.metric-icon {
  font-size: 28px;
  filter: drop-shadow(0 0 8px rgba(0, 242, 254, 0.5));
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: #00f2fe;
  margin-bottom: 3px;
  text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
}

.metric-label {
  font-size: 11px;
  color: #a0d2eb;
}

.importance-list {
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(0, 242, 254, 0.3);
  border-radius: 10px;
  padding: 15px;
  backdrop-filter: blur(10px);
}

.importance-item {
  display: grid;
  grid-template-columns: 30px 1fr 2fr 80px;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 242, 254, 0.1);
}

.importance-item:last-child {
  border-bottom: none;
}

.rank {
  color: #00f2fe;
  font-weight: 700;
  font-size: 14px;
}

.feature-name {
  color: #a0d2eb;
  font-size: 12px;
}

.importance-bar {
  height: 8px;
  background: rgba(0, 242, 254, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.importance-fill {
  height: 100%;
  background: linear-gradient(90deg, #00f2fe, #4facfe);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.importance-value {
  color: #00f2fe;
  font-size: 12px;
  font-weight: 600;
  text-align: right;
}

.table-container {
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(0, 242, 254, 0.3);
  border-radius: 10px;
  padding: 15px;
  overflow-x: auto;
  backdrop-filter: blur(10px);
}

.predictions-table {
  width: 100%;
  border-collapse: collapse;
}

.predictions-table thead th {
  background: rgba(0, 242, 254, 0.1);
  color: #00f2fe;
  padding: 10px;
  text-align: left;
  font-size: 12px;
  border-bottom: 2px solid rgba(0, 242, 254, 0.3);
}

.predictions-table tbody td {
  padding: 10px;
  color: #a0d2eb;
  font-size: 12px;
  border-bottom: 1px solid rgba(0, 242, 254, 0.1);
}

.predictions-table tbody tr:hover {
  background: rgba(0, 242, 254, 0.05);
}

.predictions-table tbody tr:last-child td {
  border-bottom: none;
}
</style>

