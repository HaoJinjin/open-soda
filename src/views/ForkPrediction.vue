<template>
  <div class="fork-prediction" :style="{ height: pageHeight + 'px' }">
    <header class="page-header">
      <h1 class="page-title">🔱 {{ $t("menu.forkPrediction") }}</h1>
      <p class="page-subtitle">
        {{ $t("pages.forkPrediction.subtitle") }}（{{
          metadata.model_used || $t("common.loading")
        }}）
      </p>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">{{ $t("common.loadingData") }}...</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <p class="error-text">{{ error }}</p>
      <button @click="loadPrediction" class="retry-btn">
        {{ $t("common.retry") }}
      </button>
    </div>

    <!-- 主内容 -->
    <div v-else class="content">
      <!-- 模型评估指标卡片 -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon">🎯</div>
          <div class="metric-content">
            <div class="metric-value">{{ formatNumber(metrics.R2_test) }}</div>
            <div class="metric-label">
              R² {{ $t("pages.forkPrediction.score") }}
            </div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">📊</div>
          <div class="metric-content">
            <div class="metric-value">
              {{ formatNumber(metrics.RMSE_test) }}
            </div>
            <div class="metric-label">RMSE</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">📈</div>
          <div class="metric-content">
            <div class="metric-value">{{ formatNumber(metrics.MAE_test) }}</div>
            <div class="metric-label">MAE</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">🔢</div>
          <div class="metric-content">
            <div class="metric-value">{{ metadata.valid_samples }}</div>
            <div class="metric-label">
              {{ $t("pages.forkPrediction.validSamples") }}
            </div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-container">
        <!-- 特征重要性图 -->
        <div class="chart-box">
          <h3 class="chart-title">
            🎯 {{ $t("pages.forkPrediction.featureImportance") }}
          </h3>
          <div ref="featureImportanceRef" class="chart"></div>
        </div>

        <!-- 预测结果散点图 -->
        <div class="chart-box">
          <h3 class="chart-title">
            📊 {{ $t("pages.forkPrediction.predictedVsActual") }}
          </h3>
          <div ref="predictionScatterRef" class="chart"></div>
        </div>

        <!-- 预测误差分布 -->
        <div class="chart-box full-width">
          <h3 class="chart-title">
            📉 {{ $t("pages.forkPrediction.errorDistribution") }}
          </h3>
          <div ref="errorDistributionRef" class="chart"></div>
        </div>

        <!-- 预测结果表格 -->
        <div class="chart-box full-width">
          <h3 class="chart-title">
            📋 {{ $t("pages.forkPrediction.predictionDetails") }}（Top 20）
          </h3>
          <div class="table-container">
            <table class="prediction-table">
              <thead>
                <tr>
                  <th>{{ $t("pages.forkPrediction.rank") }}</th>
                  <th>{{ $t("pages.forkPrediction.projectName") }}</th>
                  <th>{{ $t("pages.forkPrediction.actualValue") }}</th>
                  <th>{{ $t("pages.forkPrediction.predictedValue") }}</th>
                  <th>{{ $t("pages.forkPrediction.absoluteError") }}</th>
                  <th>{{ $t("pages.forkPrediction.relativeError") }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in topPredictions" :key="index">
                  <td>{{ index + 1 }}</td>
                  <td class="project-name">{{ item.project_name }}</td>
                  <td>{{ formatNumber(item.true_value) }}</td>
                  <td>{{ formatNumber(item.predicted_value) }}</td>
                  <td>{{ formatNumber(item.absolute_error) }}</td>
                  <td :class="getErrorClass(item.relative_error_percent)">
                    {{ formatNumber(item.relative_error_percent) }}%
                  </td>
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
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import * as echarts from "echarts";
import axios from "axios";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

// 响应式数据
const loading = ref(true);
const error = ref("");
const metadata = ref<any>({});
const metrics = ref<any>({});
const predictions = ref<any[]>([]);
const featureImportance = ref<any[]>([]);
const topPredictions = ref<any[]>([]);

// 图表引用
const featureImportanceRef = ref<HTMLElement>();
const predictionScatterRef = ref<HTMLElement>();
const errorDistributionRef = ref<HTMLElement>();

// 加载预测数据
const loadPrediction = async () => {
  loading.value = true;
  error.value = "";

  try {
    const response = await axios.get("/src/views/forkPrediction.json");

    if (response.data) {
      const data = response.data;

      // 提取数据
      metadata.value = data.metadata;
      metrics.value = data.metadata.performance_metrics;
      predictions.value = data.predictions;
      featureImportance.value = data.feature_importance || [];

      // 对预测结果按真实值降序排序
      predictions.value.sort((a, b) => b.true_value - a.true_value);
      topPredictions.value = predictions.value.slice(0, 20);

      // 先关闭 loading，让 DOM 渲染
      loading.value = false;

      // 等待 DOM 更新完成后再渲染图表
      await nextTick();
      renderCharts();
    } else {
      error.value = t("common.loadFailed");
      loading.value = false;
    }
  } catch (err: any) {
    error.value =
      t("common.loadError") + ": " + (err.message || t("common.unknownError"));
    loading.value = false;
  }
};

// 渲染图表
const renderCharts = () => {
  renderFeatureImportance();
  renderPredictionScatter();
  renderErrorDistribution();
};

// 1. 特征重要性图
const renderFeatureImportance = () => {
  if (!featureImportanceRef.value) return;

  const chart = echarts.init(featureImportanceRef.value);
  const top10Features = featureImportance.value.slice(0, 10);

  chart.setOption({
    backgroundColor: "transparent",
    grid: { left: "15%", right: "10%", top: "10%", bottom: "10%" },
    xAxis: {
      type: "value",
      axisLine: { lineStyle: { color: "#333" } },
      axisLabel: { color: "#999" },
    },
    yAxis: {
      type: "category",
      data: top10Features.map((f) => f.feature_name || f.feature).reverse(),
      axisLine: { lineStyle: { color: "#333" } },
      axisLabel: { color: "#fff" },
    },
    series: [
      {
        type: "bar",
        data: top10Features.map((f) => f.importance.toFixed(4)).reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: "#00d4ff" },
            { offset: 1, color: "#0066ff" },
          ]),
        },
        label: {
          show: true,
          position: "right",
          color: "#fff",
          formatter: "{c}",
        },
      },
    ],
  });
};

