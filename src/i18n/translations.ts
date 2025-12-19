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
    activity: {
      title: 'pages.activity.title',
      subtitle: 'pages.activity.subtitle',
      stats: {
        avgActivity: 'pages.activity.stats.avgActivity',
        newContributors: 'pages.activity.stats.newContributors',
        inactiveContributors: 'pages.activity.stats.inactiveContributors',
        activeProjects: 'pages.activity.stats.activeProjects',
      },
      charts: {
        activityTrend: 'pages.activity.charts.activityTrend',
        topActiveProjects: 'pages.activity.charts.topActiveProjects',
        newContributorsDistribution: 'pages.activity.charts.newContributorsDistribution',
      },
    },
    impact: {
      title: 'pages.impact.title',
      subtitle: 'pages.impact.subtitle',
      stats: {
        totalStars: 'pages.impact.stats.totalStars',
        totalAttention: 'pages.impact.stats.totalAttention',
        avgOpenRank: 'pages.impact.stats.avgOpenRank',
        totalForks: 'pages.impact.stats.totalForks',
      },
      charts: {
        starRanking: 'pages.impact.charts.starRanking',
        openRankTop: 'pages.impact.charts.openRankTop',
        commentActivityDistribution: 'pages.impact.charts.commentActivityDistribution',
      },
    },
    contributor: {
      title: 'pages.contributor.title',
      subtitle: 'pages.contributor.subtitle',
      stats: {
        avgBusFactor: 'pages.contributor.stats.avgBusFactor',
        totalParticipants: 'pages.contributor.stats.totalParticipants',
        totalNewContributors: 'pages.contributor.stats.totalNewContributors',
        inactiveContributors: 'pages.contributor.stats.inactiveContributors',
      },
      charts: {
        busFactorDistribution: 'pages.contributor.charts.busFactorDistribution',
        emailEcosystem: 'pages.contributor.charts.emailEcosystem',
        participantsSizeDistribution: 'pages.contributor.charts.participantsSizeDistribution',
      },
    },
    issue: {
      title: 'pages.issue.title',
      subtitle: 'pages.issue.subtitle',
      stats: {
        totalNewIssues: 'pages.issue.stats.totalNewIssues',
        totalClosedIssues: 'pages.issue.stats.totalClosedIssues',
        activeIssuesPR: 'pages.issue.stats.activeIssuesPR',
        totalComments: 'pages.issue.stats.totalComments',
      },
      charts: {
        issueComparison: 'pages.issue.charts.issueComparison',
        responseTimeTrend: 'pages.issue.charts.responseTimeTrend',
        resolutionTimeTrend: 'pages.issue.charts.resolutionTimeTrend',
      },
    },
    code: {
      title: 'pages.code.title',
      subtitle: 'pages.code.subtitle',
      stats: {
        totalPRs: 'pages.code.stats.totalPRs',
        acceptedPRs: 'pages.code.stats.acceptedPRs',
        linesAdded: 'pages.code.stats.linesAdded',
        linesRemoved: 'pages.code.stats.linesRemoved',
      },
      charts: {
        codeChangeTop: 'pages.code.charts.codeChangeTop',
        prAcceptanceRate: 'pages.code.charts.prAcceptanceRate',
        prReviewActivity: 'pages.code.charts.prReviewActivity',
      },
    },
    community: {
      title: 'pages.community.title',
      subtitle: 'pages.community.subtitle',
      stats: {
        totalAttention: 'pages.community.stats.totalAttention',
        totalStars: 'pages.community.stats.totalStars',
        totalForks: 'pages.community.stats.totalForks',
        totalParticipants: 'pages.community.stats.totalParticipants',
      },
      charts: {
        attentionRanking: 'pages.community.charts.attentionRanking',
        starForkRelationship: 'pages.community.charts.starForkRelationship',
        communityInteractionHeat: 'pages.community.charts.communityInteractionHeat',
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
