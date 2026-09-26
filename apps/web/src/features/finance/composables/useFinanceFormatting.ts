import { useLocaleStore } from '@/stores/locale.store'
import type {
  BudgetCategoryTotal,
  ContributionReminderResponse,
  ContributionReceiptDeclarationResponse,
} from '@/api/contributions.api'
import { useFinanceCopy } from './useFinanceCopy'

export const FINANCE_INCOME_PALETTE = ['#2563a8', '#21a179', '#7a5af8', '#19a7ce', '#d38b18', '#546173']
export const FINANCE_EXPENSE_PALETTE = ['#d33a4c', '#e88924', '#8f3f9f', '#2f855a', '#4a6fa5', '#7a7f89']

/**
 * Locale-aware formatters and label mappers for the finance workspace.
 *
 * Pure presentation logic extracted from the view: no API calls and no
 * authorization decisions live here.
 */
export function useFinanceFormatting() {
  const localeStore = useLocaleStore()
  const copy = useFinanceCopy()
  const t = (key: string) => localeStore.t(key)

  function formatDate(value: string | null): string {
    if (!value) return '—'
    return new Date(value).toLocaleDateString()
  }

  function formatPaymentMethod(value: string): string {
    return value.replace('_', ' ')
  }

  function formatMoney(value: string): string {
    return new Intl.NumberFormat(localeStore.currentLocale, {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
    }).format(Number(value || 0))
  }

  function incomeCategoryLabel(category: string): string {
    const keys: Record<string, string> = {
      membership_contribution: 'finance.incomeCategory.membershipContribution',
      donation: 'finance.incomeCategory.donation',
      sponsorship: 'finance.incomeCategory.sponsorship',
      tournament_proceeds: 'finance.incomeCategory.tournamentProceeds',
      disciplinary_payment: 'finance.incomeCategory.disciplinaryPayment',
      other_income: 'finance.incomeCategory.otherIncome',
    }
    return t(keys[category] || 'finance.incomeCategory.otherIncome')
  }

  function expenseCategoryLabel(category: string): string {
    const keys: Record<string, string> = {
      sport_equipment: 'finance.expenseCategory.sportEquipment',
      fuel_transport: 'finance.expenseCategory.fuelTransport',
      tournament: 'finance.expenseCategory.tournament',
      cultural_event: 'finance.expenseCategory.culturalEvent',
      administration: 'finance.expenseCategory.administration',
      other: 'finance.expenseCategory.other',
    }
    return t(keys[category] || 'finance.expenseCategory.other')
  }

  function budgetPercentage(amount: string, total: string): number {
    const denominator = Number(total)
    return denominator > 0 ? Math.round((Number(amount) / denominator) * 100) : 0
  }

  function budgetGradient(slices: BudgetCategoryTotal[], palette: string[]): string {
    const total = slices.reduce((sum, slice) => sum + Number(slice.amount), 0)
    if (total <= 0) return '#e7edf5'
    let start = 0
    const segments = slices
      .filter((slice) => Number(slice.amount) > 0)
      .map((slice, index) => {
        const end = start + (Number(slice.amount) / total) * 360
        const segment = `${palette[index % palette.length]} ${start}deg ${end}deg`
        start = end
        return segment
      })
    return `conic-gradient(${segments.join(', ')})`
  }

  function reminderStatusLabel(value: ContributionReminderResponse['delivery_status']): string {
    const map = {
      sent: copy.value.sent,
      simulated: copy.value.simulated,
      failed: copy.value.failed,
      skipped: copy.value.skipped,
    }
    return map[value] || value
  }

  function statusBadgeClass(status: string): string {
    const map: Record<string, string> = {
      pending: 'bg-secondary-subtle text-secondary',
      partial: 'bg-warning-subtle text-warning',
      paid: 'bg-success-subtle text-success',
      overdue: 'bg-danger-subtle text-danger',
      waived: 'bg-info-subtle text-info',
    }
    return map[status] || 'bg-light text-dark'
  }

  function handoverStatusLabel(value: ContributionReceiptDeclarationResponse['cash_handover_status']): string {
    return value === 'handover_reported' ? t('receipt.handoverReported') : value === 'received_in_treasury' ? t('receipt.treasuryReceived') : t('receipt.cashPending')
  }

  function receiptIncomeTypeLabel(incomeType: ContributionReceiptDeclarationResponse['income_type']): string {
    const keys = {
      membership_contribution: 'receipt.incomeType.membershipContribution',
      donation: 'receipt.incomeType.donation',
      sponsorship: 'receipt.incomeType.sponsorship',
      tournament_proceeds: 'receipt.incomeType.tournamentProceeds',
      other_income: 'receipt.incomeType.otherIncome',
      disciplinary_payment: 'receipt.incomeType.disciplinaryPayment',
    } as const
    return t(keys[incomeType])
  }

  return {
    copy,
    formatDate,
    formatPaymentMethod,
    formatMoney,
    incomeCategoryLabel,
    expenseCategoryLabel,
    budgetPercentage,
    budgetGradient,
    reminderStatusLabel,
    statusBadgeClass,
    handoverStatusLabel,
    receiptIncomeTypeLabel,
  }
}