// 2. 预测散点图
const renderPredictionScatter = () => {
  if (!predictionScatterRef.value) return;

  const chart = echarts.init(predictionScatterRef.value);
  const scatterData = predictions.value.map((p) => {
    if (p.true_value < 2000) return [p.true_value, p.predicted_value];
  });
  const maxVal = Math.max(
    ...predictions.value.map((p) => Math.max(p.true_value, p.predicted_value))
  );

  chart.setOption({
    backgroundColor: "transparent",
    grid: { left: "12%", right: "10%", top: "15%", bottom: "15%" },
    xAxis: {
      type: "value",
      name: t("pages.forkPrediction.actualValue"),
      nameTextStyle: { color: "#fff" },
      axisLine: { lineStyle: { color: "#333" } },
      axisLabel: { color: "#999" },
    },
    yAxis: {
      type: "value",
      name: t("pages.forkPrediction.predictedValue"),
      nameTextStyle: { color: "#fff" },
      axisLine: { lineStyle: { color: "#333" } },
      axisLabel: { color: "#999" },
    },
    series: [
      {
        type: "scatter",
        data: scatterData,
        symbolSize: 8,
        itemStyle: { color: "#00d4ff", opacity: 0.6 },
      },
      {
        type: "line",
        data: [
          [0, 0],
          [500, 500],
        ],
        lineStyle: { color: "#ff4444", type: "dashed", width: 2 },
        symbol: "none",
        silent: true,
      },
    ],
  });
};

// 3. 误差分布图
const renderErrorDistribution = () => {
  if (!errorDistributionRef.value) return;

  const chart = echarts.init(errorDistributionRef.value);
  const errors = predictions.value.map((p) => p.relative_error_percent);

  chart.setOption({
    backgroundColor: "transparent",
    grid: { left: "10%", right: "10%", top: "15%", bottom: "15%" },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const index = params.dataIndex;
        const item = predictions.value[index];
        return `
          <strong>${item.project_name}</strong><br/>
          ${t("pages.forkPrediction.actualValue")}: ${formatNumber(item.true_value)}<br/>
          ${t("pages.forkPrediction.predictedValue")}: ${formatNumber(item.predicted_value)}<br/>
          ${t("pages.forkPrediction.absoluteError")}: ${formatNumber(item.absolute_error)}<br/>
          ${t("pages.forkPrediction.relativeError")}: ${formatNumber(item.relative_error_percent)}%
        `;
      }
    },
    xAxis: {
      type: "category",
      data: predictions.value.map((_, i) => i + 1),
      axisLine: { lineStyle: { color: "#333" } },
      axisLabel: { color: "#999", interval: 9 },
    },
    yAxis: {
      type: "value",
      name: t("pages.forkPrediction.relativeError") + " (%)",
      nameTextStyle: { color: "#fff" },
      axisLine: { lineStyle: { color: "#333" } },
      axisLabel: { color: "#999" },
    },
    series: [
      {
        type: "bar",
        data: errors,
        itemStyle: {
          color: (params: any) => {
            const val = params.value;
            if (val < 5) return "#00ff88";
            if (val < 10) return "#ffaa00";
            return "#ff4444";
          },
        },
      },
    ],
  });
};

// 格式化数字（处理字符串和数值）
const formatNumber = (value: any): string => {
  if (value === null || value === undefined) return "0.00";

  // 如果是字符串，尝试转换为数字
  if (typeof value === "string") {
    const num = parseFloat(value);
    if (isNaN(num)) return value; // 如果无法转换，返回原字符串
    return num.toFixed(2);
  }

  // 如果是数字，直接格式化
  if (typeof value === "number") {
    return value.toFixed(2);
  }

  return String(value);
};

// 误差等级样式
const getErrorClass = (error: number) => {
  if (error < 5) return "error-low";
  if (error < 10) return "error-medium";
  return "error-high";
};

const pageHeight = ref(window.innerHeight);
// 更新页面高度
const updatePageHeight = () => {
  pageHeight.value = window.innerHeight;
};

onMounted(() => {
  loadPrediction();
  window.addEventListener("resize", updatePageHeight);
});

onUnmounted(() => {
  window.removeEventListener("resize", updatePageHeight);
});
</script>

<style scoped>
.fork-prediction {
  width: 100%;
  overflow-y: auto;
  box-sizing: border-box;
  padding: 20px;
  background: #000;
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
.loading-container,
.error-container {
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
  to {
    transform: rotate(360deg);
  }
}

.loading-text,
.error-text {
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
  height: 350px;
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

.project-name {
  text-align: left;
  color: #fff;
  font-weight: 500;
}

.error-low {
  color: #00ff88;
}

.error-medium {
  color: #ffaa00;
}

.error-high {
  color: #ff4444;
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
