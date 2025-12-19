/**
 * 翻译键值结构定义
 * 用于类型安全和自动补全
 */
export const translationKeys = {
  common: {
    language: 'common.language',
  },
  menu: {
    overview: 'menu.overview',
    activity: 'menu.activity',
    impact: 'menu.impact',
    contributor: 'menu.contributor',
    issue: 'menu.issue',
    code: 'menu.code',
    community: 'menu.community',
    forkPrediction: 'menu.forkPrediction',
    indicatorStatistics: 'menu.indicatorStatistics',
    responseTimePrediction: 'menu.responseTimePrediction',
  },
  layout: {
    openDigger: 'layout.openDigger',
  },
  pages: {
    overview: {
      title: 'pages.overview.title',
      subtitle: 'pages.overview.subtitle',
      stats: {
        projects: 'pages.overview.stats.projects',
        avgStars: 'pages.overview.stats.avgStars',
        activity: 'pages.overview.stats.activity',
        contributors: 'pages.overview.stats.contributors',
      },
      charts: {
        activityTrend: 'pages.overview.charts.activityTrend',
        starTop10: 'pages.overview.charts.starTop10',
        emailEcosystem: 'pages.overview.charts.emailEcosystem',
        forkTop10: 'pages.overview.charts.forkTop10',
        issueResponseTrend: 'pages.overview.charts.issueResponseTrend',
      },
      ranking: {
        title: 'pages.overview.ranking.title',
        starRanking: 'pages.overview.ranking.starRanking',
        activityRanking: 'pages.overview.ranking.activityRanking',
        forkRanking: 'pages.overview.ranking.forkRanking',
      },
    },
  },
} as const

/**
 * 类型推导：确保使用的键值都在翻译文件中定义
 */
export type TranslationKey = typeof translationKeys[keyof typeof translationKeys] extends infer T
  ? T extends Record<string, infer U>
    ? U extends string
      ? U
      : T extends Record<string, infer V>
      ? V extends string
        ? V
        : never
      : never
    : T
  : never
