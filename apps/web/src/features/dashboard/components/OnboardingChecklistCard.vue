<template>
  <div class="card shadow-sm border-0 onboarding-card h-100" data-testid="tenant-onboarding">
    <div class="card-body p-3 p-md-4 p-lg-5">
      <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-4">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary-emphasis mb-2">
            {{ copy.firstRunChecklist }}
          </div>
          <h2 class="h5 fw-bold mb-2">{{ statusTitle }}</h2>
          <p class="text-muted mb-0">
            {{ statusMessage }}
          </p>
        </div>
        <div class="text-md-end">
          <div
            class="display-6 fw-bold lh-1"
            data-testid="tenant-onboarding-progress"
          >
            {{ progressPercent }}%
          </div>
          <div class="small text-muted">{{ copy.complete }}</div>
        </div>
      </div>

      <div class="progress mb-4" style="height: 0.75rem">
        <div
          class="progress-bar"
          role="progressbar"
          :aria-label="copy.checklistProgress"
          :aria-valuenow="progressPercent"
          aria-valuemin="0"
          aria-valuemax="100"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>

      <div v-if="nextStep" class="alert alert-primary border-0 mb-4">
        <div class="d-flex align-items-start gap-3">
          <i class="bi bi-arrow-right-circle fs-4 flex-shrink-0"></i>
          <div>
            <div class="fw-semibold mb-1">{{ copy.nextBestAction }}</div>
            <p class="mb-2 small">
              {{ nextStep.title }}: {{ nextStep.description }}
            </p>
            <RouterLink :to="nextStep.to" class="btn btn-sm btn-primary">
              {{ nextStep.actionLabel }}
            </RouterLink>
          </div>
        </div>
      </div>

      <div class="vstack gap-3">
        <article
          v-for="step in checklist"
          :key="step.id"
          class="checklist-item"
          :class="{ completed: step.completed }"
        >
          <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
            <div class="d-flex gap-3">
              <div class="step-icon" :class="{ completed: step.completed }">
                <i :class="step.completed ? 'bi bi-check2' : stepIcon(step.id)"></i>
              </div>
              <div>
                <div class="fw-semibold mb-1">{{ step.title }}</div>
                <p class="small text-muted mb-0">{{ step.description }}</p>
              </div>
            </div>

            <div class="text-md-end">
              <span
                class="badge mb-2"
                :class="step.completed ? 'bg-success-subtle text-success-emphasis border border-success-subtle' : 'bg-secondary-subtle text-secondary-emphasis border border-secondary-subtle'"
              >
                {{ step.completed ? copy.completed : copy.pending }}
              </span>
              <div>
                <RouterLink :to="step.to" class="btn btn-sm btn-outline-primary">
                  {{ step.actionLabel }}
                </RouterLink>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { OnboardingStep } from '@/composables/useTenantOnboarding'
import type { DashboardCopy } from '../composables/useDashboardCopy'

defineProps<{
  copy: DashboardCopy
  statusTitle: string
  statusMessage: string
  progressPercent: number
  checklist: OnboardingStep[]
  nextStep: OnboardingStep | null
}>()

function stepIcon(stepId: string): string {
  const map: Record<string, string> = {
    branding: 'bi bi-palette',
    documents: 'bi bi-file-earmark-text',
    members: 'bi bi-people',
    announcements: 'bi bi-megaphone',
    events: 'bi bi-calendar-event',
  }

  return map[stepId] || 'bi bi-arrow-right'
}
</script>

<style scoped>
.onboarding-card {
  border-radius: 1.25rem;
}

.checklist-item {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: #fff;
  padding: 1rem;
}

.checklist-item.completed {
  background: linear-gradient(180deg, rgba(25, 135, 84, 0.03), rgba(25, 135, 84, 0.01));
}

.step-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(31, 79, 143, 0.08);
  color: var(--om-primary, #1f4f8f);
  flex-shrink: 0;
}

.step-icon.completed {
  background: rgba(25, 135, 84, 0.12);
  color: #198754;
}
</style>
