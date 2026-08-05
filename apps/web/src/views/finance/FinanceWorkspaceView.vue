<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">{{ t('finance.workspaceKicker') }}</div>
        <h1 class="h4 fw-bold mb-1">{{ t('finance.workspaceTitle') }}</h1>
        <p class="text-muted mb-0">
          {{ t('finance.workspaceSubtitle') }}
        </p>
      </div>
      <div class="finance-actions">
        <select v-model="selectedYear" class="form-select form-select-sm" style="width: auto" @change="refreshFinanceData">
          <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
        </select>
        <button class="btn btn-outline-secondary btn-sm" type="button" @click="refreshAll" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          {{ t('common.refresh') }}
        </button>
        <button class="btn btn-outline-primary btn-sm" type="button" @click="downloadMemberReport('xlsx')" :disabled="exporting">{{ t('finance.exportExcel') }}</button>
        <button class="btn btn-outline-primary btn-sm" type="button" @click="downloadMemberReport('pdf')" :disabled="exporting">{{ t('finance.exportPdf') }}</button>
        <button class="btn btn-outline-success btn-sm" type="button" @click="shareWhatsappSummary" :disabled="exporting">{{ t('finance.copyForWhatsapp') }}</button>
      </div>
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

    <section v-if="isTreasurer && annualBudget" class="treasury-budget card shadow-sm border-0 mb-4" data-testid="finance-annual-budget">
      <div class="card-body p-4 p-lg-5">
        <div class="d-flex flex-column flex-lg-row justify-content-between gap-2 mb-4">
          <div>
            <div class="text-uppercase small fw-semibold text-primary mb-1">{{ t('finance.budgetKicker') }} · {{ annualBudget.year }}</div>
            <h2 class="h4 fw-bold mb-1">{{ t('finance.budgetTitle') }}</h2>
            <p class="text-muted mb-0">{{ t('finance.budgetLead') }}</p>
          </div>
          <div class="budget-available align-self-lg-start">
            <span>{{ t('finance.availableTreasury') }}</span>
            <strong :class="Number(annualBudget.available_balance) < 0 ? 'text-danger' : 'text-primary'">{{ formatMoney(annualBudget.available_balance) }}</strong>
          </div>
        </div>

        <div class="row g-3 mb-4">
          <div class="col-md-4"><div class="budget-stat budget-stat-income"><span>{{ t('finance.recordedIncome') }}</span><strong>{{ formatMoney(annualBudget.income_total) }}</strong></div></div>
          <div class="col-md-4"><div class="budget-stat budget-stat-expense"><span>{{ t('finance.recordedExpenses') }}</span><strong>{{ formatMoney(annualBudget.expense_total) }}</strong></div></div>
          <div class="col-md-4"><div class="budget-stat budget-stat-balance"><span>{{ t('finance.availableTreasury') }}</span><strong>{{ formatMoney(annualBudget.available_balance) }}</strong></div></div>
        </div>

        <div class="budget-charts-grid">
          <article class="budget-chart-panel">
            <div class="d-flex align-items-center justify-content-between gap-2 mb-3"><h3 class="h6 fw-bold mb-0">{{ t('finance.incomeBreakdown') }}</h3><span class="badge text-bg-success-subtle text-success-emphasis">{{ formatMoney(annualBudget.income_total) }}</span></div>
            <div class="budget-chart-content">
              <div class="budget-donut" :style="{ background: budgetGradient(annualBudget.income_by_category, incomePalette) }"><div class="budget-donut-center"><strong>{{ formatMoney(annualBudget.income_total) }}</strong><span>{{ t('finance.recordedIncome') }}</span></div></div>
              <div class="budget-legend"><div v-for="(slice, index) in annualBudget.income_by_category" :key="slice.category" class="budget-legend-item"><span class="budget-legend-dot" :style="{ backgroundColor: incomePalette[index % incomePalette.length] }"></span><span class="budget-legend-label">{{ incomeCategoryLabel(slice.category) }}</span><strong>{{ budgetPercentage(slice.amount, annualBudget.income_total) }}%</strong></div></div>
            </div>
          </article>
          <article class="budget-chart-panel">
            <div class="d-flex align-items-center justify-content-between gap-2 mb-3"><h3 class="h6 fw-bold mb-0">{{ t('finance.expenseBreakdown') }}</h3><span class="badge text-bg-danger-subtle text-danger-emphasis">{{ formatMoney(annualBudget.expense_total) }}</span></div>
            <div class="budget-chart-content">
              <div class="budget-donut" :style="{ background: budgetGradient(annualBudget.expenses_by_category, expensePalette) }"><div class="budget-donut-center"><strong>{{ formatMoney(annualBudget.expense_total) }}</strong><span>{{ t('finance.recordedExpenses') }}</span></div></div>
              <div class="budget-legend"><div v-for="(slice, index) in annualBudget.expenses_by_category" :key="slice.category" class="budget-legend-item"><span class="budget-legend-dot" :style="{ backgroundColor: expensePalette[index % expensePalette.length] }"></span><span class="budget-legend-label">{{ expenseCategoryLabel(slice.category) }}</span><strong>{{ budgetPercentage(slice.amount, annualBudget.expense_total) }}%</strong></div></div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section v-if="isTreasurer" class="row g-4 mb-4" data-testid="finance-expense-workspace">
      <div class="col-xl-5">
        <div class="card shadow-sm border-0 expense-entry-card h-100"><div class="card-body p-4">
          <div class="text-uppercase small fw-semibold text-danger mb-1">{{ t('finance.expenseKicker') }}</div>
          <h2 class="h5 fw-bold mb-1">{{ t('finance.expenseTitle') }}</h2><p class="small text-muted mb-4">{{ t('finance.expenseLead') }}</p>
          <form class="row g-3" @submit.prevent="handleCreateExpense">
            <div class="col-md-7"><label for="expense-category" class="form-label small fw-medium">{{ t('finance.expenseCategory') }}</label><select id="expense-category" v-model="expenseForm.category" class="form-select" required><option v-for="category in expenseCategories" :key="category" :value="category">{{ expenseCategoryLabel(category) }}</option></select></div>
            <div class="col-md-5"><label for="expense-amount" class="form-label small fw-medium">{{ t('common.amount') }} (EUR)</label><input id="expense-amount" v-model="expenseForm.amount" class="form-control" type="number" min="0.01" step="0.01" required /></div>
            <div class="col-md-6"><label for="expense-date" class="form-label small fw-medium">{{ t('finance.expenseDate') }}</label><input id="expense-date" v-model="expenseForm.spent_at" class="form-control" type="date" required /></div>
            <div class="col-md-6"><label for="expense-method" class="form-label small fw-medium">{{ t('contributions.paymentMethod') }}</label><select id="expense-method" v-model="expenseForm.payment_method" class="form-select"><option value="cash">{{ t('contributions.cash') }}</option><option value="bank_transfer">{{ t('contributions.bankTransfer') }}</option><option value="card">{{ t('finance.card') }}</option><option value="check">{{ t('contributions.check') }}</option><option value="other">{{ t('finance.other') }}</option></select></div>
            <div class="col-12"><label for="expense-payee" class="form-label small fw-medium">{{ t('finance.expensePayee') }}</label><input id="expense-payee" v-model.trim="expenseForm.payee" class="form-control" /></div>
            <div class="col-12"><label for="expense-description" class="form-label small fw-medium">{{ t('finance.expenseDescription') }}</label><textarea id="expense-description" v-model.trim="expenseForm.description" class="form-control" rows="3" :placeholder="t('finance.expenseDescriptionPlaceholder')" required></textarea></div>
            <div class="col-12"><label for="expense-reference" class="form-label small fw-medium">{{ t('finance.expenseReference') }}</label><input id="expense-reference" v-model.trim="expenseForm.reference" class="form-control" /></div>
            <div class="col-12 d-grid"><button class="btn btn-danger" type="submit" :disabled="savingExpense"><span v-if="savingExpense" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>{{ savingExpense ? t('common.saving') : t('finance.recordExpense') }}</button></div>
          </form>
        </div></div>
      </div>
      <div class="col-xl-7">
        <div class="card shadow-sm border-0 recent-expenses-card h-100"><div class="card-body p-4">
          <div class="d-flex align-items-center justify-content-between gap-2 mb-3"><div><div class="text-uppercase small fw-semibold text-secondary">{{ t('finance.expenseKicker') }}</div><h2 class="h5 fw-bold mb-0">{{ t('finance.recentExpenses') }}</h2></div><span class="badge text-bg-light border text-dark">{{ annualBudget?.recent_expenses.length || 0 }}</span></div>
          <p v-if="!annualBudget || annualBudget.recent_expenses.length === 0" class="text-muted small mb-0">{{ t('finance.noExpenses') }}</p>
          <div v-else class="vstack gap-2"><article v-for="expense in annualBudget.recent_expenses" :key="expense.id" class="recent-expense-item"><div class="expense-category-icon"><i class="bi bi-arrow-up-right"></i></div><div class="flex-grow-1 min-w-0"><div class="d-flex flex-wrap justify-content-between gap-2"><strong>{{ expenseCategoryLabel(expense.category) }}</strong><strong class="text-danger">− {{ formatMoney(expense.amount) }}</strong></div><div class="small text-muted text-truncate">{{ expense.description }}</div><div class="small text-secondary mt-1">{{ formatDate(expense.spent_at) }}<span v-if="expense.payee"> · {{ expense.payee }}</span></div></div></article></div>
        </div></div>
      </div>
    </section>

    <section v-if="canManageTreasury" class="card shadow-sm border-0 mb-4 receipt-queue" data-testid="finance-receipt-validation-queue">
      <div class="card-body p-4">
        <div class="d-flex flex-column flex-md-row justify-content-between gap-2 mb-3">
          <div>
            <div class="text-uppercase small fw-semibold text-secondary mb-1">{{ t('finance.receiptValidationKicker') }}</div>
            <h2 class="h5 fw-bold mb-1">{{ t('finance.receiptValidationTitle') }}</h2>
            <p class="small text-muted mb-0">{{ t('finance.receiptValidationLead') }}</p>
          </div>
          <span class="badge align-self-start text-bg-warning">{{ pendingDeclarations.length }}</span>
        </div>
        <p v-if="pendingDeclarations.length === 0" class="small text-muted mb-0">{{ t('finance.noReceiptDeclarations') }}</p>
        <div v-else class="vstack gap-2">
          <article v-for="item in pendingDeclarations" :key="item.id" class="receipt-queue-item rounded-3 p-3">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
              <div>
                <div class="fw-semibold">{{ receiptDeclarationLabel(item) }}</div>
                <div class="small text-muted">{{ receiptIncomeTypeLabel(item.income_type) }} · {{ item.amount }} {{ item.currency }} · {{ item.declarant_role_code }} · {{ formatDate(item.received_at) }}</div>
                <div v-if="item.note" class="small mt-2">{{ item.note }}</div>
              </div>
              <div class="d-flex gap-2 align-items-start">
                <button class="btn btn-sm btn-success" type="button" @click="openReceiptDecision(item, 'validated')">{{ t('finance.validateReceipt') }}</button>
                <button class="btn btn-sm btn-outline-danger" type="button" @click="openReceiptDecision(item, 'rejected')">{{ t('finance.rejectReceipt') }}</button>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section v-if="canManageTreasury && handoverDeclarations.length" class="card shadow-sm border-0 mb-4 custody-workspace" data-testid="finance-cash-custody-queue">
      <div class="card-body p-4">
        <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
          <div>
            <div class="text-uppercase small fw-semibold text-primary mb-1">{{ t('receipt.custodyKicker') }}</div>
            <h2 class="h5 fw-bold mb-1">{{ t('receipt.cashPending') }}</h2>
            <p class="small text-muted mb-0">{{ t('receipt.custodyLead') }}</p>
          </div>
          <span class="badge rounded-pill text-bg-primary align-self-start px-3 py-2">{{ handoverDeclarations.length }} {{ t('finance.itemsCountSuffix') }}</span>
        </div>
        <div class="vstack gap-3">
          <article v-for="item in handoverDeclarations" :key="item.id" class="custody-card rounded-4 p-3 p-md-4" :class="item.cash_handover_status === 'handover_reported' ? 'custody-card-reported' : 'custody-card-pending'">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
              <div class="flex-grow-1">
                <div class="d-flex flex-wrap align-items-center gap-2 mb-2"><span class="fw-bold">{{ receiptDeclarationLabel(item) }}</span><span class="badge rounded-pill" :class="item.cash_handover_status === 'handover_reported' ? 'text-bg-info' : 'text-bg-warning'">{{ handoverStatusLabel(item.cash_handover_status) }}</span></div>
                <div class="small text-muted mb-3">{{ receiptIncomeTypeLabel(item.income_type) }} · {{ item.amount }} {{ item.currency }} · {{ t('receipt.receivedBy') }} {{ item.declarant_role_code }}</div>
                <div class="custody-meta-grid small">
                  <div><span>{{ t('receipt.currentReminder') }}</span><strong>{{ item.handover_reminder_days || 2 }} {{ t('receipt.days') }}</strong></div>
                  <div><span>{{ t('receipt.dueDate') }}</span><strong>{{ formatDate(item.handover_due_at) }}</strong></div>
                  <div v-if="item.handover_method"><span>{{ t('receipt.handoverMethod') }}</span><strong>{{ item.handover_method === 'bank_transfer' ? t('receipt.handoverTransfer') : t('receipt.handoverCash') }}</strong></div>
                </div>
              </div>
              <div class="custody-actions align-self-lg-center">
                <button class="btn btn-outline-primary" type="button" @click="openCustodyDecision(item, 'reminder')"><i class="bi bi-clock-history me-1"></i>{{ t('receipt.changeReminder') }}</button>
                <button class="btn btn-primary" type="button" @click="openCustodyDecision(item, 'close')"><i class="bi bi-safe2 me-1"></i>{{ t('receipt.closeInTreasury') }}</button>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <div v-if="summary" class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card shadow-sm border-0 bg-primary-subtle">
          <div class="card-body text-center py-3">
            <div class="text-muted small">{{ t('contributions.expected') }}</div>
            <div class="fw-bold fs-4">{{ summary.total_expected }} EUR</div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm border-0 bg-success-subtle">
          <div class="card-body text-center py-3">
            <div class="text-muted small">{{ t('contributions.paid') }}</div>
            <div class="fw-bold fs-4">{{ summary.total_paid }} EUR</div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm border-0" :class="Number(summary.total_balance) > 0 ? 'bg-warning-subtle' : 'bg-success-subtle'">
          <div class="card-body text-center py-3">
            <div class="text-muted small">{{ t('finance.outstandingBalance') }}</div>
            <div class="fw-bold fs-4">{{ summary.total_balance }} EUR</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="receiptDecision" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered"><div class="modal-content shadow">
        <div class="modal-header"><h2 class="modal-title fs-5">{{ t('receipt.reviewTitle') }}</h2><button class="btn-close" type="button" @click="closeReceiptDecision"></button></div>
        <div class="modal-body vstack gap-3"><p class="mb-0">{{ receiptDeclarationLabel(receiptDecision.item) }} · {{ receiptDecision.item.amount }} {{ receiptDecision.item.currency }}</p>
          <div v-if="receiptDecision.action === 'validated'"><label class="form-label" for="handover-reminder-days">{{ t('receipt.reminderDays') }}</label><select id="handover-reminder-days" v-model.number="receiptReminderDays" class="form-select"><option v-for="day in 7" :key="day" :value="day">{{ day }}</option></select></div>
          <div v-else><label class="form-label" for="receipt-rejection-reason">{{ t('receipt.rejectionReason') }}</label><textarea id="receipt-rejection-reason" v-model.trim="receiptDecisionNote" class="form-control" rows="3" required></textarea></div>
        </div>
        <div class="modal-footer"><button class="btn btn-outline-secondary" type="button" @click="closeReceiptDecision">{{ t('common.cancel') }}</button><button class="btn" :class="receiptDecision.action === 'validated' ? 'btn-success' : 'btn-danger'" type="button" :disabled="receiptDecision.action === 'rejected' && !receiptDecisionNote" @click="confirmReceiptDecision">{{ receiptDecision.action === 'validated' ? t('finance.validateReceipt') : t('finance.rejectReceipt') }}</button></div>
      </div></div>
    </div>

    <div v-if="custodyDecision" class="modal d-block" tabindex="-1" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-dialog-centered"><div class="modal-content shadow border-0">
        <div class="modal-header"><div><div class="text-uppercase small fw-semibold text-primary">{{ t('receipt.custodyKicker') }}</div><h2 class="modal-title fs-5">{{ custodyDecision.action === 'reminder' ? t('receipt.changeReminder') : t('receipt.closeInTreasury') }}</h2></div><button class="btn-close" type="button" @click="closeCustodyDecision"></button></div>
        <div class="modal-body vstack gap-3"><div class="rounded-3 bg-light p-3"><div class="fw-semibold">{{ receiptDeclarationLabel(custodyDecision.item) }}</div><div class="small text-muted">{{ custodyDecision.item.amount }} {{ custodyDecision.item.currency }} · {{ handoverStatusLabel(custodyDecision.item.cash_handover_status) }}</div></div>
          <template v-if="custodyDecision.action === 'reminder'"><label class="form-label mb-0" for="custody-reminder-days">{{ t('receipt.reminderDays') }}</label><select id="custody-reminder-days" v-model.number="custodyReminderDays" class="form-select"><option v-for="day in 7" :key="day" :value="day">{{ day }} {{ t('receipt.days') }}</option></select><p class="small text-muted mb-0">{{ t('receipt.reminderUpdateHint') }}</p></template>
          <template v-else><p class="small text-muted mb-0">{{ t('receipt.closeTreasuryHint') }}</p><div><label class="form-label" for="custody-method">{{ t('receipt.handoverMethod') }}</label><select id="custody-method" v-model="custodyMethod" class="form-select"><option value="cash">{{ t('receipt.handoverCash') }}</option><option value="bank_transfer">{{ t('receipt.handoverTransfer') }}</option></select></div><div><label class="form-label" for="custody-note">{{ t('receipt.closureNote') }}</label><textarea id="custody-note" v-model.trim="custodyNote" class="form-control" rows="3" :placeholder="t('receipt.closureNotePlaceholder')"></textarea></div></template>
        </div>
        <div class="modal-footer"><button class="btn btn-outline-secondary" type="button" @click="closeCustodyDecision">{{ t('common.cancel') }}</button><button class="btn btn-primary" type="button" @click="confirmCustodyDecision">{{ custodyDecision.action === 'reminder' ? t('receipt.saveReminder') : t('receipt.confirmClosure') }}</button></div>
      </div></div>
    </div>
    <div v-if="receiptDecision || custodyDecision" class="modal-backdrop show"></div>

    <div class="row g-4">
      <div class="col-xl-4">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">{{ t('finance.memberLookup') }}</h2>
              <span class="badge text-bg-light border text-dark">{{ members.length }} {{ t('finance.membersCountSuffix') }}</span>
            </div>

            <div class="mb-3">
              <label for="finance-member-search" class="form-label small fw-medium">{{ t('common.member') }}</label>
              <div class="position-relative mb-2">
                <input id="finance-member-search" v-model.trim="memberSearch" class="form-control" :placeholder="t('finance.memberSearchPlaceholder')" @focus="showMemberResults = true" />
                <div v-if="showMemberResults && memberSearch" class="list-group position-absolute w-100 shadow-sm finance-member-results">
                  <button v-for="member in filteredMembers.slice(0, 8)" :key="member.id" class="list-group-item list-group-item-action text-start" type="button" @click="selectFinanceMember(member)">
                    <span class="fw-semibold">{{ member.display_name }}</span><span class="small text-muted ms-2">{{ member.member_code }}</span>
                  </button>
                  <div v-if="filteredMembers.length === 0" class="list-group-item small text-muted">{{ t('finance.noMemberFound') }}</div>
                </div>
              </div>
              <select
                id="finance-balance-member"
                v-model="selectedMemberId"
                class="form-select"
                @change="selectFinanceMemberById"
              >
                <option value="">{{ t('finance.selectMember') }}</option>
                <option v-for="member in members" :key="member.id" :value="member.id">
                  {{ member.display_name }} ({{ member.member_code }})
                </option>
              </select>
            </div>

            <div v-if="selectedMemberBalance" class="border rounded-3 p-3 bg-light-subtle" data-testid="finance-member-balance">
              <div class="fw-semibold mb-1">{{ selectedMemberBalance.profile.display_name }}</div>
              <div class="small text-muted mb-3">{{ selectedMemberBalance.profile.member_code }}</div>
              <div class="row g-2 small">
                <div class="col-6">
                  <div class="text-muted">{{ t('contributions.expected') }}</div>
                  <div class="fw-semibold">{{ selectedMemberBalance.total_expected }} EUR</div>
                </div>
                <div class="col-6">
                  <div class="text-muted">{{ t('contributions.paid') }}</div>
                  <div class="fw-semibold">{{ selectedMemberBalance.total_paid }} EUR</div>
                </div>
                <div class="col-12">
                  <div class="text-muted">{{ t('contributions.balance') }}</div>
                  <div class="fw-semibold" :class="Number(selectedMemberBalance.total_balance) > 0 ? 'text-danger' : 'text-success'">
                    {{ selectedMemberBalance.total_balance }} EUR
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-muted small mb-0">
              {{ t('finance.selectMemberHint') }}
            </p>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-3">{{ t('finance.createContribution') }}</h2>
            <form class="vstack gap-3" @submit.prevent="handleCreateContribution">
              <div>
                <label for="finance-create-member" class="form-label small fw-medium">{{ t('common.member') }}</label>
                <select id="finance-create-member" v-model="createForm.membership_profile_id" class="form-select" required>
                  <option value="" disabled>{{ t('finance.selectMember') }}</option>
                  <option v-for="member in members" :key="member.id" :value="member.id">
                    {{ member.display_name }} ({{ member.member_code }})
                  </option>
                </select>
              </div>
              <div class="row g-2">
                <div class="col-6">
                  <label for="finance-create-year" class="form-label small fw-medium">{{ t('common.year') }}</label>
                  <input id="finance-create-year" v-model.number="createForm.year" type="number" class="form-control" min="2000" max="2100" required />
                </div>
                <div class="col-6">
                  <label for="finance-create-status" class="form-label small fw-medium">{{ t('common.status') }}</label>
                  <select id="finance-create-status" v-model="createForm.status" class="form-select">
                    <option value="pending">{{ copy.pending }}</option>
                    <option value="partial">{{ copy.partial }}</option>
                    <option value="paid">{{ copy.paid }}</option>
                    <option value="overdue">{{ copy.overdue }}</option>
                  </select>
                </div>
              </div>
              <div>
                <label for="finance-create-amount" class="form-label small fw-medium">{{ t('finance.expectedAmount') }} (EUR)</label>
                <input id="finance-create-amount" v-model="createForm.expected_amount" type="number" step="0.01" min="0" class="form-control" required />
              </div>
              <button class="btn btn-primary" type="submit" :disabled="savingContribution">
                {{ savingContribution ? t('common.saving') : t('finance.createContribution') }}
              </button>
            </form>
          </div>
        </div>
      </div>

      <div class="col-xl-8">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">{{ t('finance.recentPayments') }}</h2>
              <span class="badge text-bg-light border text-dark">{{ recentPayments.length }} {{ t('finance.itemsCountSuffix') }}</span>
            </div>

            <div v-if="recentPayments.length === 0" class="text-muted small mb-0">
              {{ t('finance.noPayments') }}
            </div>

            <div v-else class="list-group list-group-flush">
              <div v-for="payment in recentPayments" :key="payment.id" class="list-group-item px-0">
                <div class="d-flex justify-content-between gap-3">
                  <div>
                    <div class="fw-medium">{{ paymentMemberLabel(payment.contribution_record_id) }}</div>
                    <div class="small text-muted">
                      {{ payment.amount }} EUR · {{ formatPaymentMethod(payment.payment_method) }}
                    </div>
                  </div>
                  <div class="text-end small text-muted">
                    <div>{{ formatDate(payment.paid_at) }}</div>
                    <div>{{ payment.reference || t('finance.noReference') }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="remindersEnabled" class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <div>
                <h2 class="h6 fw-bold mb-0">{{ t('finance.reminders') }}</h2>
                <p class="text-muted small mb-0">{{ t('finance.remindersLead') }}</p>
              </div>
              <span class="badge text-bg-light border text-dark">{{ reminderHistory.length }} {{ t('finance.recentCountSuffix') }}</span>
            </div>

            <form class="row g-3 align-items-end mb-4" @submit.prevent="handleBatchReminder">
              <div class="col-md-4">
                <label for="finance-reminder-scope" class="form-label small fw-medium">{{ t('finance.dueScope') }}</label>
                <select id="finance-reminder-scope" v-model="reminderBatchForm.due_scope" class="form-select">
                  <option value="overdue">{{ t('finance.overdueOnly') }}</option>
                  <option value="due_soon">{{ t('finance.dueSoon') }}</option>
                  <option value="all_outstanding">{{ t('finance.allOutstanding') }}</option>
                </select>
              </div>
              <div class="col-md-4">
                <label for="finance-reminder-status" class="form-label small fw-medium">{{ t('finance.contributionStatus') }}</label>
                <select id="finance-reminder-status" v-model="reminderBatchForm.status" class="form-select">
                  <option value="">{{ t('finance.anyOutstanding') }}</option>
                  <option value="pending">{{ copy.pending }}</option>
                  <option value="partial">{{ copy.partial }}</option>
                  <option value="overdue">{{ copy.overdue }}</option>
                </select>
              </div>
              <div class="col-md-2">
                <label for="finance-reminder-limit" class="form-label small fw-medium">{{ t('finance.limit') }}</label>
                <input id="finance-reminder-limit" v-model.number="reminderBatchForm.limit" type="number" min="1" max="100" class="form-control" />
              </div>
              <div class="col-md-2 d-grid">
                <button class="btn btn-outline-primary" type="submit" :disabled="sendingBatchReminders">
                  {{ sendingBatchReminders ? t('finance.sending') : t('finance.sendBatch') }}
                </button>
              </div>
            </form>

            <div v-if="reminderHistory.length === 0" class="text-muted small mb-0">
              {{ t('finance.noReminders') }}
            </div>

            <div v-else class="list-group list-group-flush" data-testid="finance-reminder-history">
              <div v-for="reminder in reminderHistory" :key="reminder.id" class="list-group-item px-0">
                <div class="d-flex justify-content-between gap-3">
                  <div>
                    <div class="fw-medium">{{ reminder.member_display_name }} ({{ reminder.member_code }})</div>
                    <div class="small text-muted">{{ reminder.subject }}</div>
                    <div class="small text-muted">
                      {{ reminder.balance_snapshot }} EUR · {{ reminderStatusLabel(reminder.delivery_status) }}
                    </div>
                  </div>
                  <div class="text-end small text-muted">
                    <div>{{ formatDate(reminder.sent_at) }}</div>
                    <div>{{ reminder.provider_message || reminder.recipient }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">{{ t('contributions.recordPayment') }}</h2>
              <span v-if="paymentTarget" class="badge text-bg-light border text-dark">{{ paymentTarget.year }}</span>
            </div>

            <div v-if="paymentTarget" class="border rounded-3 p-3 bg-light-subtle">
              <div class="fw-semibold">{{ memberLabel(paymentTarget.membership_profile_id) }}</div>
              <div class="small text-muted mb-3">
                {{ paymentTargetCopy(paymentTarget.balance, paymentTarget.year) }}
              </div>
              <form class="row g-3 align-items-end" @submit.prevent="handleRecordPayment">
                <div class="col-md-4">
                  <label for="finance-payment-amount" class="form-label small fw-medium">{{ t('common.amount') }} (EUR)</label>
                  <input id="finance-payment-amount" v-model="paymentForm.amount" type="number" step="0.01" min="0.01" class="form-control" required />
                </div>
                <div class="col-md-4">
                  <label for="finance-payment-method" class="form-label small fw-medium">{{ t('contributions.paymentMethod') }}</label>
                  <select id="finance-payment-method" v-model="paymentForm.payment_method" class="form-select">
                    <option value="cash">{{ t('contributions.cash') }}</option>
                    <option value="bank_transfer">{{ t('contributions.bankTransfer') }}</option>
                    <option value="card">{{ t('finance.card') }}</option>
                    <option value="check">{{ t('contributions.check') }}</option>
                    <option value="other">{{ t('finance.other') }}</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label for="finance-payment-reference" class="form-label small fw-medium">{{ t('finance.reference') }}</label>
                  <input id="finance-payment-reference" v-model="paymentForm.reference" class="form-control" />
                </div>
                <div class="col-12 d-flex gap-2">
                  <button class="btn btn-primary" type="submit" :disabled="savingPayment">
                    {{ savingPayment ? t('common.saving') : t('contributions.recordPayment') }}
                  </button>
                  <button class="btn btn-outline-secondary" type="button" @click="resetPaymentForm">
                    {{ t('finance.clear') }}
                  </button>
                </div>
              </form>
            </div>
            <p v-else class="text-muted small mb-0">
              {{ t('finance.chooseContribution') }}
            </p>
          </div>
        </div>

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

        <ResponsiveDataView v-else :items="contributions" :aria-label="t('finance.tableAriaLabel')">
          <template #thead>
            <tr>
              <th class="ps-4" scope="col">{{ t('common.member') }}</th>
              <th scope="col">{{ t('common.year') }}</th>
              <th scope="col">{{ t('contributions.expected') }}</th>
              <th scope="col">{{ t('contributions.paid') }}</th>
              <th scope="col">{{ t('contributions.balance') }}</th>
              <th scope="col">{{ t('common.status') }}</th>
              <th scope="col">{{ t('finance.updated') }}</th>
              <th class="text-end pe-4" scope="col">{{ t('common.actions') }}</th>
            </tr>
          </template>
          <template #rows>
            <tr v-for="contribution in contributions" :key="contribution.id">
              <td class="ps-4"><div class="fw-medium">{{ memberLabel(contribution.membership_profile_id) }}</div><div class="small text-muted">{{ contribution.membership_profile_id.slice(0, 8) }}...</div></td>
              <td>{{ contribution.year }}</td>
              <td>{{ contribution.expected_amount }}</td>
              <td>{{ contribution.paid_amount }}</td>
              <td :class="Number(contribution.balance) > 0 ? 'text-danger fw-semibold' : 'text-success fw-semibold'">{{ contribution.balance }}</td>
              <td><span class="badge" :class="statusBadgeClass(contribution.status)">{{ contribution.status }}</span></td>
              <td class="small">{{ formatDate(contribution.updated_at) }}</td>
              <td class="text-end pe-4">
                <div class="d-flex justify-content-end gap-2">
                  <button class="btn btn-sm btn-outline-primary" type="button" @click="selectPaymentTarget(contribution)">{{ t('contributions.recordPayment') }}</button>
                  <button v-if="remindersEnabled && Number(contribution.balance) > 0" class="btn btn-sm btn-outline-secondary" type="button" :disabled="sendingSingleReminderId === contribution.id" @click="handleSingleReminder(contribution)">
                    {{ sendingSingleReminderId === contribution.id ? t('finance.sending') : t('finance.sendReminder') }}
                  </button>
                </div>
              </td>
            </tr>
          </template>
          <template #card="{ item: contribution }">
            <div class="d-flex align-items-start justify-content-between gap-3">
              <div class="min-w-0"><div class="fw-semibold">{{ memberLabel(contribution.membership_profile_id) }}</div><div class="small text-muted text-break">{{ contribution.membership_profile_id }}</div></div>
              <span class="badge" :class="statusBadgeClass(contribution.status)">{{ contribution.status }}</span>
            </div>
            <div class="row g-2 small mt-1">
              <div class="col-6"><div class="text-muted">{{ t('common.year') }}</div><div class="fw-semibold">{{ contribution.year }}</div></div>
              <div class="col-6"><div class="text-muted">{{ t('finance.updated') }}</div><div class="fw-semibold">{{ formatDate(contribution.updated_at) }}</div></div>
              <div class="col-4"><div class="text-muted">{{ t('contributions.expected') }}</div><div>{{ contribution.expected_amount }}</div></div>
              <div class="col-4"><div class="text-muted">{{ t('contributions.paid') }}</div><div>{{ contribution.paid_amount }}</div></div>
              <div class="col-4"><div class="text-muted">{{ t('contributions.balance') }}</div><div class="fw-semibold" :class="Number(contribution.balance) > 0 ? 'text-danger' : 'text-success'">{{ contribution.balance }}</div></div>
            </div>
            <div class="om-data-card-actions">
              <button class="btn btn-sm btn-outline-primary" type="button" @click="selectPaymentTarget(contribution)">{{ t('contributions.recordPayment') }}</button>
              <button v-if="remindersEnabled && Number(contribution.balance) > 0" class="btn btn-sm btn-outline-secondary" type="button" :disabled="sendingSingleReminderId === contribution.id" @click="handleSingleReminder(contribution)">
                {{ sendingSingleReminderId === contribution.id ? t('finance.sending') : t('finance.sendReminder') }}
              </button>
            </div>
          </template>
        </ResponsiveDataView>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  createExpense,
  createContribution,
  confirmContributionReceiptInTreasury,
  updateContributionReceiptHandoverReminder,
    exportMemberFinanceReport,
  getContributionSummary,
  getAnnualBudget,
  listContributions,
  listContributionReminders,
  listContributionReceiptDeclarations,
  listTenantPayments,
  recordPayment,
  processContributionReceiptDeclaration,
  sendContributionReminder,
  sendContributionReminderBatch,
  type ContributionReminderResponse,
  type ContributionRecordResponse,
  type ContributionSummary,
  type ContributionReceiptDeclarationResponse,
    type PaymentRecordResponse,
    type MemberFinanceExportFormat,
    type AnnualBudgetResponse,
    type BudgetCategoryTotal,
    type TreasuryExpenseCategory,
} from '@/api/contributions.api'
import {
  getMemberBalance,
  listMembers,
  type MemberBalanceResponse,
  type MembershipProfileResponse,
} from '@/api/membership.api'
import { useTenantStore } from '@/stores/tenant.store'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import { useRecoveryState } from '@/composables/useRecoveryState'
import ResponsiveDataView from '@/components/ui/ResponsiveDataView.vue'
import { computed, onMounted, ref } from 'vue'

const localeStore = useLocaleStore()
const t = (key: string) => localeStore.t(key)

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
const memberSearch = ref('')
const showMemberResults = ref(false)
const paymentTarget = ref<ContributionRecordResponse | null>(null)
const recentPayments = ref<PaymentRecordResponse[]>([])
const reminderHistory = ref<ContributionReminderResponse[]>([])
const tenantStore = useTenantStore()
const authStore = useAuthStore()
const allContributionRecords = ref<ContributionRecordResponse[]>([])
const receiptDeclarations = ref<ContributionReceiptDeclarationResponse[]>([])
const receiptDecision = ref<{ item: ContributionReceiptDeclarationResponse; action: 'validated' | 'rejected' } | null>(null)
const receiptDecisionNote = ref('')
const receiptReminderDays = ref(2)
const custodyDecision = ref<{ item: ContributionReceiptDeclarationResponse; action: 'reminder' | 'close' } | null>(null)
const custodyReminderDays = ref(2)
const custodyMethod = ref<'cash' | 'bank_transfer'>('cash')
const custodyNote = ref('')
const annualBudget = ref<AnnualBudgetResponse | null>(null)
const isTreasurer = computed(() => authStore.user?.roles.includes('treasurer') ?? false)
const canManageTreasury = computed(() => authStore.user?.roles.some((role) => ['treasurer', 'admin', 'principal_admin'].includes(role)) ?? false)

const currentYear = new Date().getFullYear()
const years = [currentYear - 1, currentYear, currentYear + 1]
const selectedYear = ref(currentYear)
const remindersEnabled = computed(() => tenantStore.isModuleEnabled('notifications'))
const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      pending: 'Ausstehend',
      partial: 'Teilweise',
      paid: 'Bezahlt',
      overdue: 'Überfällig',
      sent: 'Gesendet',
      simulated: 'Simuliert',
      failed: 'Fehlgeschlagen',
      skipped: 'Übersprungen',
      unknownMember: 'Unbekanntes Mitglied',
      outstandingFor: (balance: string, year: number) => `Offen ${balance} EUR für ${year}`,
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      pending: 'Pending',
      partial: 'Partial',
      paid: 'Paid',
      overdue: 'Overdue',
      sent: 'Sent',
      simulated: 'Simulated',
      failed: 'Failed',
      skipped: 'Skipped',
      unknownMember: 'Unknown member',
      outstandingFor: (balance: string, year: number) => `Outstanding ${balance} EUR for ${year}`,
    }
  }
  return {
    pending: 'En attente',
    partial: 'Partiel',
    paid: 'Payé',
    overdue: 'En retard',
    sent: 'Envoyé',
    simulated: 'Simulé',
    failed: 'Échoué',
    skipped: 'Ignoré',
    unknownMember: 'Membre inconnu',
    outstandingFor: (balance: string, year: number) => `Solde ouvert ${balance} EUR pour ${year}`,
  }
})
const noContributionRecordsLabel = computed(() => `${t('contributions.noRecords').replace('{year}', String(selectedYear.value))}`)

