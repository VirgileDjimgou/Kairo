<template>
  <section class="card shadow-sm border-0 mb-4" data-testid="finance-budget-plan">
    <div class="card-body p-4">
      <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary-emphasis">
            {{ t('finance.exercise') }} {{ year }}
          </div>
          <h2 class="h5 fw-bold mb-1">{{ t('finance.plannedBudget') }}</h2>
          <p class="small text-muted mb-0">{{ t('finance.plannedBudgetLead') }}</p>
        </div>
        <div class="d-flex flex-wrap gap-2 align-items-start">
          <button class="btn btn-outline-secondary btn-sm" type="button" :disabled="loading" @click="load">
            {{ t('common.refresh') }}
          </button>
          <button
            v-if="canEdit"
            class="btn btn-primary btn-sm"
            type="button"
            :disabled="saving"
            @click="save"
          >
            <span v-if="saving" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            {{ t('finance.saveBudgetPlan') }}
          </button>
        </div>
      </div>

      <div v-if="errorMessage" class="alert alert-warning border-0 shadow-sm mb-3" role="alert">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="alert alert-success border-0 shadow-sm mb-3" role="status">
        {{ successMessage }}
      </div>

      <div class="row g-4">
        <div class="col-lg-6">
          <h3 class="h6 fw-bold">{{ t('finance.incomeBreakdown') }}</h3>
          <div class="vstack gap-2">
            <div v-for="line in incomeLines" :key="line.category" class="d-flex align-items-center gap-2">
              <label class="flex-grow-1 small mb-0" :for="`plan-income-${line.category}`">
                {{ incomeCategoryLabel(line.category) }}
              </label>
              <input
                v-if="canEdit"
                :id="`plan-income-${line.category}`"
                v-model="editable[`income:${line.category}`]"
                type="number"
                min="0"
                step="0.01"
                class="form-control form-control-sm text-end"
                style="max-width: 9rem"
              />
              <span v-else class="fw-semibold">{{ formatMoney(line.planned_amount) }}</span>
            </div>
          </div>
          <div class="d-flex justify-content-between border-top mt-3 pt-2 fw-bold">
            <span>{{ t('finance.plannedIncome') }}</span>
            <span>{{ formatMoney(plannedIncomeTotal) }}</span>
          </div>
        </div>

        <div class="col-lg-6">
          <h3 class="h6 fw-bold">{{ t('finance.expenseBreakdown') }}</h3>
          <div class="vstack gap-2">
            <div v-for="line in expenseLines" :key="line.category" class="d-flex align-items-center gap-2">
              <label class="flex-grow-1 small mb-0" :for="`plan-expense-${line.category}`">
                {{ expenseCategoryLabel(line.category) }}
              </label>
              <input
                v-if="canEdit"
                :id="`plan-expense-${line.category}`"
                v-model="editable[`expense:${line.category}`]"
                type="number"
                min="0"
                step="0.01"
                class="form-control form-control-sm text-end"
                style="max-width: 9rem"
              />
              <span v-else class="fw-semibold">{{ formatMoney(line.planned_amount) }}</span>
            </div>
          </div>
          <div class="d-flex justify-content-between border-top mt-3 pt-2 fw-bold">
            <span>{{ t('finance.plannedExpense') }}</span>
            <span>{{ formatMoney(plannedExpenseTotal) }}</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  getBudgetPlan,
  setBudgetPlan,
  type BudgetPlanLine,
} from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import { useFinanceFormatting } from '../composables/useFinanceFormatting'
import { useExpenseCategories } from '../composables/useExpenseCategories'

const props = defineProps<{
  year: number
  canEdit?: boolean
}>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { formatMoney, incomeCategoryLabel, expenseCategoryLabel } = useFinanceFormatting()
const { ensureLoaded: ensureCategoriesLoaded } = useExpenseCategories()

const lines = ref<BudgetPlanLine[]>([])
const editable = ref<Record<string, string>>({})
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const incomeLines = computed(() => lines.value.filter((line) => line.direction === 'income'))
const expenseLines = computed(() => lines.value.filter((line) => line.direction === 'expense'))

const plannedIncomeTotal = computed(() =>
  sumDirection('income'),
)
const plannedExpenseTotal = computed(() =>
  sumDirection('expense'),
)

function sumDirection(direction: 'income' | 'expense'): string {
  return incomeLines.value
    .concat(expenseLines.value)
    .filter((line) => line.direction === direction)
    .reduce((total, line) => {
      const value = editable.value[`${line.direction}:${line.category}`] ?? line.planned_amount
      return total + Number(value || 0)
    }, 0)
    .toFixed(2)
}

async function load() {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const plan = await getBudgetPlan(props.year)
    lines.value = plan.lines
    const next: Record<string, string> = {}
    for (const line of plan.lines) {
      next[`${line.direction}:${line.category}`] = line.planned_amount
    }
    editable.value = next
  } catch {
    errorMessage.value = t('finance.budgetPlanFailed')
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const payload: BudgetPlanLine[] = lines.value.map((line) => ({
      direction: line.direction,
      category: line.category,
      planned_amount: editable.value[`${line.direction}:${line.category}`] || '0.00',
    }))
    await setBudgetPlan(props.year, payload)
    await load()
    successMessage.value = t('finance.budgetPlanSaved')
  } catch {
    errorMessage.value = t('finance.budgetPlanFailed')
  } finally {
    saving.value = false
  }
}

watch(() => props.year, load)
onMounted(() => {
  void ensureCategoriesLoaded()
  void load()
})
</script>
