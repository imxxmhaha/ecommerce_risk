import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../stores/auth'

const routes = [
  { path: '/', component: { template: '<div />' } },
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  { path: '/risk-check', component: () => import('../views/RiskCheck.vue'), meta: { permission: 'risk:check' } },
  { path: '/rules', component: () => import('../views/RuleManage.vue'), meta: { permission: 'rule:write' } },
  { path: '/ai-rules', component: () => import('../views/AiRuleAssistant.vue'), meta: { permission: 'rule:ai' } },
  { path: '/cases', component: () => import('../views/CaseManage.vue'), meta: { permission: 'case:read' } },
  { path: '/cases/:caseId', component: () => import('../views/CaseDetail.vue'), meta: { permission: 'case:read' } },
  { path: '/blacklists', component: () => import('../views/BlacklistManage.vue'), meta: { permission: 'blacklist:read' } },
  { path: '/users/profile', component: () => import('../views/UserProfile.vue'), meta: { permission: 'profile:read' } },
  { path: '/dashboard', component: () => import('../views/Dashboard.vue'), meta: { permission: 'dashboard:read' } },
  { path: '/system/users', component: () => import('../views/SystemUsers.vue'), meta: { permission: 'system:user:read' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  if (to.meta.public) {
    if (authStore.token && to.path === '/login') {
      await authStore.loadMe().catch(() => null)
      return authStore.firstMenuPath()
    }
    return true
  }

  if (!authStore.token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  await authStore.loadMe().catch(() => {
    authStore.logout()
  })
  if (!authStore.token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (to.path === '/') {
    return authStore.firstMenuPath()
  }

  const permission = to.meta.permission as string | undefined
  if (!authStore.hasPermission(permission)) {
    return authStore.firstMenuPath()
  }
  return true
})

export default router
