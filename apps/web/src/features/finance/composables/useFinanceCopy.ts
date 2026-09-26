import { computed, type ComputedRef } from 'vue'
import { useLocaleStore } from '@/stores/locale.store'

export interface FinanceCopy {
  pending: string
  partial: string
  paid: string
  overdue: string
  sent: string
  simulated: string
  failed: string
  skipped: string
  unknownMember: string
  outstandingFor: (balance: string, year: number) => string
}

/**
 * Feature-scoped copy for the finance workspace.
 *
 * All values resolve through the feature catalogs
 * (`i18n/<locale>/finance.json`); no inline locale switching remains.
 */
export function useFinanceCopy(): ComputedRef<FinanceCopy> {
  const localeStore = useLocaleStore()

  return computed<FinanceCopy>(() => ({
    pending: localeStore.t('finance.status.pending'),
    partial: localeStore.t('finance.status.partial'),
    paid: localeStore.t('finance.status.paid'),
    overdue: localeStore.t('finance.status.overdue'),
    sent: localeStore.t('finance.reminderStatus.sent'),
    simulated: localeStore.t('finance.reminderStatus.simulated'),
    failed: localeStore.t('finance.reminderStatus.failed'),
    skipped: localeStore.t('finance.reminderStatus.skipped'),
    unknownMember: localeStore.t('finance.unknownMember'),
    outstandingFor: (balance: string, year: number) => localeStore.t('finance.outstandingFor', { balance, year }),
  }))
}
