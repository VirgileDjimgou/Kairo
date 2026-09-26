<template>
  <section v-if="budget" class="treasury-budget card shadow-sm border-0 mb-4" data-testid="finance-annual-budget">
    <div class="card-body p-4 p-lg-5">
      <div class="d-flex flex-column flex-lg-row justify-content-between gap-2 mb-4">
        <div>
          <div class="text-uppercase small fw-semibold text-primary mb-1">{{ t('finance.budgetKicker') }} · {{ budget.year }}</div>
          <h2 class="h4 fw-bold mb-1">{{ t('finance.budgetTitle') }}</h2>
          <p class="text-muted mb-0">{{ t('finance.budgetLead') }}</p>
        </div>
        <div class="budget-available align-self-lg-start">
          <span>{{ t('finance.availableTreasury') }}</span>
          <strong :class="Number(budget.available_balance) < 0 ? 'text-danger' : 'text-primary'">{{ formatMoney(budget.available_balance) }}</strong>
        </div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-md-4"><div class="budget-stat budget-stat-income"><span>{{ t('finance.recordedIncome') }}</span><strong>{{ formatMoney(budget.income_total) }}</strong></div></div>
        <div class="col-md-4"><div class="budget-stat budget-stat-expense"><span>{{ t('finance.recordedExpenses') }}</span><strong>{{ formatMoney(budget.expense_total) }}</strong></div></div>
        <div class="col-md-4"><div class="budget-stat budget-stat-balance"><span>{{ t('finance.availableTreasury') }}</span><strong>{{ formatMoney(budget.available_balance) }}</strong></div></div>
      </div>

      <div class="budget-charts-grid">
        <article class="budget-chart-panel">
          <div class="d-flex align-items-center justify-content-between gap-2 mb-3"><h3 class="h6 fw-bold mb-0">{{ t('finance.incomeBreakdown') }}</h3><span class="badge text-bg-success-subtle text-success-emphasis">{{ formatMoney(budget.income_total) }}</span></div>
          <div class="budget-chart-content">
            <div class="budget-donut" :style="{ background: budgetGradient(budget.income_by_category, incomePalette) }"><div class="budget-donut-center"><strong>{{ formatMoney(budget.income_total) }}</strong><span>{{ t('finance.recordedIncome') }}</span></div></div>
            <div class="budget-legend"><div v-for="(slice, index) in budget.income_by_category" :key="slice.category" class="budget-legend-item"><span class="budget-legend-dot" :style="{ backgroundColor: incomePalette[index % incomePalette.length] }"></span><span class="budget-legend-label">{{ incomeCategoryLabel(slice.category) }}</span><strong>{{ budgetPercentage(slice.amount, budget.income_total) }}%</strong></div></div>
          </div>
        </article>
        <article class="budget-chart-panel">
          <div class="d-flex align-items-center justify-content-between gap-2 mb-3"><h3 class="h6 fw-bold mb-0">{{ t('finance.expenseBreakdown') }}</h3><span class="badge text-bg-danger-subtle text-danger-emphasis">{{ formatMoney(budget.expense_total) }}</span></div>
          <div class="budget-chart-content">
            <div class="budget-donut" :style="{ background: budgetGradient(budget.expenses_by_category, expensePalette) }"><div class="budget-donut-center"><strong>{{ formatMoney(budget.expense_total) }}</strong><span>{{ t('finance.recordedExpenses') }}</span></div></div>
            <div class="budget-legend"><div v-for="(slice, index) in budget.expenses_by_category" :key="slice.category" class="budget-legend-item"><span class="budget-legend-dot" :style="{ backgroundColor: expensePalette[index % expensePalette.length] }"></span><span class="budget-legend-label">{{ expenseCategoryLabel(slice.category) }}</span><strong>{{ budgetPercentage(slice.amount, budget.expense_total) }}%</strong></div></div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { AnnualBudgetResponse } from '@/api/contributions.api'
import { useLocaleStore } from '@/stores/locale.store'
import { useFinanceFormatting, FINANCE_EXPENSE_PALETTE, FINANCE_INCOME_PALETTE } from '../composables/useFinanceFormatting'

defineProps<{ budget: AnnualBudgetResponse | null }>()

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { formatMoney, incomeCategoryLabel, expenseCategoryLabel, budgetPercentage, budgetGradient } = useFinanceFormatting()
const incomePalette = FINANCE_INCOME_PALETTE
const expensePalette = FINANCE_EXPENSE_PALETTE
</script>

<style scoped>
.treasury-budget {
  overflow: hidden;
  background:
    radial-gradient(circle at 92% 0%, rgba(53, 123, 212, 0.12), transparent 28rem),
    linear-gradient(135deg, #ffffff 0%, #f7faff 100%);
  border-top: 4px solid #2563a8;
}
.budget-available { display: grid; gap: 0.15rem; min-width: 12rem; padding: 0.75rem 1rem; border-radius: 1rem; background: #fff; border: 1px solid #d8e3f2; box-shadow: 0 0.45rem 1rem rgba(28, 65, 111, 0.07); }
.budget-available span, .budget-stat span { color: var(--bs-secondary); font-size: 0.82rem; }
.budget-available strong { font-size: 1.25rem; }
.budget-stat { min-height: 5.5rem; display: grid; align-content: center; gap: 0.4rem; padding: 1rem 1.1rem; border-radius: 1rem; border: 1px solid transparent; }
.budget-stat strong { font-size: 1.45rem; color: #142a48; }
.budget-stat-income { background: #e9f8f1; border-color: #c7ecdb; }
.budget-stat-expense { background: #fff0f1; border-color: #ffd1d6; }
.budget-stat-balance { background: #eaf2ff; border-color: #cbdcf8; }
.budget-charts-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
.budget-chart-panel { padding: 1.2rem; border: 1px solid #dce5f2; border-radius: 1.1rem; background: rgba(255,255,255,0.9); }
.budget-chart-content { display: flex; align-items: center; gap: 1.1rem; }
.budget-donut { display: grid; place-items: center; flex: 0 0 9.5rem; width: 9.5rem; height: 9.5rem; padding: 1.05rem; border-radius: 50%; box-shadow: inset 0 0 0 1px rgba(31, 79, 143, 0.08); }
.budget-donut-center { display: grid; place-items: center; width: 100%; height: 100%; padding: 0.4rem; border-radius: 50%; background: #fff; text-align: center; }
.budget-donut-center strong { font-size: 0.95rem; color: #152b4c; }
.budget-donut-center span { color: var(--bs-secondary); font-size: 0.67rem; line-height: 1.2; }
.budget-legend { min-width: 0; flex: 1; display: grid; gap: 0.45rem; }
.budget-legend-item { display: grid; grid-template-columns: 0.65rem minmax(0, 1fr) auto; align-items: center; gap: 0.45rem; font-size: 0.78rem; }
.budget-legend-dot { width: 0.6rem; height: 0.6rem; border-radius: 999px; }
.budget-legend-label { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #455569; }

@media (max-width: 767.98px) {
  .budget-available { width: 100%; }
  .budget-charts-grid { grid-template-columns: 1fr; }
  .budget-chart-content { align-items: flex-start; }
  .budget-donut { flex-basis: 7.5rem; width: 7.5rem; height: 7.5rem; padding: 0.85rem; }
  .budget-donut-center strong { font-size: 0.8rem; }
}

@media (max-width: 420px) {
  .budget-chart-content { flex-direction: column; align-items: center; }
  .budget-legend { width: 100%; }
}
</style>
