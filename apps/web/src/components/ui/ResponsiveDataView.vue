<template>
  <div class="responsive-data-view">
    <div v-if="$slots.header" class="responsive-data-view-header">
      <slot name="header" />
    </div>

    <div class="desktop-data-table">
      <div class="table-responsive">
        <table class="table align-middle" v-bind="$attrs">
          <thead v-if="$slots.thead">
            <slot name="thead" />
          </thead>
          <tbody>
            <slot name="desktop-row">
              <slot name="rows" />
            </slot>
          </tbody>
        </table>
      </div>
    </div>

    <section class="mobile-data-list" :aria-label="mobileAriaLabel">
      <div v-if="items.length" class="om-card-list">
        <article
          v-for="(item, i) in items"
          :key="itemKey ? itemKey(item, i) : i"
          class="mobile-data-card om-card-list-item"
        >
          <slot name="card" :item="item" :index="i">
            <header v-if="$slots['mobile-title'] || $slots['mobile-status']" class="mobile-data-card__header">
              <div class="mobile-data-card__identity">
                <slot name="mobile-title" :item="item" :index="i" />
              </div>
              <div v-if="$slots['mobile-status']" class="mobile-data-card__status">
                <slot name="mobile-status" :item="item" :index="i" />
              </div>
            </header>
            <div v-if="$slots['mobile-fields']" class="mobile-data-card__fields">
              <slot name="mobile-fields" :item="item" :index="i" />
            </div>
            <footer v-if="$slots['mobile-actions']" class="mobile-data-card__actions">
              <slot name="mobile-actions" :item="item" :index="i" />
            </footer>
          </slot>
        </article>
      </div>
      <slot v-else name="empty-mobile" />
    </section>

    <div v-if="$slots.footer" class="responsive-data-view-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts" generic="T extends object">
defineProps<{
  items: T[]
  itemKey?: (item: T, index: number) => string | number
  mobileAriaLabel?: string
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

.desktop-data-table {
  display: none;
}

.mobile-data-list {
  display: block;
}

.mobile-data-card {
  overflow-wrap: break-word;
  word-break: normal;
  hyphens: auto;
}

.mobile-data-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--om-space-sm);
  margin-bottom: var(--om-space-base);
}

.mobile-data-card__identity {
  min-width: 0;
  font-weight: 650;
}

.mobile-data-card__status {
  flex: 0 0 auto;
}

.mobile-data-card__fields {
  display: grid;
  gap: var(--om-space-sm);
}

.mobile-data-card__actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(9rem, 100%), 1fr));
  gap: var(--om-space-sm);
  margin-top: var(--om-space-base);
  padding-top: var(--om-space-base);
  border-top: 1px solid var(--om-neutral-100);
}

.mobile-data-card__actions :deep(.btn) {
  min-height: 44px;
  width: 100%;
  white-space: normal;
}

@media (min-width: 768px) {
  .desktop-data-table {
    display: block;
  }

  .mobile-data-list {
    display: none;
  }
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
