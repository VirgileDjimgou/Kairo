<template>
  <div class="error-state alert alert-warning border-0 shadow-sm" role="alert">
    <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
      <div>
        <div class="fw-semibold">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ title }}
        </div>
        <p v-if="message" class="small mb-0 mt-1">{{ message }}</p>
        <p v-if="recoveryHint" class="mb-0 small text-muted mt-1">{{ recoveryHint }}</p>
      </div>
      <button
        v-if="retryLabel"
        class="btn btn-outline-secondary btn-sm align-self-start"
        type="button"
        :disabled="retrying"
        @click="$emit('retry')"
      >
        <span v-if="retrying" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
        {{ retryLabel }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  message?: string
  recoveryHint?: string
  retryLabel?: string
  retrying?: boolean
}>()

defineEmits<{
  (e: 'retry'): void
}>()
</script>

<style scoped>
.error-state {
  border-radius: var(--om-radius-lg);
}
</style>
