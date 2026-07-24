<template>
  <div class="responsive-data-view">
    <div v-if="$slots.header" class="responsive-data-view-header">
      <slot name="header" />
    </div>

    <div class="d-none d-lg-block">
      <div class="table-responsive">
        <table class="table align-middle" v-bind="$attrs">
          <thead v-if="$slots.thead">
            <slot name="thead" />
          </thead>
          <tbody>
            <slot name="rows" />
          </tbody>
        </table>
      </div>
    </div>

    <div class="d-lg-none">
      <div v-if="items.length" class="om-card-list">
        <div
          v-for="(item, i) in items"
          :key="i"
          class="om-card-list-item"
        >
          <slot name="card" :item="item" :index="i" />
        </div>
      </div>
      <slot v-else name="empty-mobile" />
    </div>

    <div v-if="$slots.footer" class="responsive-data-view-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: Record<string, unknown>[]
}>()
</script>

<style scoped>
.responsive-data-view {
  width: 100%;
}

.responsive-data-view-header {
  padding: 0 0 var(--om-space-base);
}

.responsive-data-view-footer {
  padding: var(--om-space-base) 0 0;
}

.table {
  margin-bottom: 0;
  font-size: 0.9375rem;
}

.table thead th {
  background: var(--om-neutral-50);
  border-bottom: 2px solid var(--om-neutral-200);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--om-neutral-500);
  padding: 0.625rem 0.75rem;
  white-space: nowrap;
}

.table tbody td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--om-neutral-100);
  color: var(--om-neutral-700);
  font-size: 0.875rem;
}

.table tbody tr:hover {
  background: var(--om-neutral-50);
}
</style>
