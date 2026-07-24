<template>
  <span
    class="status-badge"
    :class="`status-badge--${tone}`"
    role="status"
  >
    <span v-if="showDot" class="status-badge-dot"></span>
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'info'
  showDot?: boolean
}>()

const tone = computed(() => props.tone ?? 'neutral')
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1;
  padding: 0.375rem 0.625rem;
  border-radius: var(--om-radius-sm);
  letter-spacing: 0.01em;
  white-space: nowrap;
}

.status-badge--neutral {
  background: var(--om-neutral-100);
  color: var(--om-neutral-700);
}

.status-badge--success {
  background: var(--om-success-subtle);
  color: var(--om-success);
}

.status-badge--warning {
  background: var(--om-warning-subtle);
  color: var(--om-warning);
}

.status-badge--danger {
  background: var(--om-danger-subtle);
  color: var(--om-danger);
}

.status-badge--info {
  background: var(--om-info-subtle);
  color: var(--om-info);
}

.status-badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
</style>
