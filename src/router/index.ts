// src/router/index.ts 或相应路由文件
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        redirect: '/home'
    },
    {
    path: '/home',
    name: 'Home',
    component: ()=>import('@/views/mainLayout.vue'),
    children: [
      {
        path: '',
        redirect: 'home/overview'
      },
      {
        path: 'overview',
        name: 'showBoard',
        component: ()=>import('@/components/showBorad.vue'),
      },
      {
        path: 'activity',
        name: 'activity',
        component: ()=>import('@/views/ActivityAnalysis.vue'),
      },
      {
        path: 'impact',
        name: 'impact',
        component: ()=>import('@/views/ImpactAnalysis.vue'),
      },
      {
        path: 'contributor',
        name: 'contributor',
        component: ()=>import('@/views/ContributorEcosystem.vue'),
      },
      {
        path: 'issue',
        name: 'issue',
        component: ()=>import('@/views/IssueLifecycle.vue'),
      },
      {
        path: 'code',
        name: 'code',
        component: ()=>import('@/views/CodeChanges.vue'),
      },
      {
        path: 'community',
        name: 'community',
        component: ()=>import('@/views/CommunityAttention.vue'),
      },
      {
        path: 'prediction',
        name: 'prediction',
        component: ()=>import('@/views/Prediction.vue'),
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router