import { createRouter, createWebHistory } from 'vue-router'
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
      component: () => import('@/views/auth/MfaSetupView.vue'),
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
router.beforeEach((to) => {
  const auth = useAuthStore()
  const tenant = useTenantStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.requiresGuest && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  if (
    to.path.startsWith('/admin') &&
    auth.isAuthenticated &&
    auth.user &&
    !auth.hasRole('admin').value
  ) {
    return { name: 'dashboard' }
  }

  if (to.meta.module && !tenant.isModuleEnabled(to.meta.module as string)) {
    return { name: 'dashboard' }
  }
})

export default router
