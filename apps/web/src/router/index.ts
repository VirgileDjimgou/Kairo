import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

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
        },
        {
          path: 'members/profile',
          name: 'my-profile',
          component: () => import('@/views/members/MyProfileView.vue'),
        },
        {
          path: 'policies',
          name: 'policies',
          component: () => import('@/views/policies/PoliciesView.vue'),
        },
        {
          path: 'disciplinary',
          name: 'my-disciplinary',
          component: () => import('@/views/disciplinary/MyDisciplinaryView.vue'),
        },
        {
          path: 'events',
          name: 'events',
          component: () => import('@/views/events/EventsView.vue'),
        },
        {
          path: 'announcements',
          name: 'announcements',
          component: () => import('@/views/announcements/AnnouncementsView.vue'),
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
          path: 'documents',
          name: 'admin-documents',
          component: () => import('@/views/admin/AdminDocumentsView.vue'),
        },
        {
          path: 'chat-queries',
          name: 'admin-chat-queries',
          component: () => import('@/views/admin/AdminChatQueriesView.vue'),
        },
        {
          path: 'members',
          name: 'admin-members',
          component: () => import('@/views/members/AdminMembersView.vue'),
        },
        {
          path: 'contributions',
          name: 'admin-contributions',
          component: () => import('@/views/contributions/AdminContributionsView.vue'),
        },
        {
          path: 'policies',
          name: 'admin-policies',
          component: () => import('@/views/policies/AdminPoliciesView.vue'),
        },
        {
          path: 'disciplinary',
          name: 'admin-disciplinary',
          component: () => import('@/views/disciplinary/AdminDisciplinaryView.vue'),
        },
        {
          path: 'events',
          name: 'admin-events',
          component: () => import('@/views/events/AdminEventsView.vue'),
        },
        {
          path: 'announcements',
          name: 'admin-announcements',
          component: () => import('@/views/announcements/AdminAnnouncementsView.vue'),
        },
        {
          path: 'notifications',
          name: 'admin-notifications',
          component: () => import('@/views/admin/AdminNotificationsView.vue'),
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: () => import('@/views/admin/AdminSettingsView.vue'),
        },
      ],
    },
    // Future sprint routes are added here
    {
      path: '/:pathMatch(.*)*',
      redirect: '/dashboard',
    },
  ],
})

// Navigation guard
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.requiresGuest && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
