<template>
  <div class="empty-state" role="status">
    <div v-if="icon" class="empty-state-icon">
      <i :class="icon"></i>
    </div>
    <h3 class="empty-state-title">{{ title }}</h3>
    <p v-if="description" class="empty-state-description">{{ description }}</p>
    <button
      v-if="actionLabel && !actionTo"
      class="btn btn-primary"
      @click="$emit('action')"
    >
      {{ actionLabel }}
    </button>
    <RouterLink
      v-else-if="actionLabel && actionTo"
      :to="actionTo"
      class="btn btn-primary"
    >
      {{ actionLabel }}
    </RouterLink>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

defineProps<{
  title: string
  description?: string
  icon?: string
  actionLabel?: string
  actionTo?: string
}>()

defineEmits<{
  (e: 'action'): void
}>()
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1.5rem;
  min-height: 240px;
}

.empty-state-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--om-neutral-100);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--om-space-lg);
}

.empty-state-icon i {
  font-size: 1.75rem;
  color: var(--om-neutral-400);
}

.empty-state-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--om-neutral-800);
  margin: 0 0 var(--om-space-sm);
}

.empty-state-description {
  font-size: 0.9375rem;
  color: var(--om-neutral-500);
  margin: 0 0 var(--om-space-lg);
  max-width: 320px;
  line-height: 1.5;
}

.btn {
  font-size: 0.875rem;
  padding: 0.5rem 1.25rem;
  border-radius: var(--om-radius-base);
}
</style>
