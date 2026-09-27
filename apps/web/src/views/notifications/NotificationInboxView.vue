<template>
  <div class="p-3 p-md-4 p-lg-5">
    <PageHeader :title="copy.title" :lead="copy.subtitle">
      <template #actions>
        <button
          v-if="items.length"
          class="btn btn-outline-secondary btn-sm"
          type="button"
          :disabled="loading"
          @click="markAllRead"
        >
          {{ copy.markAllRead }}
        </button>
      </template>
    </PageHeader>

    <ErrorState
      v-if="errorMessage"
      :title="copy.title"
      :message="errorMessage"
      :retry-label="copy.markAllRead"
      :retrying="loading"
      @retry="load"
    />

    <EmptyState
      v-else-if="!items.length"
      icon="bi-bell"
      :title="copy.title"
      :description="copy.empty"
    />

    <div v-else class="vstack gap-2">
      <button
        v-for="item in items"
        :key="item.id"
        class="inbox-item card border-0 shadow-sm text-start"
        :class="{ 'inbox-item--unread': !item.read_at }"
        type="button"
        @click="open(item)"
      >
        <div class="card-body d-flex align-items-start gap-3">
          <span class="inbox-item-icon" aria-hidden="true">
            <i class="bi" :class="iconFor(item.category)"></i>
          </span>
          <span class="flex-grow-1">
            <span class="d-block fw-semibold">{{ titleFor(item) }}</span>
            <span class="d-block small text-muted">{{ item.created_at }}</span>
          </span>
          <span v-if="!item.read_at" class="inbox-item-dot" aria-hidden="true"></span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/ui/PageHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import { useLocaleStore } from '@/stores/locale.store'
import {
  getNotificationInbox,
  markAllNotificationsRead,
  markNotificationRead,
  type InboxNotification,
} from '@/api/notifications.api'

const router = useRouter()
const localeStore = useLocaleStore()

const copy = computed(() => ({
  title: localeStore.t('notifications.inbox'),
  subtitle: localeStore.t('notifications.label'),
  markAllRead: localeStore.t('notifications.markAllRead'),
  empty: localeStore.t('notifications.empty'),
}))

const items = ref<InboxNotification[]>([])
const loading = ref(false)
const errorMessage = ref('')

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await getNotificationInbox()
    items.value = response.items
  } catch {
    errorMessage.value = localeStore.t('common.recoveryHint')
  } finally {
    loading.value = false
  }
}

async function markAllRead() {
  loading.value = true
  try {
    await markAllNotificationsRead()
    await load()
  } finally {
    loading.value = false
  }
}

async function open(item: InboxNotification) {
  if (!item.read_at) {
    await markNotificationRead(item.id)
    item.read_at = new Date().toISOString()
  }
  // Deep links are server-owned internal paths. Resolve them against the
  // authenticated router so unknown or external targets never navigate away.
  const target = safeInternalTarget(item.target_path)
  if (target) {
    await router.push(target)
  } else {
    await load()
  }
}

function safeInternalTarget(path: string | null | undefined): string | null {
  if (!path || !path.startsWith('/') || path.startsWith('//')) return null
  try {
    const resolved = router.resolve(path)
    if (!resolved.matched.length) return null
    if (resolved.name === 'not-found') return null
    return path
  } catch {
    return null
  }
}

function iconFor(category: string): string {
  if (category === 'finance') return 'bi-cash-coin'
  if (category === 'discipline') return 'bi-shield-lock'
  if (category === 'events') return 'bi-calendar-event'
  if (category === 'announcements') return 'bi-megaphone'
  return 'bi-bell'
}

function titleFor(item: InboxNotification): string {
  const key = `notifications.${item.event_type}`
  const label = localeStore.t(key)
  return label === key ? item.event_type : label
}

onMounted(load)
</script>

<style scoped>
.inbox-item {
  border-radius: var(--om-radius-lg);
  transition: background-color var(--om-transition-fast);
}

.inbox-item:hover {
  background: var(--om-neutral-50);
}

.inbox-item--unread {
  border-left: 3px solid var(--om-primary);
}

.inbox-item-icon {
  display: inline-grid;
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  place-items: center;
  border-radius: var(--om-radius-base);
  background: var(--om-primary-subtle);
  color: var(--om-primary);
}

.inbox-item-dot {
  width: 0.5rem;
  height: 0.5rem;
  margin-top: 0.375rem;
  border-radius: 50%;
  background: var(--om-primary);
}
</style>
