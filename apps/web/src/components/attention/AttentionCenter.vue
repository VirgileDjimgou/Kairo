<template>
  <section class="attention-center mb-4" data-testid="attention-center">
    <SectionHeader :title="copy.title" />

    <ErrorState
      v-if="errorMessage"
      :title="copy.title"
      :message="errorMessage"
      :retry-label="copy.retry"
      :retrying="loading"
      @retry="load"
    />

    <EmptyState
      v-else-if="!loading && !items.length"
      icon="bi-check2-circle"
      :title="copy.empty"
      :description="copy.emptyHint"
    />

    <div v-else class="row g-2 g-md-3">
      <div
        v-for="item in items"
        :key="item.id"
        class="col-12 col-md-6 col-xl-4"
      >
        <RouterLink
          :to="item.target_path"
          class="attention-card card border-0 shadow-sm h-100 text-decoration-none"
          :data-testid="`attention-item-${item.id}`"
        >
          <div class="card-body d-flex align-items-start gap-3">
            <span class="attention-card-icon" aria-hidden="true">
              <i class="bi" :class="iconFor(item.category)"></i>
            </span>
            <span class="flex-grow-1">
              <span class="d-flex align-items-center gap-2 mb-1">
                <StatusBadge :label="copy.priorities[item.priority]" :tone="toneFor(item.priority)" />
                <span class="attention-card-count">{{ item.count }}</span>
              </span>
              <span class="attention-card-title">{{ titleFor(item) }}</span>
            </span>
            <i class="bi bi-chevron-right attention-card-chevron" aria-hidden="true"></i>
          </div>
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { getAttentionOverview, type AttentionItem, type AttentionPriority } from '@/api/attention.api'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()

const copy = computed(() => ({
  title: localeStore.t('attention.title'),
  empty: localeStore.t('attention.empty'),
  emptyHint: localeStore.t('attention.emptyHint'),
  retry: localeStore.t('common.retry'),
  priorities: {
    urgent: localeStore.t('attention.priority.urgent'),
    attention: localeStore.t('attention.priority.attention'),
    normal: localeStore.t('attention.priority.normal'),
    informational: localeStore.t('attention.priority.informational'),
  } as Record<AttentionPriority, string>,
}))

const items = ref<AttentionItem[]>([])
const loading = ref(false)
const errorMessage = ref('')

function toneFor(priority: AttentionPriority): 'danger' | 'warning' | 'info' | 'neutral' {
  if (priority === 'urgent') return 'danger'
  if (priority === 'attention') return 'warning'
  if (priority === 'normal') return 'info'
  return 'neutral'
}

function iconFor(category: AttentionItem['category']): string {
  if (category === 'finance') return 'bi-cash-coin'
  if (category === 'governance') return 'bi-diagram-3'
  if (category === 'community') return 'bi-megaphone'
  if (category === 'knowledge') return 'bi-file-earmark-text'
  return 'bi-person'
}

function titleFor(item: AttentionItem): string {
  const label = localeStore.t(item.title_key)
  return label === item.title_key ? item.id : label
}

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const overview = await getAttentionOverview()
    items.value = overview.items
  } catch {
    errorMessage.value = localeStore.t('common.recoveryHint')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.attention-card {
  border-radius: var(--om-radius-lg);
  transition: background-color var(--om-transition-fast);
}

.attention-card:hover {
  background: var(--om-neutral-50);
}

.attention-card-icon {
  display: inline-grid;
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  place-items: center;
  border-radius: var(--om-radius-base);
  background: var(--om-primary-subtle);
  color: var(--om-primary);
}

.attention-card-count {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--om-neutral-900);
}

.attention-card-title {
  display: block;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--om-neutral-800);
  line-height: 1.4;
}

.attention-card-chevron {
  color: var(--om-neutral-400);
  align-self: center;
}
</style>