const createForm = ref({
  membership_profile_id: '',
  year: currentYear,
  expected_amount: '100.00',
  status: 'pending',
})

const paymentForm = ref({
  amount: '',
  payment_method: 'bank_transfer',
  reference: '',
})

const expenseCategories: TreasuryExpenseCategory[] = [
  'sport_equipment',
  'fuel_transport',
  'tournament',
  'cultural_event',
  'administration',
  'other',
]
const incomePalette = ['#2563a8', '#21a179', '#7a5af8', '#19a7ce', '#d38b18', '#546173']
const expensePalette = ['#d33a4c', '#e88924', '#8f3f9f', '#2f855a', '#4a6fa5', '#7a7f89']
const expenseForm = ref({
  category: 'sport_equipment' as TreasuryExpenseCategory,
  amount: '',
  spent_at: new Date().toISOString().slice(0, 10),
  description: '',
  payee: '',
  payment_method: 'cash',
  reference: '',
})

const reminderBatchForm = ref({
  due_scope: 'overdue' as 'all_outstanding' | 'overdue' | 'due_soon',
  status: '',
  limit: 25,
})

const membersById = computed(() =>
  Object.fromEntries(members.value.map((member) => [member.id, member])),
)

const filteredMembers = computed(() => {
  const query = memberSearch.value.toLocaleLowerCase()
  if (!query) return members.value
  return members.value.filter((member) =>
    `${member.display_name} ${member.first_name} ${member.last_name} ${member.member_code} ${member.phone || ''} ${member.email || ''}`
      .toLocaleLowerCase()
      .includes(query),
  )
})

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

