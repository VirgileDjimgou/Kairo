<template>
  <div class="skeleton-loader" role="status" aria-label="Loading content">
    <div
      v-for="i in count"
      :key="i"
      class="skeleton-row"
    >
      <div
        v-for="(col, j) in columns"
        :key="j"
        class="om-skeleton"
        :style="{ width: col.width, height: col.height ?? '1rem' }"
      ></div>
    </div>
    <span class="visually-hidden">Loading...</span>
  </div>
</template>

<script setup lang="ts">
interface SkeletonColumn {
  width: string
  height?: string
}

withDefaults(defineProps<{
  count?: number
  columns?: SkeletonColumn[]
}>(), {
  count: 4,
  columns: () => [
    { width: '100%', height: '1rem' },
    { width: '60%', height: '0.875rem' },
  ],
})
</script>

<style scoped>
.skeleton-loader {
  display: flex;
  flex-direction: column;
  gap: var(--om-space-base);
  padding: var(--om-space-base) 0;
}

.skeleton-row {
  display: flex;
  flex-direction: column;
  gap: var(--om-space-sm);
  padding: var(--om-space-base);
  border: 1px solid var(--om-neutral-100);
  border-radius: var(--om-radius-lg);
  background: var(--om-neutral-0);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
