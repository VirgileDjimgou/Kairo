import { computed, ref } from 'vue'
import {
  confirmContributionReceiptInTreasury,
  createContribution,
  createExpense,
  exportMemberFinanceReport,
  getAnnualBudget,
  getContributionSummary,
  listContributionReceiptDeclarations,
  listContributionReminders,
  listContributions,
  listTenantPayments,
  processContributionReceiptDeclaration,
  recordPayment,
  sendContributionReminder,
  sendContributionReminderBatch,
  updateContributionReceiptHandoverReminder,
  type AnnualBudgetResponse,
  type ContributionRecordResponse,
  type ContributionReminderResponse,
  type ContributionReceiptDeclarationResponse,
  type ContributionSummary,
  type MemberFinanceExportFormat,
  type PaymentRecordResponse,
  type TreasuryExpenseCategory,
} from '@/api/contributions.api'
import {
  getMemberBalance,
  listMembers,
  type MemberBalanceResponse,
  type MembershipProfileResponse,
} from '@/api/membership.api'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'
import { CAP_FINANCE_EXPENSES_WRITE, CAP_FINANCE_WRITE } from '@/config/capabilities'
import { useRecoveryState } from '@/composables/useRecoveryState'
import { useFinanceCopy } from './useFinanceCopy'
import { useFinanceFormatting } from './useFinanceFormatting'

export interface ContributionCreateInput {
  membership_profile_id: string
  year: number
  expected_amount: string
  status: string
}

export interface PaymentInput {
  amount: string
  payment_method: string
  reference: string
}

export interface ExpenseInput {
  category: TreasuryExpenseCategory
  amount: string
  spent_at: string
  description: string
  payee: string
  payment_method: string
  reference: string
}

export interface ReminderBatchInput {
  due_scope: 'all_outstanding' | 'overdue' | 'due_soon'
  status: string
  limit: number
}

export type ReceiptDecisionAction = 'validated' | 'rejected'
export type CustodyDecisionAction = 'reminder' | 'close'

export interface ReceiptDecision {
  item: ContributionReceiptDeclarationResponse
  action: ReceiptDecisionAction
}

export interface CustodyDecision {
  item: ContributionReceiptDeclarationResponse
  action: CustodyDecisionAction
}

export interface ReceiptDecisionConfirmation {
  reminderDays: number
  note: string
}

export interface CustodyDecisionConfirmation {
  reminderDays: number
  method: 'cash' | 'bank_transfer'
  note: string
}

/**
 * Orchestration for the finance workspace.
 *
 * Owns finance state, API gateway calls and mutation handlers. The Vue view and
 * its feature components stay presentational; every permission decision remains
 * server-enforced.
 */
