<template>
  <div class="success-state alert alert-success border-0 shadow-sm" role="status">
    <div class="d-flex align-items-start gap-2">
      <i class="bi bi-check-circle-fill mt-1" aria-hidden="true"></i>
      <div>
        <div class="fw-semibold">{{ title }}</div>
        <p v-if="message" class="small mb-0 mt-1">{{ message }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  message?: string
}>()
</script>

<style scoped>
.success-state {
  border-radius: var(--om-radius-lg);
}
</style>
