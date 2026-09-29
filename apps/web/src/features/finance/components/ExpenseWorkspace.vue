<template>
  <section class="row g-4 mb-4" data-testid="finance-expense-workspace">
    <div class="col-xl-5">
      <div class="card shadow-sm border-0 expense-entry-card h-100"><div class="card-body p-4">
        <div class="text-uppercase small fw-semibold text-danger mb-1">{{ t('finance.expenseKicker') }}</div>
        <h2 class="h5 fw-bold mb-1">{{ t('finance.expenseTitle') }}</h2><p class="small text-muted mb-4">{{ t('finance.expenseLead') }}</p>
        <form class="row g-3" @submit.prevent="submitExpense">
          <div class="col-md-7"><label for="expense-category" class="form-label small fw-medium">{{ t('finance.expenseCategory') }}</label><select id="expense-category" v-model="form.category" class="form-select" required><option v-for="category in categories" :key="category" :value="category">{{ expenseCategoryLabel(category) }}</option></select></div>
          <div class="col-md-5"><label for="expense-amount" class="form-label small fw-medium">{{ t('common.amount') }} (EUR)</label><input id="expense-amount" v-model="form.amount" class="form-control" type="number" min="0.01" step="0.01" required /></div>
          <div class="col-md-6"><label for="expense-date" class="form-label small fw-medium">{{ t('finance.expenseDate') }}</label><input id="expense-date" v-model="form.spent_at" class="form-control" type="date" required /></div>
          <div class="col-md-6"><label for="expense-method" class="form-label small fw-medium">{{ t('contributions.paymentMethod') }}</label><select id="expense-method" v-model="form.payment_method" class="form-select"><option value="cash">{{ t('contributions.cash') }}</option><option value="bank_transfer">{{ t('contributions.bankTransfer') }}</option><option value="card">{{ t('finance.card') }}</option><option value="check">{{ t('contributions.check') }}</option><option value="other">{{ t('finance.other') }}</option></select></div>
          <div class="col-12"><label for="expense-payee" class="form-label small fw-medium">{{ t('finance.expensePayee') }}</label><input id="expense-payee" v-model.trim="form.payee" class="form-control" /></div>
          <div class="col-12"><label for="expense-description" class="form-label small fw-medium">{{ t('finance.expenseDescription') }}</label><textarea id="expense-description" v-model.trim="form.description" class="form-control" rows="3" :placeholder="t('finance.expenseDescriptionPlaceholder')" required></textarea></div>
          <div class="col-12"><label for="expense-reference" class="form-label small fw-medium">{{ t('finance.expenseReference') }}</label><input id="expense-reference" v-model.trim="form.reference" class="form-control" /></div>
          <div class="col-12 d-grid"><button class="btn btn-danger" type="submit" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>{{ saving ? t('common.saving') : t('finance.recordExpense') }}</button></div>
        </form>
      </div></div>
    </div>
    <div class="col-xl-7">
      <div class="card shadow-sm border-0 recent-expenses-card h-100"><div class="card-body p-4">
        <div class="d-flex align-items-center justify-content-between gap-2 mb-3"><div><div class="text-uppercase small fw-semibold text-secondary-emphasis">{{ t('finance.expenseKicker') }}</div><h2 class="h5 fw-bold mb-0">{{ t('finance.recentExpenses') }}</h2></div><span class="badge text-bg-light border text-dark">{{ budget?.recent_expenses.length || 0 }}</span></div>
        <p v-if="!budget || budget.recent_expenses.length === 0" class="text-muted small mb-0">{{ t('finance.noExpenses') }}</p>
        <div v-else class="vstack gap-2"><article v-for="expense in budget.recent_expenses" :key="expense.id" class="recent-expense-item"><div class="expense-category-icon"><i class="bi bi-arrow-up-right"></i></div><div class="flex-grow-1 min-w-0"><div class="d-flex flex-wrap justify-content-between gap-2"><strong>{{ expenseCategoryLabel(expense.category) }}</strong><strong class="text-danger">− {{ formatMoney(expense.amount) }}</strong></div><div class="small text-muted text-truncate">{{ expense.description }}</div><div class="small text-secondary mt-1">{{ formatDate(expense.spent_at) }}<span v-if="expense.payee"> · {{ expense.payee }}</span></div></div></article></div>
      </div></div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { AnnualBudgetResponse, TreasuryExpenseCategory } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import type { ExpenseInput } from '../composables/useFinanceWorkspace'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'

const props = defineProps<{
  budget: AnnualBudgetResponse | null
  categories: TreasuryExpenseCategory[]
  saving: boolean
  resetToken: number
}>()

const emit = defineEmits<{ submit: [payload: ExpenseInput] }>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { expenseCategoryLabel, formatMoney, formatDate } = useFinanceFormatting()

function defaultForm() {
  return {
    category: 'sport_equipment' as TreasuryExpenseCategory,
    amount: '',
    spent_at: new Date().toISOString().slice(0, 10),
    description: '',
    payee: '',
    payment_method: 'cash',
    reference: '',
  }
}

const form = ref(defaultForm())

function resetForm() {
  form.value = defaultForm()
}

function submitExpense() {
  emit('submit', { ...form.value })
}

watch(() => props.resetToken, resetForm)
</script>

<style scoped>
.expense-entry-card { border-top: 4px solid #d33a4c !important; background: linear-gradient(150deg, #fff 0%, #fff8f8 100%); }
.recent-expenses-card { border-top: 4px solid #e88924 !important; }
.recent-expense-item { display: flex; gap: 0.8rem; align-items: flex-start; padding: 0.85rem; border: 1px solid #e7eaf0; border-radius: 0.85rem; background: #fff; }
.expense-category-icon { display: grid; place-items: center; flex: 0 0 2.25rem; width: 2.25rem; height: 2.25rem; border-radius: 0.75rem; background: #fff0f1; color: #c92f42; }
</style>
