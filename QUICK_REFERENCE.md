# 多语言系统快速参考 🚀

## 最常用的 3 种方式

### 方式 1：最简单 - 直接在模板中使用 $t()
```vue
<template>
  <h1>{{ $t('pages.activity.title') }}</h1>
  <p>{{ $t('menu.overview') }}</p>
</template>
```

### 方式 2：推荐 - 使用 useTranslations (类型安全)
```vue
<script setup lang="ts">
import { useTranslations } from '@/composables/useTranslations'
const { t, page } = useTranslations()
</script>

<template>
  <h1>{{ t(page.activity.title) }}</h1>
  <div>{{ t(page.activity.stats.avgActivity) }}</div>
</template>
```

### 方式 3：在脚本中获取翻译
```typescript
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const title = t('pages.activity.title')
```

---

## 快速添加翻译步骤

### 1. 更新 JSON 文件 (30 秒)

**src/locales/zh.json**
```json
"pages": {
  "newPage": {
    "title": "新页面标题"
  }
}
```

**src/locales/en.json**
```json
"pages": {
  "newPage": {
    "title": "New Page Title"
  }
}
```

### 2. 更新 translations.ts (10 秒)

**src/i18n/translations.ts**
```typescript
pages: {
  newPage: {
    title: 'pages.newPage.title'
  }
}
```

### 3. 在组件中使用 (5 秒)

```vue
<script setup>
const { t, page } = useTranslations()
</script>

<template>
  {{ t(page.newPage.title) }}
</template>
```

**总计：45 秒！**

---

## 翻译键值速查表

### 菜单项
```
menu.overview              // 全局总览
menu.activity              // 活跃度分析
menu.impact                // 影响力分析
menu.contributor           // 贡献者生态
menu.issue                 // Issue 生命周期
menu.code                  // PR & 代码变更
menu.community             // 社区关注度
```

### 已翻译的页面

#### 全局总览 (Overview)
```
pages.overview.title                    // 全局总览
pages.overview.subtitle                 // OpenSODA - Top 300...
pages.overview.stats.projects           // 项目
pages.overview.stats.avgStars           // 平均⭐
pages.overview.stats.activity           // 活跃度
pages.overview.stats.contributors       // 贡献者
pages.overview.charts.activityTrend     // 📈 年度活跃度趋势
pages.overview.charts.starTop10         // 🏆 Star Top 10
pages.overview.charts.emailEcosystem    // 📧 贡献者邮箱生态
pages.overview.charts.forkTop10         // 🔱 Fork Top 10
pages.overview.charts.issueResponseTrend// ⏱️ Issue 响应趋势
pages.overview.ranking.title            // 实时排行榜
pages.overview.ranking.starRanking      // ⭐ Star 排行
pages.overview.ranking.activityRanking  // 🔥 活跃度排行
pages.overview.ranking.forkRanking      // 🔱 Fork 排行
```

#### 活跃度分析 (Activity)
```
pages.activity.title                        // 活跃度分析
pages.activity.subtitle                     // Activity Analysis - ...
pages.activity.stats.avgActivity            // 平均活跃度
pages.activity.stats.newContributors        // 新贡献者总数
pages.activity.stats.inactiveContributors   // 不活跃贡献者
pages.activity.stats.activeProjects         // 高活跃项目数
pages.activity.charts.activityTrend         // 📈 活跃度趋势分布
pages.activity.charts.topActiveProjects     // 👑 Top 10 活跃项目
pages.activity.charts.newContributorsDistribution // 🌟 新贡献者分布
```

#### 影响力分析 (Impact)
```
pages.impact.title                          // 影响力分析
pages.impact.subtitle                       // Impact Analysis - ...
pages.impact.stats.totalStars               // 总星标数
pages.impact.stats.totalAttention           // 总关注度
pages.impact.stats.avgOpenRank              // 平均OpenRank
pages.impact.stats.totalForks               // 总Fork数
pages.impact.charts.starRanking             // 🌟 Star排行榜 Top 20
pages.impact.charts.openRankTop             // 🏆 OpenRank Top 15
pages.impact.charts.commentActivityDistribution // 💬 评论活跃度分布
```

