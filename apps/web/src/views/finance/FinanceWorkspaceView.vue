<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary-emphasis mb-2">{{ t('finance.workspaceKicker') }}</div>
        <h1 class="h4 fw-bold mb-1">{{ t('finance.workspaceTitle') }}</h1>
        <p class="text-muted mb-0">
          {{ t('finance.workspaceSubtitle') }}
        </p>
      </div>
      <FinanceWorkspaceActions
        v-model:selected-year="selectedYear"
        :years="years"
        :loading="loading"
        :exporting="exporting"
        @refresh="refreshAll"
        @update:model-value="refreshFinanceData"
        @export="downloadMemberReport"
        @share-whatsapp="shareWhatsappSummary"
      />
    </div>

    <div v-if="error" class="alert alert-danger border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
        <div>
          <div class="fw-semibold mb-1">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ t('finance.workspaceErrorTitle') }}
          </div>
          <p class="mb-0 small">{{ error }}</p>
          <p class="mb-0 small text-muted mt-1">{{ t('common.recoveryHint') }}</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm flex-shrink-0" type="button" @click="retryAll" :disabled="isRecovering">
          <span v-if="isRecovering" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          {{ isRecovering ? t('common.loading') : t('common.retry') }}
        </button>
      </div>
    </div>

    <div v-if="notice" class="alert alert-success alert-dismissible small py-2 mb-4" role="status">
      <i class="bi bi-check-circle me-1"></i>{{ notice }}
      <button type="button" class="btn-close py-2" @click="notice = ''"></button>
    </div>

    <AnnualBudgetOverview v-if="isTreasurer && annualBudget" :budget="annualBudget" />

    <ExpenseWorkspace
      v-if="isTreasurer"
      :budget="annualBudget"
      :categories="expenseCategories"
      :saving="savingExpense"
      :reset-token="expenseFormResetToken"
      @submit="handleCreateExpense"
    />

    <ReceiptValidationQueue
      v-if="canManageTreasury"
      :items="pendingDeclarations"
      :label-for="receiptDeclarationLabel"
      @decide="openReceiptDecision"
    />

    <CustodyQueue
      v-if="canManageTreasury && handoverDeclarations.length"
      :items="handoverDeclarations"
      :label-for="receiptDeclarationLabel"
      @decide="openCustodyDecision"
    />

    <ReceiptDecisionModal
      :decision="receiptDecision"
      :label-for="receiptDeclarationLabel"
      @confirm="confirmReceiptDecision"
      @close="closeReceiptDecision"
    />

    <CustodyDecisionModal
      :decision="custodyDecision"
      :label-for="receiptDeclarationLabel"
      @confirm="confirmCustodyDecision"
      @close="closeCustodyDecision"
    />
    <div v-if="receiptDecision || custodyDecision" class="modal-backdrop show"></div>

    <ContributionSummaryCards :summary="summary" />

    <div class="row g-4">
      <div class="col-xl-4">
        <MemberBalanceLookup
          v-model:selected-member-id="selectedMemberId"
          :members="members"
          :selected-balance="selectedMemberBalance"
          @member-selected="loadSelectedMemberBalance"
        />

        <ContributionCreateForm
          :members="members"
          :year="selectedYear"
          :saving="savingContribution"
          :reset-token="createFormResetToken"
          @submit="handleCreateContribution"
        />
      </div>

      <div class="col-xl-8">
        <RecentPaymentsCard :payments="recentPayments" :label-for="paymentMemberLabel" />

        <RemindersPanel
          v-if="remindersEnabled"
          :history="reminderHistory"
          :sending-batch="sendingBatchReminders"
          @submit="handleBatchReminder"
        />

        <PaymentRecordingCard
          :target="paymentTarget"
          :member-label="paymentTarget ? memberLabel(paymentTarget.membership_profile_id) : ''"
          :target-copy="paymentTarget ? paymentTargetCopy(paymentTarget.balance, paymentTarget.year) : ''"
          :saving="savingPayment"
          :reset-token="paymentFormResetToken"
          @submit="handleRecordPayment"
          @clear="resetPaymentForm"
        />

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">{{ t('common.loading') }}</span>
          </div>
        </div>

        <div v-else-if="contributions.length === 0" class="empty-state p-5">
          <i class="bi bi-cash-stack display-6 text-secondary"></i>
          <p class="mb-1 fw-semibold">{{ noContributionRecordsLabel }}</p>
          <p class="text-muted mb-0">{{ t('finance.noContributionRecordsHint') }}</p>
        </div>

        <ContributionRecordsTable
          v-else
          :contributions="contributions"
          :member-label="memberLabel"
          :status-badge-class="statusBadgeClass"
          :format-date="formatDate"
          :reminders-enabled="remindersEnabled"
          :sending-single-reminder-id="sendingSingleReminderId"
          @record-payment="selectPaymentTarget"
          @send-reminder="handleSingleReminder"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useLocaleStore } from '@/stores/locale.store'
import AnnualBudgetOverview from '@/features/finance/components/AnnualBudgetOverview.vue'
import ExpenseWorkspace from '@/features/finance/components/ExpenseWorkspace.vue'
import ReceiptValidationQueue from '@/features/finance/components/ReceiptValidationQueue.vue'
import CustodyQueue from '@/features/finance/components/CustodyQueue.vue'
import ReceiptDecisionModal from '@/features/finance/components/ReceiptDecisionModal.vue'
import CustodyDecisionModal from '@/features/finance/components/CustodyDecisionModal.vue'
import ContributionSummaryCards from '@/features/finance/components/ContributionSummaryCards.vue'
import MemberBalanceLookup from '@/features/finance/components/MemberBalanceLookup.vue'
import ContributionCreateForm from '@/features/finance/components/ContributionCreateForm.vue'
import RecentPaymentsCard from '@/features/finance/components/RecentPaymentsCard.vue'
import RemindersPanel from '@/features/finance/components/RemindersPanel.vue'
import PaymentRecordingCard from '@/features/finance/components/PaymentRecordingCard.vue'
import ContributionRecordsTable from '@/features/finance/components/ContributionRecordsTable.vue'
import FinanceWorkspaceActions from '@/features/finance/components/FinanceWorkspaceActions.vue'
import { useFinanceFormatting } from '@/features/finance/composables/useFinanceFormatting'
import { useFinanceWorkspace } from '@/features/finance/composables/useFinanceWorkspace'

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)
const { statusBadgeClass, formatDate } = useFinanceFormatting()

const {
  loading,
  error,
  isRecovering,
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
  openReceiptDecision,
  closeReceiptDecision,
  confirmReceiptDecision,
  openCustodyDecision,
  closeCustodyDecision,
  confirmCustodyDecision,
  handleCreateExpense,
  handleSingleReminder,
  handleBatchReminder,
  selectPaymentTarget,
  handleCreateContribution,
  resetPaymentForm,
  handleRecordPayment,
  downloadMemberReport,
  shareWhatsappSummary,
  initialize,
} = useFinanceWorkspace()

onMounted(initialize)
</script>