function paymentMemberLabel(contributionId: string): string {
  const contribution = contributionsById.value[contributionId]
  if (!contribution) return copy.value.unknownMember
  return memberLabel(contribution.membership_profile_id)
}

function paymentTargetCopy(balance: string, year: number) {
  return copy.value.outstandingFor(balance, year)
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

function resetExpenseForm() {
  expenseForm.value = {
    category: 'sport_equipment',
    amount: '',
    spent_at: new Date().toISOString().slice(0, 10),
    description: '',
    payee: '',
    payment_method: 'cash',
    reference: '',
  }
}

async function handleCreateExpense() {
  savingExpense.value = true
  clearError()
  notice.value = ''
  try {
    await createExpense({
      category: expenseForm.value.category,
      amount: expenseForm.value.amount,
      spent_at: new Date(`${expenseForm.value.spent_at}T12:00:00`).toISOString(),
      description: expenseForm.value.description,
      payee: expenseForm.value.payee || null,
      payment_method: expenseForm.value.payment_method,
      reference: expenseForm.value.reference || null,
    })
    resetExpenseForm()
    notice.value = t('finance.expenseRecorded')
    await refreshFinanceData()
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('common.error')
  } finally {
    savingExpense.value = false
  }
}

async function loadSelectedMemberBalance() {
  if (!selectedMemberId.value) {
    selectedMemberBalance.value = null
    return
  }
  selectedMemberBalance.value = await getMemberBalance(selectedMemberId.value)
}

function selectFinanceMember(member: MembershipProfileResponse) {
  selectedMemberId.value = member.id
  memberSearch.value = member.display_name
  showMemberResults.value = false
  void loadSelectedMemberBalance()
}

function selectFinanceMemberById() {
  const member = members.value.find((item) => item.id === selectedMemberId.value)
  if (member) selectFinanceMember(member)
  else void loadSelectedMemberBalance()
}

async function processReceiptDeclaration(
  item: ContributionReceiptDeclarationResponse,
  action: 'validated' | 'rejected',
) {
  clearError()
  const contribution = allContributionRecords.value.find(
    (row) => row.membership_profile_id === item.membership_profile_id && Number(row.balance) > 0,
  )
  if (action === 'validated' && item.income_type === 'membership_contribution' && !contribution) {
    error.value = t('finance.noOutstandingContribution')
    return
  }
  try {
    await processContributionReceiptDeclaration(
      item.id,
      action === 'validated'
        ? { action, handover_reminder_days: receiptReminderDays.value, ...(item.income_type === 'membership_contribution' ? { contribution_record_id: contribution!.id } : {}) }
        : { action, note: t('finance.receiptRejectedNote') },
    )
    notice.value = action === 'validated' ? t('finance.receiptValidated') : t('finance.receiptRejected')
    await refreshAll()
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('finance.receiptProcessingFailed')
  }
}

function openReceiptDecision(item: ContributionReceiptDeclarationResponse, action: 'validated' | 'rejected') {
  receiptDecision.value = { item, action }
  receiptDecisionNote.value = ''
  receiptReminderDays.value = 2
}
function closeReceiptDecision() { receiptDecision.value = null; receiptDecisionNote.value = '' }
async function confirmReceiptDecision() {
  if (!receiptDecision.value) return
  const { item, action } = receiptDecision.value
  if (action === 'rejected' && !receiptDecisionNote.value) return
  const note = receiptDecisionNote.value
  closeReceiptDecision()
  await processReceiptDeclarationWithNote(item, action, action === 'rejected' ? note : undefined)
}
async function processReceiptDeclarationWithNote(item: ContributionReceiptDeclarationResponse, action: 'validated' | 'rejected', rejectionNote?: string) {
  clearError()
  const contribution = allContributionRecords.value.find((row) => row.membership_profile_id === item.membership_profile_id && Number(row.balance) > 0)
  if (action === 'validated' && item.income_type === 'membership_contribution' && !contribution) { error.value = t('finance.noOutstandingContribution'); return }
  try {
    await processContributionReceiptDeclaration(item.id, action === 'validated' ? { action, handover_reminder_days: receiptReminderDays.value, ...(item.income_type === 'membership_contribution' ? { contribution_record_id: contribution!.id } : {}) } : { action, note: rejectionNote || t('finance.receiptRejectedNote') })
    notice.value = action === 'validated' ? t('finance.receiptValidated') : t('finance.receiptRejected')
    await refreshAll()
  } catch (err) { error.value = err instanceof Error ? err.message : t('finance.receiptProcessingFailed') }
}
function openCustodyDecision(item: ContributionReceiptDeclarationResponse, action: 'reminder' | 'close') {
  custodyDecision.value = { item, action }
  custodyReminderDays.value = item.handover_reminder_days || 2
  custodyMethod.value = item.handover_method === 'bank_transfer' ? 'bank_transfer' : 'cash'
  custodyNote.value = ''
}
function closeCustodyDecision() {
  custodyDecision.value = null
  custodyNote.value = ''
}
async function confirmCustodyDecision() {
  if (!custodyDecision.value) return
  const { item, action } = custodyDecision.value
  clearError()
  try {
    if (action === 'reminder') {
      await updateContributionReceiptHandoverReminder(item.id, { reminder_days: custodyReminderDays.value })
      notice.value = t('receipt.reminderUpdated')
    } else {
      await confirmContributionReceiptInTreasury(item.id, { method: custodyMethod.value, note: custodyNote.value || null })
      notice.value = t('receipt.treasuryReceived')
    }
    closeCustodyDecision()
    await refreshAll()
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('finance.receiptProcessingFailed')
  }
}
function handoverStatusLabel(value: ContributionReceiptDeclarationResponse['cash_handover_status']) {
  return value === 'handover_reported' ? t('receipt.handoverReported') : value === 'received_in_treasury' ? t('receipt.treasuryReceived') : t('receipt.cashPending')
}

function receiptIncomeTypeLabel(incomeType: ContributionReceiptDeclarationResponse['income_type']) {
  const keys = {
    membership_contribution: 'receipt.incomeType.membershipContribution', donation: 'receipt.incomeType.donation', sponsorship: 'receipt.incomeType.sponsorship', tournament_proceeds: 'receipt.incomeType.tournamentProceeds', other_income: 'receipt.incomeType.otherIncome', disciplinary_payment: 'receipt.incomeType.disciplinaryPayment',
  } as const
  return t(keys[incomeType])
}

function receiptDeclarationLabel(item: ContributionReceiptDeclarationResponse) {
  return item.income_type === 'membership_contribution'
    ? memberLabel(item.membership_profile_id!)
    : (item.source_name || t('receipt.externalIncome'))
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
    const summary = await (await exportMemberFinanceReport('whatsapp', selectedYear.value)).text()
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(summary)
      notice.value = t('finance.whatsappCopied')
    } else {
      downloadBlob(new Blob([summary], { type: 'text/plain;charset=utf-8' }), `rapport-financier-${selectedYear.value}-whatsapp.txt`)
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

async function handleBatchReminder() {
  sendingBatchReminders.value = true
  clearError()
  notice.value = ''
  try {
    const result = await sendContributionReminderBatch({
      year: selectedYear.value,
      due_scope: reminderBatchForm.value.due_scope,
      limit: reminderBatchForm.value.limit,
      ...(reminderBatchForm.value.status ? { status: reminderBatchForm.value.status } : {}),
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
  createForm.value = {
    membership_profile_id: '',
    year: selectedYear.value,
    expected_amount: '100.00',
    status: 'pending',
  }
}

function selectPaymentTarget(contribution: ContributionRecordResponse) {
  paymentTarget.value = contribution
  paymentForm.value.amount = contribution.balance
  paymentForm.value.payment_method = 'bank_transfer'
  paymentForm.value.reference = ''
}

function resetPaymentForm() {
  paymentTarget.value = null
  paymentForm.value = {
    amount: '',
    payment_method: 'bank_transfer',
    reference: '',
  }
}

async function handleCreateContribution() {
  savingContribution.value = true
  clearError()
  try {
    await createContribution({
      membership_profile_id: createForm.value.membership_profile_id,
      year: createForm.value.year,
      expected_amount: createForm.value.expected_amount,
      paid_amount: '0.00',
      status: createForm.value.status,
    })
    resetCreateForm()
    await refreshAll()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to create the contribution record.'
  } finally {
    savingContribution.value = false
  }
}

async function handleRecordPayment() {
  if (!paymentTarget.value) return

  savingPayment.value = true
  clearError()
  try {
    await recordPayment({
      contribution_record_id: paymentTarget.value.id,
      amount: paymentForm.value.amount,
      payment_method: paymentForm.value.payment_method,
      reference: paymentForm.value.reference || null,
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

onMounted(async () => {
  members.value = await listMembers()
  resetCreateForm()
  await refreshAll()
})
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
.expense-entry-card { border-top: 4px solid #d33a4c !important; background: linear-gradient(150deg, #fff 0%, #fff8f8 100%); }
.recent-expenses-card { border-top: 4px solid #e88924 !important; }
.recent-expense-item { display: flex; gap: 0.8rem; align-items: flex-start; padding: 0.85rem; border: 1px solid #e7eaf0; border-radius: 0.85rem; background: #fff; }
.expense-category-icon { display: grid; place-items: center; flex: 0 0 2.25rem; width: 2.25rem; height: 2.25rem; border-radius: 0.75rem; background: #fff0f1; color: #c92f42; }

.receipt-queue { border-top: 4px solid var(--bs-warning); }
.receipt-queue-item { background: var(--bs-warning-bg-subtle); border: 1px solid #f0d38a; }
.custody-workspace { border-top: 4px solid var(--bs-primary); background: linear-gradient(135deg, #fff 0%, #f5f9ff 100%); }
.custody-card { border: 1px solid #d9e3f2; box-shadow: 0 0.35rem 1.1rem rgba(24, 62, 111, 0.07); }
.custody-card-pending { background: linear-gradient(135deg, #fffdf6 0%, #fff 58%); border-left: 5px solid var(--bs-warning); }
.custody-card-reported { background: linear-gradient(135deg, #f2fbff 0%, #fff 58%); border-left: 5px solid var(--bs-info); }
.custody-meta-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.75rem; }
.custody-meta-grid > div { display: grid; gap: 0.15rem; padding: 0.65rem 0.75rem; border-radius: 0.75rem; background: rgba(255, 255, 255, 0.82); border: 1px solid #e3e9f2; }
.custody-meta-grid span { color: var(--bs-secondary); }
.custody-actions { display: grid; gap: 0.5rem; min-width: 12.5rem; }
.finance-member-results { z-index: 1040; max-height: 17rem; overflow-y: auto; }

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

  .custody-meta-grid { grid-template-columns: 1fr; }
  .custody-actions { width: 100%; min-width: 0; }
  .custody-actions .btn { min-height: 44px; }
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
