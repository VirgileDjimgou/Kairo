<template>
  <div class="dropdown notification-bell">
    <button class="notification-bell__button" type="button" data-bs-toggle="dropdown" :aria-label="localeStore.t('notifications.label')" @click="refresh">
      <i class="bi bi-bell"></i>
      <span v-if="inbox.unread_count" class="notification-bell__badge">{{ inbox.unread_count > 99 ? '99+' : inbox.unread_count }}</span>
    </button>
    <div class="dropdown-menu dropdown-menu-end notification-bell__menu shadow">
      <div class="notification-bell__header">
        <strong>{{ localeStore.t('notifications.inbox') }}</strong>
        <button v-if="inbox.unread_count" class="btn btn-link btn-sm p-0" type="button" @click="markAllRead">{{ localeStore.t('notifications.markAllRead') }}</button>
      </div>
      <button class="btn btn-outline-primary btn-sm w-100 mb-2" type="button" @click="enablePush">{{ localeStore.t('notifications.enablePush') }}</button>
      <p class="notification-bell__push-help small text-muted mb-2">{{ localeStore.t('notifications.pushHelp') }}</p>
      <details class="notification-bell__preferences mb-2" @toggle="loadPreferences">
        <summary>{{ localeStore.t('notifications.preferences') }}</summary>
        <label v-for="category in categories" :key="category.key" class="form-check form-switch small mt-2">
          <input v-model="preferences[category.key]" class="form-check-input" type="checkbox" @change="savePreferences" />
          <span class="form-check-label">{{ localeStore.t(category.label) }}</span>
        </label>
      </details>
      <p v-if="!inbox.items.length" class="text-muted small mb-1">{{ localeStore.t('notifications.empty') }}</p>
      <button v-for="item in inbox.items" :key="item.id" class="notification-bell__item" :class="{ 'notification-bell__item--unread': !item.read_at }" type="button" @click="open(item)">
        <span>{{ notificationLabel(item.event_type) }}</span>
        <small>{{ formatDate(item.created_at) }}</small>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { getNotificationInbox, getNotificationPreferences, markAllNotificationsRead, markNotificationRead, updateNotificationPreferences, type InboxNotification, type NotificationPreferences } from '@/api/notifications.api'
import { enablePushForCurrentProfile, registerCurrentDevice } from '@/services/web-push'
import { useLocaleStore } from '@/stores/locale.store'

const router = useRouter()
const toast = useToast()
const localeStore = useLocaleStore()
const inbox = reactive({ items: [] as InboxNotification[], unread_count: 0 })
const preferences = reactive<NotificationPreferences>({ push_enabled: true, finance_enabled: true, discipline_enabled: true, announcements_enabled: true, events_enabled: true })
const categories: Array<{ key: Exclude<keyof NotificationPreferences, 'push_enabled'>; label: string }> = [
  { key: 'finance_enabled', label: 'notifications.preferenceFinance' },
  { key: 'discipline_enabled', label: 'notifications.preferenceDiscipline' },
  { key: 'announcements_enabled', label: 'notifications.preferenceAnnouncements' },
  { key: 'events_enabled', label: 'notifications.preferenceEvents' },
]
let timer: number | undefined

function notificationLabel(eventType: string): string {
  return localeStore.t(`notifications.${eventType}`) === `notifications.${eventType}`
    ? localeStore.t('notifications.generic')
    : localeStore.t(`notifications.${eventType}`)
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(localeStore.currentLocale, { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value))
}

async function refresh(): Promise<void> {
  try {
    const response = await getNotificationInbox()
    inbox.items = response.items
    inbox.unread_count = response.unread_count
  } catch {
    // The notification menu remains silent if a session is changing.
  }
}

async function markAllRead(): Promise<void> {
  await markAllNotificationsRead()
  await refresh()
}

async function open(item: InboxNotification): Promise<void> {
  if (!item.read_at) await markNotificationRead(item.id)
  await router.push(item.target_path)
  await refresh()
}

async function enablePush(): Promise<void> {
  try {
    const result = await enablePushForCurrentProfile()
    const key = result === 'enabled'
      ? 'notifications.pushEnabled'
      : result === 'denied'
        ? 'notifications.pushDenied'
        : result === 'not_configured'
          ? 'notifications.pushNotConfigured'
          : 'notifications.pushUnavailable'
    toast[result === 'enabled' ? 'success' : 'warning'](localeStore.t(key))
  } catch {
    toast.error(localeStore.t('notifications.pushUnavailable'))
  }
}

async function loadPreferences(event: Event): Promise<void> {
  if (!(event.target as HTMLDetailsElement).open) return
  try {
    Object.assign(preferences, await getNotificationPreferences())
  } catch {
    // A profile may not be registered yet while a session is being restored.
  }
}

async function savePreferences(): Promise<void> {
  try {
    Object.assign(preferences, await updateNotificationPreferences({ ...preferences }))
  } catch {
    toast.error(localeStore.t('notifications.preferencesSaveFailed'))
  }
}

onMounted(() => {
  void registerCurrentDevice().catch(() => undefined)
  void refresh()
  timer = window.setInterval(() => void refresh(), 30_000)
})

onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<style scoped>
.notification-bell { position: relative; }
.notification-bell__button { position: relative; display: inline-flex; width: 2.75rem; height: 2.75rem; align-items: center; justify-content: center; border: 1px solid var(--om-neutral-300); border-radius: var(--om-radius-base); background: var(--om-neutral-0); color: var(--om-primary); font-size: 1.1rem; }
.notification-bell__badge { position: absolute; top: -0.25rem; right: -0.25rem; min-width: 1.15rem; padding: 0.05rem 0.25rem; border-radius: 999px; background: #c93146; color: #fff; font-size: 0.65rem; font-weight: 700; }
.notification-bell__menu { width: min(24rem, calc(100vw - 2rem)); padding: 0.75rem; }
.notification-bell__header { display: flex; justify-content: space-between; gap: 0.75rem; align-items: center; margin-bottom: 0.75rem; }
.notification-bell__preferences { border-top: 1px solid var(--om-neutral-200); padding-top: 0.5rem; }
.notification-bell__push-help { line-height: 1.35; }
.notification-bell__preferences summary { cursor: pointer; color: var(--om-primary); font-size: 0.875rem; }
.notification-bell__item { display: flex; width: 100%; flex-direction: column; gap: 0.25rem; padding: 0.65rem; border: 0; border-top: 1px solid var(--om-neutral-200); background: transparent; color: inherit; text-align: left; }
.notification-bell__item--unread { background: #eef5ff; font-weight: 600; }
.notification-bell__item small { color: var(--om-neutral-600); font-weight: 400; }
</style>
