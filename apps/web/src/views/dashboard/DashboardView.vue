<template>
  <div class="p-3 p-md-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row align-items-lg-end justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary-emphasis mb-2">
          {{ dashboardKicker }}
        </div>
        <h1 class="h4 fw-bold mb-1">{{ copy.welcomeBack }}, {{ authStore.user?.display_name }}</h1>
        <p class="text-muted mb-0">
          {{ dashboardLead }}
        </p>
      </div>
      <span
        class="badge px-3 py-2"
        :class="isSetupMode ? 'bg-warning-subtle text-warning-emphasis border border-warning-subtle' : 'bg-success-subtle text-success-emphasis border border-success-subtle'"
      >
        <i class="bi bi-circle-fill me-1" style="font-size: 0.5rem"></i>
        {{ isSetupMode ? copy.setupMode : copy.operational }}
      </span>
    </div>

    <DemoTourPanel />

    <AttentionCenter />

    <div v-if="loading" class="alert alert-info border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex gap-3">
        <div class="spinner-border spinner-border-sm mt-1" role="status" aria-hidden="true"></div>
        <div>
          <h6 class="alert-heading mb-1">{{ copy.loadingTitle }}</h6>
          <p class="mb-0 small">
            {{ copy.loadingBody }}
          </p>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <WorkspaceFocusCard v-else :focus="workspaceFocus" />

    <div class="row g-4">
      <div class="col-lg-8">
        <OnboardingChecklistCard
          :copy="copy"
          :status-title="statusTitle"
          :status-message="statusMessage"
          :progress-percent="progressPercent"
          :checklist="checklist"
          :next-step="nextStep"
        />
      </div>

      <div class="col-lg-4">
        <TenantSnapshotCard
          :copy="copy"
          :metrics="summaryMetrics"
          :tenant-name="tenantStore.currentTenantName"
          :roles-label="authStore.user?.roles.join(', ') || ''"
          :completed-count="completedCount"
          :checklist-length="checklist.length"
          :last-refreshed-at="lastRefreshedAt"
          :loading="loading"
          @refresh="refresh"
        />

        <QuickActionsCard :copy="copy" :actions="filteredQuickActions" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useTenantStore } from '@/stores/tenant.store'
import { useTenantOnboarding } from '@/composables/useTenantOnboarding'
import DemoTourPanel from '@/components/DemoTourPanel.vue'
import AttentionCenter from '@/components/attention/AttentionCenter.vue'
import WorkspaceFocusCard from '@/features/dashboard/components/WorkspaceFocusCard.vue'
import OnboardingChecklistCard from '@/features/dashboard/components/OnboardingChecklistCard.vue'
import TenantSnapshotCard from '@/features/dashboard/components/TenantSnapshotCard.vue'
import QuickActionsCard from '@/features/dashboard/components/QuickActionsCard.vue'
import { useDashboardRoles } from '@/features/dashboard/composables/useDashboardRoles'
import { useDashboardCopy } from '@/features/dashboard/composables/useDashboardCopy'
import { useWorkspaceFocus } from '@/features/dashboard/composables/useWorkspaceFocus'
import { useDashboardQuickActions } from '@/features/dashboard/composables/useDashboardQuickActions'

const authStore = useAuthStore()
const tenantStore = useTenantStore()

const roles = useDashboardRoles()
const { copy, dashboardKicker, dashboardLead } = useDashboardCopy(roles)
const workspaceFocus = useWorkspaceFocus(roles)
const { filteredQuickActions } = useDashboardQuickActions(roles)

const {
  loading,
  error,
  checklist,
  completedCount,
  progressPercent,
  statusTitle,
  statusMessage,
  summaryMetrics,
  nextStep,
  lastRefreshedAt,
  refresh,
} = useTenantOnboarding()

const isSetupMode = computed(() => {
  return progressPercent.value < 100 && completedCount.value === 0
})

onMounted(refresh)
</script>
