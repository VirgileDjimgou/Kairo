<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          Discipline
        </div>
        <h1 class="h4 fw-bold mb-1">My disciplinary records</h1>
        <p class="text-muted mb-0">
          Review any open, resolved, or waived records linked to your profile.
        </p>
      </div>
      <button class="btn om-primary-btn align-self-start" type="button" @click="refreshRecords" :disabled="loading">
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <div v-if="loading" class="text-muted py-5 text-center">
      Loading disciplinary records...
    </div>

    <div v-else-if="records.length === 0" class="empty-state">
      <i class="bi bi-shield-check display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">No records found</p>
      <p class="text-muted mb-0">
        You currently have no disciplinary records for this tenant.
      </p>
    </div>

    <div v-else class="row g-3">
      <div v-for="record in records" :key="record.id" class="col-md-6 col-xl-4">
        <article class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <div class="d-flex align-items-start justify-content-between gap-3 mb-3">
              <div>
                <h2 class="h6 fw-bold mb-1">{{ record.title }}</h2>
                <div class="small text-muted">
                  {{ record.policy_title || 'No linked policy' }}
                </div>
              </div>
              <span class="badge" :class="statusClass(record.status)">
                {{ record.status }}
              </span>
            </div>

            <p class="text-muted small mb-3">
              {{ record.description || 'No description provided.' }}
            </p>

            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Amount</span>
                <span class="fw-semibold">{{ record.amount }} {{ record.currency }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Recorded</span>
                <span class="fw-medium">{{ formatDate(record.recorded_at) }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Linked profile</span>
                <span class="fw-medium text-end">{{ record.membership_display_name || record.membership_profile_id }}</span>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listMyDisciplinaryRecords, type DisciplinaryRecordResponse } from '@/api/disciplinary.api'

const loading = ref(true)
const records = ref<DisciplinaryRecordResponse[]>([])

function statusClass(status: string): string {
  const map: Record<string, string> = {
    open: 'bg-danger-subtle text-danger border border-danger-subtle',
    under_review: 'bg-warning-subtle text-warning border border-warning-subtle',
    resolved: 'bg-success-subtle text-success border border-success-subtle',
    waived: 'bg-secondary-subtle text-secondary border border-secondary-subtle',
  }
  return map[status] || 'bg-light text-dark border'
}

async function refreshRecords() {
  loading.value = true
  try {
    records.value = await listMyDisciplinaryRecords()
  } finally {
    loading.value = false
  }
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString()
}

onMounted(refreshRecords)
</script>
