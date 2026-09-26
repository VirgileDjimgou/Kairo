<template>
  <div class="p-3 p-md-4 p-lg-5">
    <PageHeader
      :title="copy.title"
      :subtitle="copy.subtitle"
    />
    <section
      v-for="section in moreNavigation"
      :key="section.label"
      class="mb-4"
      :data-testid="`more-section-${section.label}`"
    >
      <SectionHeader :title="section.label" />
      <div class="row g-2 g-md-3">
        <div
          v-for="item in section.items"
          :key="item.to"
          class="col-12 col-md-6 col-xl-4"
        >
          <RouterLink
            :to="item.to"
            class="more-card card border-0 shadow-sm h-100 text-decoration-none"
          >
            <div class="card-body d-flex align-items-center gap-3">
              <span class="more-card-icon" aria-hidden="true">
                <i class="bi" :class="item.icon"></i>
              </span>
              <span class="more-card-label">{{ item.label }}</span>
            </div>
          </RouterLink>
        </div>
      </div>
    </section>
    <EmptyState
      v-if="!moreNavigation.length"
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
import { useRoleNavigation } from '@/composables/useRoleNavigation'
import { useLocaleStore } from '@/stores/locale.store'

const localeStore = useLocaleStore()
const { moreNavigation } = useRoleNavigation()

const copy = computed(() => ({
  title: localeStore.t('more.title'),
  subtitle: localeStore.t('more.subtitle'),
}))
</script>

<style scoped>
.more-card {
  border-radius: var(--om-radius-lg);
  transition: background-color var(--om-transition-fast), transform var(--om-transition-fast);
}

.more-card:hover {
  background: var(--om-neutral-50);
}

.more-card-icon {
  display: inline-grid;
  width: 2.5rem;
  height: 2.5rem;
  flex-shrink: 0;
  place-items: center;
  border-radius: var(--om-radius-base);
  background: var(--om-primary-subtle);
  color: var(--om-primary);
}

.more-card-icon i {
  font-size: 1.25rem;
}

.more-card-label {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--om-neutral-800);
}
</style>
