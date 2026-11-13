<template>
  <section class="card shadow-sm border-0 mb-4" data-testid="finance-expense-ledger">
    <div class="card-body p-4">
      <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary-emphasis">
            {{ t('finance.expenseKicker') }}
          </div>
          <h2 class="h5 fw-bold mb-1">{{ t('finance.expenseLedger') }}</h2>
          <p class="small text-muted mb-0">{{ t('finance.expenseLedgerLead') }}</p>
        </div>
        <div class="d-flex flex-wrap gap-2 align-items-start">
          <select v-model="selectedCategory" class="form-select form-select-sm" style="width: auto" @change="load">
            <option value="">{{ t('finance.allCategories') }}</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ expenseCategoryLabel(category) }}
            </option>
          </select>
          <button class="btn btn-outline-secondary btn-sm" type="button" :disabled="loading" @click="load">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            {{ t('common.refresh') }}
          </button>
          <button class="btn btn-outline-primary btn-sm" type="button" :disabled="exporting" @click="exportLedger('csv')">
            {{ t('common.exportCsv') }}
          </button>
          <button class="btn btn-outline-primary btn-sm" type="button" :disabled="exporting" @click="exportLedger('xlsx')">
            {{ t('finance.exportExcel') }}
          </button>
        </div>
      </div>

      <div v-if="errorMessage" class="alert alert-warning border-0 shadow-sm mb-3" role="alert">
        {{ errorMessage }}
      </div>
      <div v-if="uploadMessage" class="alert alert-success border-0 shadow-sm mb-3" role="status">
        {{ uploadMessage }}
      </div>

      <p v-if="!loading && rows.length === 0" class="text-muted small mb-0">
        {{ t('finance.noExpenses') }}
      </p>

      <div v-else class="table-responsive">
        <table class="table table-sm align-middle mb-0">
          <thead>
            <tr>
              <th scope="col">{{ t('finance.expenseDate') }}</th>
              <th scope="col">{{ t('finance.filterCategory') }}</th>
              <th scope="col">{{ t('finance.expensePayee') }}</th>
              <th scope="col">{{ t('finance.expenseDescription') }}</th>
              <th scope="col" class="text-end">{{ t('common.amount') }}</th>
              <th scope="col">{{ t('finance.attachment') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="expense in rows" :key="expense.id">
              <td class="text-nowrap">{{ formatDate(expense.spent_at) }}</td>
              <td>{{ expenseCategoryLabel(expense.category) }}</td>
              <td>{{ expense.payee || '—' }}</td>
              <td class="small">
                {{ expense.description }}
                <span class="badge ms-1" :class="expenseStatusClass(expense.status)">
                  {{ t(`finance.expenseStatus.${expense.status}`) }}
                </span>
                <span v-if="expense.reversed_at" class="badge text-bg-danger ms-1">
                  {{ t('finance.reversed') }}
                </span>
              </td>
              <td class="text-end text-nowrap fw-semibold">{{ formatMoney(expense.amount) }}</td>
              <td class="text-nowrap">
                <button
                  v-if="expense.attachment_file_name"
                  class="btn btn-link btn-sm p-0 me-2"
                  type="button"
                  :disabled="downloadingId === expense.id"
                  @click="downloadReceipt(expense)"
                >
                  {{ t('finance.downloadReceipt') }}
                </button>
                <span v-else class="small text-muted me-2">{{ t('finance.noAttachment') }}</span>
                <button
                  v-if="!readonly"
                  class="btn btn-outline-secondary btn-sm"
                  type="button"
                  :disabled="uploadingId === expense.id"
                  @click="chooseReceipt(expense)"
                >
                  {{ t('finance.attachReceipt') }}
                </button>
                <button
                  v-if="!readonly && !expense.reversed_at"
                  class="btn btn-outline-danger btn-sm ms-1"
                  type="button"
                  :disabled="reversingId === expense.id"
                  @click="reverseRow(expense)"
                >
                  {{ t('finance.reverseExpense') }}
                </button>
                <button
                  v-if="canApprove && !expense.reversed_at && expense.status === 'recorded'"
                  class="btn btn-outline-success btn-sm ms-1"
                  type="button"
                  :disabled="approvingId === expense.id"
                  @click="approveRow(expense)"
                >
                  {{ t('finance.approveExpense') }}
                </button>
                <button
                  v-if="canApprove && !expense.reversed_at && expense.status === 'recorded'"
                  class="btn btn-outline-danger btn-sm ms-1"
                  type="button"
                  :disabled="approvingId === expense.id"
                  @click="rejectRow(expense)"
                >
                  {{ t('finance.rejectExpense') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <input ref="fileInput" type="file" class="d-none" accept="application/pdf,image/jpeg,image/png" @change="onFileSelected" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  approveExpense,
  downloadExpenseAttachment,
  exportExpenses,
  rejectExpense,
  listExpenses,
  reverseExpense,
  uploadExpenseAttachment,
  type ExpenseRecordResponse,
  type TreasuryExpenseCategory,
} from '@/api/contributions.api'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import { useCsvExport } from '@/composables/useCsvExport'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'
import { useExpenseCategories } from '../composables/useExpenseCategories'

const props = defineProps<{
  year: number
  readonly?: boolean
}>()

const authStore = useAuthStore()
const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { expenseCategoryLabel, formatDate, formatMoney } = useFinanceFormatting()
const { ensureLoaded: ensureCategoriesLoaded } = useExpenseCategories()
const canApprove = computed(() => authStore.hasCapability('finance:expenses_approve'))
const { exportCsv, exporting } = useCsvExport()

const categories: TreasuryExpenseCategory[] = [
  'sport_equipment',
  'fuel_transport',
  'tournament',
  'cultural_event',
  'administration',
  'other',
]

const rows = ref<ExpenseRecordResponse[]>([])
const selectedCategory = ref<'' | TreasuryExpenseCategory>('')
const loading = ref(false)
const errorMessage = ref('')
const uploadMessage = ref('')
const downloadingId = ref('')
const uploadingId = ref('')
const reversingId = ref('')
const approvingId = ref('')
const uploadTargetId = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params: { year: number; limit: number; category?: TreasuryExpenseCategory } = {
      year: props.year,
      limit: 500,
    }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    rows.value = await listExpenses(params)
  } catch (error) {
    errorMessage.value = (error as { message?: string })?.message || t('finance.ledgerLoadFailed')
  } finally {
    loading.value = false
  }
}

async function exportLedger(format: 'csv' | 'xlsx') {
  await exportCsv(
    () => exportExpenses(props.year, format),
    `depenses-${props.year}.${format}`,
  )
}

async function downloadReceipt(expense: ExpenseRecordResponse) {
  downloadingId.value = expense.id
  try {
    const blob = await downloadExpenseAttachment(expense.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = expense.attachment_file_name || `receipt-${expense.id}`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch {
    errorMessage.value = t('finance.uploadFailed')
  } finally {
    downloadingId.value = ''
  }
}

function chooseReceipt(expense: ExpenseRecordResponse) {
  uploadTargetId.value = expense.id
  uploadMessage.value = ''
  fileInput.value?.click()
}

async function reverseRow(expense: ExpenseRecordResponse) {
  const reason = window.prompt(t('finance.reverseExpensePrompt'))
  if (reason === null || !reason.trim()) return
  reversingId.value = expense.id
  errorMessage.value = ''
  uploadMessage.value = ''
  try {
    const updated = await reverseExpense(expense.id, reason.trim())
    rows.value = rows.value.map((row) => (row.id === updated.id ? updated : row))
    uploadMessage.value = t('finance.expenseReversed')
  } catch (error) {
    errorMessage.value =
      (error as { message?: string })?.message || t('finance.expenseReverseFailed')
  } finally {
    reversingId.value = ''
  }
}

async function onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file || !uploadTargetId.value) return
  uploadingId.value = uploadTargetId.value
  errorMessage.value = ''
  try {
    const updated = await uploadExpenseAttachment(uploadTargetId.value, file)
    rows.value = rows.value.map((row) => (row.id === updated.id ? updated : row))
    uploadMessage.value = t('finance.receiptUploaded')
  } catch (error) {
    errorMessage.value =
      (error as { message?: string })?.message || t('finance.uploadFailed')
  } finally {
    uploadingId.value = ''
    uploadTargetId.value = ''
  }
}


function expenseStatusClass(status: string): string {
  if (status === 'approved') return 'text-bg-success'
  if (status === 'rejected') return 'text-bg-danger'
  return 'text-bg-secondary'
}

async function approveRow(expense: ExpenseRecordResponse) {
  approvingId.value = expense.id
  errorMessage.value = ''
  uploadMessage.value = ''
  try {
    const updated = await approveExpense(expense.id)
    rows.value = rows.value.map((row) => (row.id === updated.id ? updated : row))
    uploadMessage.value = t('finance.expenseApproved')
  } catch (error) {
    errorMessage.value =
      (error as { message?: string })?.message || t('finance.expenseApprovalFailed')
  } finally {
    approvingId.value = ''
  }
}

async function rejectRow(expense: ExpenseRecordResponse) {
  const note = window.prompt(t('finance.rejectExpensePrompt'))
  if (note === null || note.trim().length < 3) return
  approvingId.value = expense.id
  errorMessage.value = ''
  uploadMessage.value = ''
  try {
    const updated = await rejectExpense(expense.id, note.trim())
    rows.value = rows.value.map((row) => (row.id === updated.id ? updated : row))
    uploadMessage.value = t('finance.expenseRejected')
  } catch (error) {
    errorMessage.value =
      (error as { message?: string })?.message || t('finance.expenseApprovalFailed')
  } finally {
    approvingId.value = ''
  }
}

watch(() => props.year, load)
onMounted(() => {
  void ensureCategoriesLoaded()
  void load()
})

defineExpose({ reload: load })
</script>