export function useFinanceWorkspace() {
  const localeStore = useLocaleStore()
  const authStore = useAuthStore()
  const tenantStore = useTenantStore()
  const t = (key: string) => localeStore.t(key)
  const copy = useFinanceCopy()
  const { reminderStatusLabel } = useFinanceFormatting()
  const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState()

  const notice = ref('')
  const exporting = ref(false)
  const savingContribution = ref(false)
  const savingPayment = ref(false)
  const savingExpense = ref(false)
  const sendingSingleReminderId = ref('')
  const sendingBatchReminders = ref(false)

  const members = ref<MembershipProfileResponse[]>([])
  const contributions = ref<ContributionRecordResponse[]>([])
  const summary = ref<ContributionSummary | null>(null)
  const selectedMemberBalance = ref<MemberBalanceResponse | null>(null)
  const selectedMemberId = ref('')
  const paymentTarget = ref<ContributionRecordResponse | null>(null)
  const recentPayments = ref<PaymentRecordResponse[]>([])
  const reminderHistory = ref<ContributionReminderResponse[]>([])
  const allContributionRecords = ref<ContributionRecordResponse[]>([])
  const receiptDeclarations = ref<ContributionReceiptDeclarationResponse[]>([])
  const receiptDecision = ref<ReceiptDecision | null>(null)
  const custodyDecision = ref<CustodyDecision | null>(null)
  const annualBudget = ref<AnnualBudgetResponse | null>(null)
  const createFormResetToken = ref(0)
  const paymentFormResetToken = ref(0)
  const expenseFormResetToken = ref(0)

  const isTreasurer = authStore.hasCapability(CAP_FINANCE_EXPENSES_WRITE)
  const canManageTreasury = authStore.hasCapability(CAP_FINANCE_WRITE)

  const currentYear = new Date().getFullYear()
  const years = [currentYear - 1, currentYear, currentYear + 1]
  const selectedYear = ref(currentYear)
  const remindersEnabled = computed(() => tenantStore.isModuleEnabled('notifications'))
  const expenseCategories: TreasuryExpenseCategory[] = [
    'sport_equipment',
    'fuel_transport',
    'tournament',
    'cultural_event',
    'administration',
    'other',
  ]
  const noContributionRecordsLabel = computed(() => `${t('contributions.noRecords').replace('{year}', String(selectedYear.value))}`)

  const membersById = computed(() =>
    Object.fromEntries(members.value.map((member) => [member.id, member])),
  )

  const pendingDeclarations = computed(() =>
    receiptDeclarations.value.filter((item) => item.status === 'submitted'),
  )
  const handoverDeclarations = computed(() => receiptDeclarations.value.filter((item) => ['pending_handover', 'handover_reported'].includes(item.cash_handover_status || '')))

  const contributionsById = computed(() =>
    Object.fromEntries(contributions.value.map((contribution) => [contribution.id, contribution])),
  )

  function memberLabel(profileId: string): string {
    const member = membersById.value[profileId]
    if (!member) return copy.value.unknownMember
    return `${member.display_name} (${member.member_code})`
  }

  function paymentMemberLabel(contributionId: string): string {
    const contribution = contributionsById.value[contributionId]
    if (!contribution) return copy.value.unknownMember
    return memberLabel(contribution.membership_profile_id)
  }

  function paymentTargetCopy(balance: string, year: number): string {
    return copy.value.outstandingFor(balance, year)
  }

  function receiptDeclarationLabel(item: ContributionReceiptDeclarationResponse): string {
    return item.income_type === 'membership_contribution'
      ? memberLabel(item.membership_profile_id!)
      : (item.source_name || t('receipt.externalIncome'))
  }

  async function refreshFinanceData() {
    const reminderPromise = remindersEnabled.value ? listContributionReminders(selectedYear.value) : Promise.resolve([])
    const [contributionRows, summaryData, paymentRows, reminderRows] = await Promise.all([
      listContributions(selectedYear.value),
      getContributionSummary(selectedYear.value),
      listTenantPayments(),
      reminderPromise,
    ])
    contributions.value = contributionRows
    summary.value = summaryData
    recentPayments.value = paymentRows.slice(0, 8)
    reminderHistory.value = reminderRows.slice(0, 8)
    if (canManageTreasury.value) {
      const [declarations, allContributions, budget] = await Promise.all([
        listContributionReceiptDeclarations(),
        listContributions(),
        isTreasurer.value ? getAnnualBudget(selectedYear.value) : Promise.resolve(null),
      ])
      receiptDeclarations.value = declarations
      allContributionRecords.value = allContributions
      annualBudget.value = budget
    } else {
      receiptDeclarations.value = []
      allContributionRecords.value = []
      annualBudget.value = null
    }
  }

  async function refreshAll() {
    await run(async () => {
      members.value = await listMembers()
      await refreshFinanceData()
      if (selectedMemberId.value) {
        await loadSelectedMemberBalance()
      }
    })
  }

  async function retryAll() {
    await retry(async () => {
      members.value = await listMembers()
      await refreshFinanceData()
      if (selectedMemberId.value) {
        await loadSelectedMemberBalance()
      }
    })
  }

  async function loadSelectedMemberBalance() {
    if (!selectedMemberId.value) {
      selectedMemberBalance.value = null
      return
    }
    selectedMemberBalance.value = await getMemberBalance(selectedMemberId.value)
  }

  function selectFinanceMemberById() {
    const member = members.value.find((item) => item.id === selectedMemberId.value)
    if (member) {
      selectedMemberId.value = member.id
      void loadSelectedMemberBalance()
    } else {
      void loadSelectedMemberBalance()
    }
  }

  function openReceiptDecision(item: ContributionReceiptDeclarationResponse, action: ReceiptDecisionAction) {
    receiptDecision.value = { item, action }
  }

  function closeReceiptDecision() {
    receiptDecision.value = null
  }

  async function confirmReceiptDecision(confirmation: ReceiptDecisionConfirmation) {
    if (!receiptDecision.value) return
    const { item, action } = receiptDecision.value
    if (action === 'rejected' && !confirmation.note) return
    const reminderDays = confirmation.reminderDays
    const note = confirmation.note
    closeReceiptDecision()
    clearError()
    const contribution = allContributionRecords.value.find((row) => row.membership_profile_id === item.membership_profile_id && Number(row.balance) > 0)
    if (action === 'validated' && item.income_type === 'membership_contribution' && !contribution) {
      error.value = t('finance.noOutstandingContribution')
      return
    }
    try {
      await processContributionReceiptDeclaration(item.id, action === 'validated'
        ? { action, handover_reminder_days: reminderDays, ...(item.income_type === 'membership_contribution' ? { contribution_record_id: contribution!.id } : {}) }
        : { action, note: note || t('finance.receiptRejectedNote') })
      notice.value = action === 'validated' ? t('finance.receiptValidated') : t('finance.receiptRejected')
      await refreshAll()
    } catch (err) {
      error.value = err instanceof Error ? err.message : t('finance.receiptProcessingFailed')
    }
  }

  function openCustodyDecision(item: ContributionReceiptDeclarationResponse, action: CustodyDecisionAction) {
    custodyDecision.value = { item, action }
  }

  function closeCustodyDecision() {
    custodyDecision.value = null
  }

  async function confirmCustodyDecision(confirmation: CustodyDecisionConfirmation) {
    if (!custodyDecision.value) return
    const { item, action } = custodyDecision.value
    clearError()
    try {
      if (action === 'reminder') {
        await updateContributionReceiptHandoverReminder(item.id, { reminder_days: confirmation.reminderDays })
        notice.value = t('receipt.reminderUpdated')
      } else {
        await confirmContributionReceiptInTreasury(item.id, { method: confirmation.method, note: confirmation.note || null })
        notice.value = t('receipt.treasuryReceived')
      }
      closeCustodyDecision()
      await refreshAll()
    } catch (err) {
      error.value = err instanceof Error ? err.message : t('finance.receiptProcessingFailed')
    }
  }

  async function handleCreateExpense(payload: ExpenseInput) {
    savingExpense.value = true
    clearError()
    notice.value = ''
    try {
      await createExpense({
        category: payload.category,
        amount: payload.amount,
        spent_at: new Date(`${payload.spent_at}T12:00:00`).toISOString(),
        description: payload.description,
        payee: payload.payee || null,
        payment_method: payload.payment_method,
        reference: payload.reference || null,
      })
      expenseFormResetToken.value += 1
      notice.value = t('finance.expenseRecorded')
      await refreshFinanceData()
    } catch (err) {
      error.value = err instanceof Error ? err.message : t('common.error')
    } finally {
      savingExpense.value = false
    }
  }

  async function handleSingleReminder(contribution: ContributionRecordResponse) {
    sendingSingleReminderId.value = contribution.id
    clearError()
    notice.value = ''
    try {
      const result = await sendContributionReminder(contribution.id)
      notice.value = `${reminderStatusLabel(result.delivery_status)} reminder for ${result.member_display_name}.`
      await refreshFinanceData()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unable to send the reminder.'
    } finally {
      sendingSingleReminderId.value = ''
    }
  }

  async function handleBatchReminder(payload: ReminderBatchInput) {
    sendingBatchReminders.value = true
    clearError()
    notice.value = ''
    try {
      const result = await sendContributionReminderBatch({
        year: selectedYear.value,
        due_scope: payload.due_scope,
        limit: payload.limit,
        ...(payload.status ? { status: payload.status } : {}),
      })
      notice.value = `Processed ${result.attempted_count} reminder target(s).`
      await refreshFinanceData()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unable to send reminder batch.'
    } finally {
      sendingBatchReminders.value = false
    }
  }

  function resetCreateForm() {
    createFormResetToken.value += 1
  }

  function selectPaymentTarget(contribution: ContributionRecordResponse) {
    paymentTarget.value = contribution
  }

  async function handleCreateContribution(payload: ContributionCreateInput) {
    savingContribution.value = true
    clearError()
    try {
      await createContribution({
        membership_profile_id: payload.membership_profile_id,
        year: payload.year,
        expected_amount: payload.expected_amount,
        paid_amount: '0.00',
        status: payload.status,
      })
      resetCreateForm()
      await refreshAll()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unable to create the contribution record.'
    } finally {
      savingContribution.value = false
    }
  }

  function resetPaymentForm() {
    paymentTarget.value = null
    paymentFormResetToken.value += 1
  }

  async function handleRecordPayment(payload: PaymentInput) {
    if (!paymentTarget.value) return

    savingPayment.value = true
    clearError()
    try {
      await recordPayment({
        contribution_record_id: paymentTarget.value.id,
        amount: payload.amount,
        payment_method: payload.payment_method,
        reference: payload.reference || null,
      })
      const targetMemberId = paymentTarget.value.membership_profile_id
      resetPaymentForm()
      await refreshAll()
      if (selectedMemberId.value === targetMemberId) {
        await loadSelectedMemberBalance()
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unable to record the payment.'
    } finally {
      savingPayment.value = false
    }
  }

  async function downloadMemberReport(format: Exclude<MemberFinanceExportFormat, 'whatsapp'>) {
    exporting.value = true
    try {
      const blob = await exportMemberFinanceReport(format, selectedYear.value)
      downloadBlob(blob, `rapport-financier-${selectedYear.value}.${format}`)
    } finally {
      exporting.value = false
    }
  }

  async function shareWhatsappSummary() {
    exporting.value = true
    try {
      const summaryText = await (await exportMemberFinanceReport('whatsapp', selectedYear.value)).text()
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(summaryText)
        notice.value = t('finance.whatsappCopied')
      } else {
        downloadBlob(new Blob([summaryText], { type: 'text/plain;charset=utf-8' }), `rapport-financier-${selectedYear.value}-whatsapp.txt`)
        notice.value = t('finance.whatsappFileDownloaded')
      }
    } finally {
      exporting.value = false
    }
  }

  function downloadBlob(blob: Blob, filename: string) {
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
  }

  async function initialize() {
    members.value = await listMembers()
    await refreshAll()
  }

  return {
    loading,
    error,
    isRecovering,
    clearError,
    notice,
    exporting,
    savingContribution,
    savingPayment,
    savingExpense,
    sendingSingleReminderId,
    sendingBatchReminders,
    members,
    contributions,
    summary,
    selectedMemberBalance,
    selectedMemberId,
    paymentTarget,
    recentPayments,
    reminderHistory,
    allContributionRecords,
    receiptDeclarations,
    receiptDecision,
    custodyDecision,
    annualBudget,
    createFormResetToken,
    paymentFormResetToken,
    expenseFormResetToken,
    isTreasurer,
    canManageTreasury,
    years,
    selectedYear,
    remindersEnabled,
    expenseCategories,
    noContributionRecordsLabel,
    pendingDeclarations,
    handoverDeclarations,
    memberLabel,
    paymentMemberLabel,
    paymentTargetCopy,
    receiptDeclarationLabel,
    refreshFinanceData,
    refreshAll,
    retryAll,
    loadSelectedMemberBalance,
    selectFinanceMemberById,
    openReceiptDecision,
    closeReceiptDecision,
    confirmReceiptDecision,
    openCustodyDecision,
    closeCustodyDecision,
    confirmCustodyDecision,
    handleCreateExpense,
    handleSingleReminder,
    handleBatchReminder,
    resetCreateForm,
    selectPaymentTarget,
    handleCreateContribution,
    resetPaymentForm,
    handleRecordPayment,
    downloadMemberReport,
    shareWhatsappSummary,
    initialize,
  }
}

export type FinanceWorkspace = ReturnType<typeof useFinanceWorkspace>
