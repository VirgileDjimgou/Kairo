<template>
  <div class="finance-actions">
    <select v-model.number="selectedYear" class="form-select form-select-sm" style="width: auto">
      <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
    </select>
    <button class="btn btn-outline-secondary btn-sm" type="button" @click="emit('refresh')" :disabled="loading">
      <span v-if="loading" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
      {{ t('common.refresh') }}
    </button>
    <button class="btn btn-outline-primary btn-sm" type="button" @click="emit('export', 'xlsx')" :disabled="exporting">{{ t('finance.exportExcel') }}</button>
    <button class="btn btn-outline-primary btn-sm" type="button" @click="emit('export', 'pdf')" :disabled="exporting">{{ t('finance.exportPdf') }}</button>
    <button class="btn btn-outline-success btn-sm" type="button" @click="emit('share-whatsapp')" :disabled="exporting">{{ t('finance.copyForWhatsapp') }}</button>
  </div>
</template>

<script setup lang="ts">
import { useLocaleStore } from '@/stores/locale.store'

defineProps<{
  years: number[]
  loading: boolean
  exporting: boolean
}>()

const emit = defineEmits<{
  refresh: []
  export: [format: 'xlsx' | 'pdf']
  'share-whatsapp': []
}>()

const selectedYear = defineModel<number>('selectedYear', { required: true })

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
</script>

<style scoped>
.finance-actions {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.finance-actions .btn,
.finance-actions .form-select {
  min-height: 44px;
}

@media (max-width: 767.98px) {
  .finance-actions {
    display: grid;
    width: 100%;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .finance-actions .form-select,
  .finance-actions .btn {
    width: 100% !important;
  }

  .finance-actions .btn {
    white-space: normal;
  }

  .finance-actions .btn-outline-primary,
  .finance-actions .btn-outline-success {
    grid-column: 1 / -1;
  }
}
</style>
