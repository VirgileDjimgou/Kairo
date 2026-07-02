import { createRouter, createWebHistory } from 'vue-router'
import { nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useTenantStore } from '@/stores/tenant.store'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('@/views/auth/ForgotPasswordView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('@/views/auth/ResetPasswordView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/accept-invite',
      name: 'accept-invite',
      component: () => import('@/views/auth/AcceptInviteView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/mfa/setup',
      name: 'mfa-setup',
      redirect: '/account/security',
      meta: { requiresAuth: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/dashboard',
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
        },
        {
          path: 'chat',
          name: 'chat',
          component: () => import('@/views/chat/ChatView.vue'),
          meta: { module: 'chat' },
        },
        {
          path: 'members/profile',
          name: 'my-profile',
          component: () => import('@/views/members/MyProfileView.vue'),
          meta: { module: 'membership' },
        },
        {
          path: 'account/security',
          name: 'account-security',
          component: () => import('@/views/account/AccountSecurityView.vue'),
        },
        {
          path: 'policies',
          name: 'policies',
          component: () => import('@/views/policies/PoliciesView.vue'),
          meta: { module: 'policies' },
        },
        {
          path: 'disciplinary',
          name: 'my-disciplinary',
          component: () => import('@/views/disciplinary/MyDisciplinaryView.vue'),
          meta: { module: 'disciplinary' },
        },
        {
          path: 'censor',
          name: 'censor-workspace',
          component: () => import('@/views/disciplinary/CensorWorkspaceView.vue'),
          meta: {
            module: 'disciplinary',
            allowedRoles: ['censor', 'president', 'principal_admin', 'admin'],
          },
        },
        {
          path: 'sports',
          name: 'sports-workspace',
          component: () => import('@/views/sports/SportsWorkspaceView.vue'),
          meta: {
            module: 'events',
            allowedRoles: ['sports_manager', 'principal_admin', 'admin'],
          },
        },
        {
          path: 'governance',
          name: 'governance-cockpit',
          component: () => import('@/views/governance/GovernanceCockpitView.vue'),
          meta: {
            allowedRoles: ['president', 'vice_president', 'principal_admin', 'admin'],
          },
        },
        {
          path: 'events',
          name: 'events',
          component: () => import('@/views/events/EventsView.vue'),
          meta: { module: 'events' },
        },
        {
          path: 'announcements',
          name: 'announcements',
          component: () => import('@/views/announcements/AnnouncementsView.vue'),
          meta: { module: 'announcements' },
        },
        {
          path: 'finance',
          name: 'finance-workspace',
          component: () => import('@/views/finance/FinanceWorkspaceView.vue'),
          meta: { requiresFinanceWorkspace: true },
        },
        {
          path: 'finance-audit',
          name: 'finance-audit-workspace',
          component: () => import('@/views/finance/AuditorFinanceView.vue'),
          meta: {
            requiresAuth: true,
            allowedRoles: ['auditor', 'president', 'principal_admin', 'admin'],
          },
        },
        {
          path: 'secretary',
          component: () => import('@/layouts/SecretaryLayout.vue'),
          meta: {
            requiresAuth: true,
            allowedRoles: ['secretary_general', 'principal_admin', 'admin'],
          },
          children: [
            {
              path: '',
              name: 'secretary-overview',
              component: () => import('@/views/secretary/SecretaryOverviewView.vue'),
            },
            {
              path: 'documents',
              name: 'secretary-documents',
              component: () => import('@/views/admin/AdminDocumentsView.vue'),
            },
            {
              path: 'policies',
              name: 'secretary-policies',
              component: () => import('@/views/policies/AdminPoliciesView.vue'),
              meta: { module: 'policies' },
            },
            {
              path: 'announcements',
              name: 'secretary-announcements',
              component: () => import('@/views/announcements/AdminAnnouncementsView.vue'),
              meta: { module: 'announcements' },
            },
          ],
        },
      ],
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'admin-overview',
          component: () => import('@/views/admin/AdminOverviewView.vue'),
        },
        {
          path: 'access',
          name: 'admin-access',
          component: () => import('@/views/admin/AdminAccessView.vue'),
        },
        {
          path: 'documents',
          name: 'admin-documents',
          component: () => import('@/views/admin/AdminDocumentsView.vue'),
        },
        {
          path: 'chat-queries',
          name: 'admin-chat-queries',
          component: () => import('@/views/admin/AdminChatQueriesView.vue'),
          meta: { module: 'chat' },
        },
        {
          path: 'audit',
          name: 'admin-audit-trail',
          component: () => import('@/views/admin/AuditTrailView.vue'),
        },
        {
          path: 'members',
          name: 'admin-members',
          component: () => import('@/views/members/AdminMembersView.vue'),
          meta: { module: 'membership' },
        },
        {
          path: 'contributions',
          name: 'admin-contributions',
          component: () => import('@/views/contributions/AdminContributionsView.vue'),
          meta: { module: 'contributions' },
        },
        {
          path: 'policies',
          name: 'admin-policies',
          component: () => import('@/views/policies/AdminPoliciesView.vue'),
          meta: { module: 'policies' },
        },
        {
          path: 'disciplinary',
          name: 'admin-disciplinary',
          component: () => import('@/views/disciplinary/AdminDisciplinaryView.vue'),
          meta: { module: 'disciplinary' },
        },
        {
          path: 'events',
          name: 'admin-events',
          component: () => import('@/views/events/AdminEventsView.vue'),
          meta: { module: 'events' },
        },
        {
          path: 'announcements',
          name: 'admin-announcements',
          component: () => import('@/views/announcements/AdminAnnouncementsView.vue'),
          meta: { module: 'announcements' },
        },
        {
          path: 'notifications',
          name: 'admin-notifications',
          component: () => import('@/views/admin/AdminNotificationsView.vue'),
          meta: { module: 'notifications' },
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: () => import('@/views/admin/AdminSettingsView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard',
    },
  ],
})

// Navigation guard
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const tenant = useTenantStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if ((auth.isAuthenticated || localStorage.getItem('access_token')) && !auth.user) {
    await auth.restoreSession()
    await nextTick()
  }

  const currentRoles = auth.user?.roles ?? []

  if (to.meta.requiresGuest && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  if (
    to.path.startsWith('/admin') &&
    auth.isAuthenticated &&
    auth.user &&
    !currentRoles.some((role) => ['admin', 'principal_admin'].includes(role))
  ) {
    return { name: 'dashboard' }
  }

  if (to.meta.allowedRoles && auth.isAuthenticated && auth.user) {
    const allowedRoles = to.meta.allowedRoles as string[]
    const hasAllowedRole = allowedRoles.some((role) => currentRoles.includes(role))
    if (!hasAllowedRole) {
      return { name: 'dashboard' }
    }
  }

  if (
    to.meta.requiresFinanceWorkspace &&
    auth.isAuthenticated &&
    auth.user &&
    !['admin', 'treasurer', 'principal_admin'].some((role) => currentRoles.includes(role))
  ) {
    return { name: 'dashboard' }
  }

  if (
    to.meta.requiresFinanceWorkspace &&
    (!tenant.isModuleEnabled('membership') || !tenant.isModuleEnabled('contributions'))
  ) {
    return { name: 'dashboard' }
  }

  if (to.meta.module && !tenant.isModuleEnabled(to.meta.module as string)) {
    return { name: 'dashboard' }
  }
})

export default router
