<template>
  <div class="p-3 p-md-4 p-lg-5">
    <PageHeader :title="copy.title" :subtitle="copy.subtitle" />
    <AttentionCenter />
    <section
      v-for="group in taskGroups"
      :key="group.label"
      class="mb-4"
    >
      <SectionHeader :title="group.label" />
      <div class="row g-2 g-md-3">
        <div
          v-for="item in group.items"
          :key="item.to"
          class="col-12 col-md-6 col-xl-4"
        >
          <div class="task-card card border-0 shadow-sm h-100">
            <div class="card-body d-flex flex-column gap-2">
              <div class="d-flex align-items-center gap-2">
                <span class="task-card-icon" aria-hidden="true">
                  <i class="bi" :class="item.icon"></i>
                </span>
                <h3 class="task-card-title mb-0">{{ item.label }}</h3>
              </div>
              <p class="task-card-description mb-0">{{ describe(item.to) }}</p>
              <RouterLink :to="item.to" class="btn btn-outline-primary btn-sm align-self-start mt-2">
                {{ copy.open }}
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </section>
    <EmptyState
      v-if="!taskGroups.length"
      :title="copy.title"
      :description="copy.subtitle"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import AttentionCenter from '@/components/attention/AttentionCenter.vue'
import { useRoleNavigation } from '@/composables/useRoleNavigation'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()
const { moreNavigation } = useRoleNavigation()

const copy = computed(() => ({
  title: localeStore.t('tasks.title'),
  subtitle: localeStore.t('tasks.subtitle'),
  open: localeStore.t('tasks.open'),
}))

// Task cards surface the workspaces where pending work lives (management and
// governance). Community reading and account surfaces stay in the More catalog.
const taskGroups = computed(() =>
  moreNavigation.value.filter(
    (section) => section.label === localeStore.t('more.management')
      || section.label === localeStore.t('more.governance'),
  ),
)

const descriptionKeys: Record<string, string> = {
  '/finance': 'tasks.desc.finance',
  '/receipts': 'tasks.desc.receipts',
  '/members/manage': 'tasks.desc.members',
  '/secretary': 'tasks.desc.secretary',
  '/censor': 'tasks.desc.discipline',
  '/governance': 'tasks.desc.governance',
  '/finance-audit': 'tasks.desc.financeAudit',
  '/sports': 'tasks.desc.sports',
  '/operation-journal': 'tasks.desc.journal',
  '/recovery': 'tasks.desc.recovery',
  '/admin': 'tasks.desc.admin',
}

function describe(to: string): string {
  const exact = descriptionKeys[to]
  if (exact) return localeStore.t(exact)
  const parent = Object.keys(descriptionKeys)
    .filter((route) => to.startsWith(`${route}/`))
    .sort((a, b) => b.length - a.length)[0]
  return localeStore.t(
    parent ? (descriptionKeys[parent] ?? 'tasks.desc.default') : 'tasks.desc.default',
  )
}
</script>

<style scoped>
.task-card {
  border-radius: var(--om-radius-lg);
}

.task-card-icon {
  display: inline-grid;
  width: 2.25rem;
  height: 2.25rem;
  flex-shrink: 0;
  place-items: center;
  border-radius: var(--om-radius-base);
  background: var(--om-primary-subtle);
  color: var(--om-primary);
}

.task-card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--om-neutral-800);
}

.task-card-description {
  font-size: 0.875rem;
  color: var(--om-neutral-500);
  line-height: 1.5;
}
</style>
