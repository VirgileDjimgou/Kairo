<template>
  <div class="section-header mb-3">
    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-end gap-2">
      <div>
        <div v-if="kicker" class="section-header-kicker">{{ kicker }}</div>
        <h2 class="section-header-title mb-0">{{ title }}</h2>
      </div>
      <slot name="actions" />
    </div>
    <p v-if="description" class="section-header-description mb-0 mt-2">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  kicker?: string
  description?: string
}>()
</script>

<style scoped>
.section-header-kicker {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--om-neutral-500);
  margin-bottom: var(--om-space-xs);
}

.section-header-title {
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.25;
  color: var(--om-neutral-800);
}

.section-header-description {
  font-size: 0.9375rem;
  color: var(--om-neutral-500);
  max-width: 70ch;
}
</style>
