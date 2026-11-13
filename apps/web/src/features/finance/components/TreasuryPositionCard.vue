<template>
  <section class="card shadow-sm border-0 mb-4" data-testid="finance-treasury-position">
    <div class="card-body p-4">
      <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary-emphasis">
            {{ t('finance.exercise') }} {{ year }}
          </div>
          <h2 class="h5 fw-bold mb-1">{{ t('finance.treasuryPosition') }}</h2>
          <p class="small text-muted mb-0">{{ t('finance.treasuryPositionLead') }}</p>
          <p class="small text-muted mb-0">{{ t('finance.openingBalanceHint') }}</p>
        </div>
        <div class="d-flex flex-wrap gap-2 align-items-start">
          <button class="btn btn-outline-secondary btn-sm" type="button" :disabled="loading" @click="load">
            {{ t('common.refresh') }}
          </button>
          <button class="btn btn-outline-primary btn-sm" type="button" :disabled="exportingJournal" @click="exportJournal">
            <span v-if="exportingJournal" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            {{ t('finance.exportJournal') }}
          </button>
          <button
            v-if="canEdit && changedOpeningCount > 0"
            class="btn btn-primary btn-sm"
            type="button"
            :disabled="saving"
            @click="saveOpenings"
          >
            <span v-if="saving" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            {{ t('finance.saveOpeningBalances') }}
          </button>
        </div>
      </div>

      <div v-if="errorMessage" class="alert alert-warning border-0 shadow-sm mb-3" role="alert">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="alert alert-success border-0 shadow-sm mb-3" role="status">
        {{ successMessage }}
      </div>

      <div class="table-responsive">
        <table class="table table-sm align-middle mb-0">
          <thead>
            <tr>
              <th scope="col">{{ t('finance.account') }}</th>
              <th scope="col" class="text-end">{{ t('finance.openingBalance') }}</th>
              <th scope="col" class="text-end">{{ t('finance.inflow') }}</th>
              <th scope="col" class="text-end">{{ t('finance.outflow') }}</th>
              <th scope="col" class="text-end">{{ t('finance.custodyPending') }}</th>
              <th scope="col" class="text-end">{{ t('finance.closingBalance') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in position?.accounts ?? []" :key="row.account_id ?? 'unassigned'">
              <td class="fw-semibold">{{ row.name }}</td>
              <td class="text-end" style="min-width: 9rem">
                <input
                  v-if="canEdit && row.account_id"
                  v-model="openings[row.account_id]"
                  type="number"
                  step="0.01"
                  class="form-control form-control-sm text-end"
                  :aria-label="`${t('finance.openingBalance')} ${row.name}`"
                />
                <span v-else>{{ formatMoney(row.opening_balance) }}</span>
              </td>
              <td class="text-end text-success">{{ formatMoney(row.inflow) }}</td>
              <td class="text-end text-danger">{{ formatMoney(row.outflow) }}</td>
              <td class="text-end text-warning">{{ formatMoney(row.pending_custody) }}</td>
              <td class="text-end fw-semibold">{{ formatMoney(row.closing_balance) }}</td>
            </tr>
          </tbody>
          <tfoot v-if="position">
            <tr class="border-top">
              <th scope="row">{{ t('common.total') }}</th>
              <td class="text-end">{{ formatMoney(position.total_opening) }}</td>
              <td class="text-end">{{ formatMoney(position.total_inflow) }}</td>
              <td class="text-end">{{ formatMoney(position.total_outflow) }}</td>
              <td class="text-end">{{ formatMoney(position.total_pending_custody) }}</td>
              <td class="text-end fw-bold">{{ formatMoney(position.total_closing) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  exportFinanceJournal,
  getTreasuryPosition,
  listFinanceAccounts,
  setOpeningBalance,
  type TreasuryPositionResponse,
} from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import { useCsvExport } from '@/composables/useCsvExport'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'

const props = defineProps<{
  year: number
  canEdit?: boolean
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { formatMoney } = useFinanceFormatting()
const { exportCsv, exporting: exportingJournal } = useCsvExport()

const position = ref<TreasuryPositionResponse | null>(null)
const openings = ref<Record<string, string>>({})
const initialOpenings = ref<Record<string, string>>({})
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const changedOpeningCount = computed(() =>
  Object.keys(openings.value).filter(
    (accountId) => openings.value[accountId] !== initialOpenings.value[accountId],
  ).length,
)

async function load() {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await listFinanceAccounts()
    const data = await getTreasuryPosition(props.year)
    position.value = data
    const next: Record<string, string> = {}
    for (const row of data.accounts) {
      if (row.account_id) next[row.account_id] = row.opening_balance
    }
    openings.value = next
    initialOpenings.value = { ...next }
  } catch {
    errorMessage.value = t('finance.positionFailed')
  } finally {
    loading.value = false
  }
}

async function saveOpenings() {
  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    for (const accountId of Object.keys(openings.value)) {
      if (openings.value[accountId] === initialOpenings.value[accountId]) continue
      await setOpeningBalance(accountId, props.year, openings.value[accountId] || '0.00')
    }
    await load()
    successMessage.value = t('finance.positionSaved')
  } catch {
    errorMessage.value = t('finance.positionFailed')
  } finally {
    saving.value = false
  }
}

async function exportJournal() {
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await exportCsv(
      () => exportFinanceJournal(props.year),
      `journal-financier-${props.year}.csv`,
    )
  } catch {
    errorMessage.value = t('finance.journalExportFailed')
  }
}

watch(() => props.year, load)
onMounted(load)
</script>
