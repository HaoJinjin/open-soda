<template>
  <div class="layout">
    <!-- 侧边菜单 -->
    <aside class="menu">
      <div class="logo-container">
        <h2>OpenSODA</h2>
        <div class="logo-divider"></div>
      </div>
      
      <ul class="menu-list">
        <li 
          v-for="m in menus"
          :key="m.key"
          :class="{active: current===m.key}"
          @click="selectMenu(m)"
          class="menu-item"
        >
          <span class="menu-title">{{ m.title }}</span>
        </li>
      </ul>
      
      <div class="menu-footer">
        <div class="tech-badge">OpenDigger</div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

interface Menu {
  key: string
  title: string
}

const current = ref("overview")

const menus: Menu[] = [
  { key: "overview", title: "全局总览" },
  { key: "activity", title: "活跃度分析" },
  { key: "impact", title: "影响力分析" },
  { key: "contributor", title: "贡献者生态" },
  { key: "issue", title: "Issue 生命周期" },
  { key: "code", title: "PR & 代码变更" },
  { key: "community", title: "社区关注度" },
  { key: "fork-prediction", title: "🔱 Fork 预测" },
  { key: "indicator-statistics", title: "📊 指标统计" },
  { key: "response-time-prediction", title: "⏱️ 响应时间预测" }
]

function selectMenu(m: Menu) {
  current.value = m.key
  // 根据菜单项导航到相应的路由
  switch(m.key) {
    case "overview":
      router.push({ name: "showBoard" })
      break
    case "activity":
      router.push({ name: "activity" })
      break
    case "impact":
      router.push({ name: "impact" })
      break
    case "contributor":
      router.push({ name: "contributor" })
      break
    case "issue":
      router.push({ name: "issue" })
      break
    case "code":
      router.push({ name: "code" })
      break
    case "community":
      router.push({ name: "community" })
      break
    case "fork-prediction":
      router.push({ name: "forkPrediction" })
      break
    case "indicator-statistics":
      router.push({ name: "indicatorStatistics" })
      break
    case "response-time-prediction":
      router.push({ name: "responseTimePrediction" })
      break
    default:
      router.push({ name: "showBoard" })
  }
}
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  min-width: 200px;
}

.menu {
  width: 200px;
  /* height: 100%; */
  background: #000000;
  background-image:
    linear-gradient(180deg, #000000 0%, #0a0a0a 50%, #000000 100%),
    radial-gradient(circle at 50% 0%, rgba(0, 242, 254, 0.05) 0%, transparent 50%);
  border-right: 1px solid rgba(0, 242, 254, 0.4);
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  box-shadow:
    2px 0 20px rgba(0, 0, 0, 0.8),
    inset -1px 0 0 rgba(0, 242, 254, 0.1);
  position: relative;
}

.menu::before {
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
      rgba(0, 242, 254, 0.02) 2px,
      rgba(0, 242, 254, 0.02) 4px
    );
  pointer-events: none;
  opacity: 0.5;
}

.logo-container {
  padding: 0 20px 20px;
  position: relative;
  z-index: 1;
}

.logo-container h2 {
  font-size: 24px;
  font-weight: 700;
  color: #00f2fe;
  margin-bottom: 12px;
  text-align: center;
  text-shadow:
    0 0 15px rgba(0, 242, 254, 0.8),
    0 0 30px rgba(0, 242, 254, 0.4);
  letter-spacing: 2px;
  animation: logoGlow 3s ease-in-out infinite;
}

@keyframes logoGlow {
  0%, 100% {
    text-shadow:
      0 0 15px rgba(0, 242, 254, 0.8),
      0 0 30px rgba(0, 242, 254, 0.4);
  }
  50% {
    text-shadow:
      0 0 20px rgba(0, 242, 254, 1),
      0 0 40px rgba(0, 242, 254, 0.6),
      0 0 60px rgba(0, 242, 254, 0.3);
  }
}

.logo-divider {
  height: 2px;
  background: linear-gradient(90deg, transparent, #00f2fe, transparent);
  margin: 0 10px;
  box-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
}

.menu-list {
  flex: 1;
  list-style: none;
  padding: 10px 0;
  margin: 0;
  position: relative;
  z-index: 1;
}

.menu-item {
  padding: 15px 20px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
  color: #a0d2eb;
  border-left: 3px solid transparent;
  margin: 2px 0;
}

.menu-item:hover {
  background: rgba(0, 242, 254, 0.15);
  color: #00f2fe;
  box-shadow:
    inset 0 0 20px rgba(0, 242, 254, 0.1),
    0 0 15px rgba(0, 242, 254, 0.2);
}

.menu-item.active {
  background: rgba(0, 242, 254, 0.2);
  color: #00f2fe;
  border-left: 3px solid #00f2fe;
  box-shadow:
    inset 0 0 25px rgba(0, 242, 254, 0.15),
    0 0 20px rgba(0, 242, 254, 0.3),
    inset -1px 0 0 rgba(0, 242, 254, 0.2);
}

.menu-item.active .menu-title {
  text-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
}

.menu-item::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 242, 254, 0.3), transparent);
  opacity: 0.5;
}

.menu-item:first-child::before {
  display: none;
}

.menu-item::after {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 60%;
  background: linear-gradient(90deg, #00f2fe, transparent);
  transition: width 0.3s ease;
  opacity: 0;
}

.menu-item:hover::after {
  width: 100%;
  opacity: 0.1;
}

.menu-item.active::after {
  width: 100%;
  opacity: 0.15;
}

.menu-title {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 1px;
  position: relative;
  z-index: 1;
}

.menu-footer {
  padding: 20px;
  text-align: center;
  position: relative;
  z-index: 1;
}

.tech-badge {
  display: inline-block;
  padding: 8px 16px;
  background: rgba(0, 242, 254, 0.15);
  color: #00f2fe;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1.5px;
  border: 1px solid rgba(0, 242, 254, 0.4);
  box-shadow:
    0 0 15px rgba(0, 242, 254, 0.3),
    inset 0 1px 0 rgba(0, 242, 254, 0.2);
  text-transform: uppercase;
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% {
    box-shadow:
      0 0 15px rgba(0, 242, 254, 0.3),
      inset 0 1px 0 rgba(0, 242, 254, 0.2);
  }
  50% {
    box-shadow:
      0 0 25px rgba(0, 242, 254, 0.5),
      inset 0 1px 0 rgba(0, 242, 254, 0.3);
  }
}
</style>