<template>
  <div class="metric-card card border-0 shadow-sm h-100">
    <div class="card-body">
      <div class="metric-card-label">{{ label }}</div>
      <div class="metric-card-value" :class="`metric-card-value--${tone}`">{{ value }}</div>
      <div v-if="hint" class="metric-card-hint">{{ hint }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  value: string
  hint?: string
  tone?: 'neutral' | 'positive' | 'attention' | 'critical' | 'info'
}>()

const tone = computed(() => props.tone ?? 'neutral')
</script>

<style scoped>
.metric-card {
  border-radius: var(--om-radius-lg);
}

.metric-card-label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--om-neutral-500);
  margin-bottom: var(--om-space-xs);
}

.metric-card-value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--om-neutral-900);
}

.metric-card-value--positive {
  color: var(--om-success);
}

.metric-card-value--attention {
  color: var(--om-warning);
}

.metric-card-value--critical {
  color: var(--om-danger);
}

.metric-card-value--info {
  color: var(--om-info);
}

.metric-card-hint {
  font-size: 0.75rem;
  color: var(--om-neutral-500);
  margin-top: var(--om-space-xs);
}
</style>