#### 贡献者生态 (Contributor)
```
pages.contributor.title                     // 贡献者生态
pages.contributor.subtitle                  // Contributor Ecosystem - ...
pages.contributor.stats.avgBusFactor        // 平均巴士因子
pages.contributor.stats.totalParticipants   // 总参与者数
pages.contributor.stats.totalNewContributors// 新贡献者总数
pages.contributor.stats.inactiveContributors// 不活跃贡献者
pages.contributor.charts.busFactorDistribution  // 🚌 巴士因子分布
pages.contributor.charts.emailEcosystem     // 📧 贡献者邮箱生态
pages.contributor.charts.participantsSizeDistribution // 👤 参与者规模分布
```

#### Issue 生命周期 (Issue)
```
pages.issue.title                           // Issue 生命周期
pages.issue.subtitle                        // Issue Lifecycle - ...
pages.issue.stats.totalNewIssues            // 新增Issue总数
pages.issue.stats.totalClosedIssues         // 已关闭Issue
pages.issue.stats.activeIssuesPR            // 活跃Issue/PR
pages.issue.stats.totalComments             // Issue评论总数
pages.issue.charts.issueComparison          // 📊 Issue新增vs关闭对比
pages.issue.charts.responseTimeTrend        // ⏱️ Issue响应时间趋势
pages.issue.charts.resolutionTimeTrend      // 🔧 Issue解决时长趋势
```

#### PR & 代码变更 (Code)
```
pages.code.title                            // PR & 代码变更
pages.code.subtitle                         // Pull Request & Code Changes - ...
pages.code.stats.totalPRs                   // PR总数
pages.code.stats.acceptedPRs                // 已接受PR
pages.code.stats.linesAdded                 // 新增代码行
pages.code.stats.linesRemoved               // 删除代码行
pages.code.charts.codeChangeTop             // 📊 代码变更量 Top 20
pages.code.charts.prAcceptanceRate          // 🔀 PR接受率分布
pages.code.charts.prReviewActivity          // 📝 PR评审活跃度
```

#### 社区关注度 (Community)
```
pages.community.title                       // 社区关注度
pages.community.subtitle                    // Community Attention - ...
pages.community.stats.totalAttention        // 总关注度
pages.community.stats.totalStars            // 总星标数
pages.community.stats.totalForks            // 总Fork数
pages.community.stats.totalParticipants     // 总参与者
pages.community.charts.attentionRanking     // 🔥 关注度排行 Top 20
pages.community.charts.starForkRelationship // ⭐ Star vs Fork 关系
pages.community.charts.communityInteractionHeat // 💬 社区互动热度
```

---

## IDE 自动补全技巧

如果你使用 TypeScript 和 useTranslations：

```typescript
const { page } = useTranslations()

// 在编辑器中输入时会获得自动补全：
page.              // ← 按 Ctrl+Space 显示所有页面
page.activity.     // ← 按 Ctrl+Space 显示所有 activity 子项
page.activity.title // ← 直接可用！
```

---

## 语言切换方式

### 用户方式（最简单）
点击侧边栏底部的 "中文" / "English" 按钮

### 程序方式
```typescript
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

// 切换到英文
locale.value = 'en'

// 切换到中文
locale.value = 'zh'

// 获取当前语言
console.log(locale.value) // 'zh' 或 'en'
```

---

## 常见问题

### Q: 如何找到某个文本的翻译键？
**A:** 在 src/i18n/translations.ts 中搜索，或查看 QUICK_REFERENCE.md 中的速查表

### Q: 翻译没有显示怎么办？
**A:**
1. 检查键是否在 JSON 文件中存在
2. 检查 TypeScript 定义是否正确
3. 检查组件是否已导入 useTranslations
4. 查看浏览器 console 是否有错误

### Q: 如何添加新的翻译？
**A:** 按照上面的"快速添加翻译步骤"即可，总共 45 秒

### Q: 能同时支持多个语言吗？
**A:** 能！在 src/locales/ 中添加新的 JSON 文件，然后在 src/i18n.js 中注册即可

### Q: localStorage 中翻译选择的键是什么？
**A:** `language`

---

## 文件清单

| 文件 | 作用 | 修改频率 |
|------|------|---------|
| src/locales/zh.json | 中文翻译内容 | 高 |
| src/locales/en.json | 英文翻译内容 | 高 |
| src/i18n/translations.ts | TypeScript 类型定义 | 中 |
| src/composables/useTranslations.ts | 翻译 Hook | 低 |
| src/i18n.js | i18n 配置 | 低 |
| src/components/LanguageSwitcher.vue | 语言切换组件 | 低 |

---

**最后更新**：2025-12-19
**快速参考版本**：1.0
