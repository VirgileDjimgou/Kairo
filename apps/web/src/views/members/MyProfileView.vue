<template>
  <div class="p-4 p-lg-5 member-self-service">
    <div class="hero-card rounded-4 p-4 p-lg-5 mb-4">
      <div class="d-flex flex-column flex-lg-row justify-content-between gap-4">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-2">
            Member self-service
          </div>
          <h1 class="h3 fw-bold mb-2">My profile and contribution statement</h1>
          <p class="text-muted mb-0 hero-copy">
            Review your personal details, check your current balance, and download your own PDF statement.
          </p>
        </div>

        <div class="d-flex align-items-start">
          <button
            class="btn btn-primary"
            type="button"
            @click="handleDownloadPdf"
            :disabled="downloadingPdf || !statement"
          >
            <span
              v-if="downloadingPdf"
              class="spinner-border spinner-border-sm me-2"
              role="status"
              aria-hidden="true"
            ></span>
            <i v-else class="bi bi-file-earmark-pdf me-2"></i>
            {{ downloadingPdf ? 'Preparing PDF...' : 'Download my statement' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="alert alert-info border-0 shadow-sm" role="alert">
      <div class="d-flex gap-3">
        <div class="spinner-border spinner-border-sm mt-1" role="status" aria-hidden="true"></div>
        <div>
          <h6 class="alert-heading mb-1">Loading your member workspace</h6>
          <p class="mb-0 small">We are fetching your personal profile and contribution history.</p>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-warning border-0 shadow-sm" role="alert">
      <i class="bi bi-info-circle me-2"></i>{{ error }}
    </div>

    <template v-else-if="statement">
      <div class="row g-4 mb-4">
        <div class="col-xl-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <div class="d-flex align-items-center gap-3 mb-3">
                <div class="icon-tile">
                  <i class="bi bi-person-badge fs-4"></i>
                </div>
                <div>
                  <div class="fw-semibold">{{ statement.profile.display_name }}</div>
                  <div class="small text-muted">{{ statement.profile.member_code }}</div>
                </div>
              </div>

              <hr />

              <dl class="row small mb-0 profile-grid">
                <dt class="col-sm-5 text-muted">First name</dt>
                <dd class="col-sm-7">{{ statement.profile.first_name }}</dd>

                <dt class="col-sm-5 text-muted">Last name</dt>
                <dd class="col-sm-7">{{ statement.profile.last_name }}</dd>

                <dt class="col-sm-5 text-muted">Email</dt>
                <dd class="col-sm-7">{{ statement.profile.email || '—' }}</dd>

                <dt class="col-sm-5 text-muted">Phone</dt>
                <dd class="col-sm-7">{{ statement.profile.phone || '—' }}</dd>

                <dt class="col-sm-5 text-muted">Status</dt>
                <dd class="col-sm-7">
                  <span class="badge rounded-pill text-bg-success" v-if="statement.profile.status === 'active'">
                    Active
                  </span>
                  <span class="badge rounded-pill text-bg-secondary" v-else>
                    {{ statement.profile.status }}
                  </span>
                </dd>

                <dt class="col-sm-5 text-muted">Joined</dt>
                <dd class="col-sm-7">{{ formatDate(statement.profile.joined_at) }}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="col-xl-8">
          <div class="row g-3">
            <div class="col-md-4">
              <div class="metric-card metric-neutral h-100">
                <div class="metric-label">Expected</div>
                <div class="metric-value">{{ statement.summary.total_expected }}</div>
                <div class="metric-foot">EUR</div>
              </div>
            </div>

            <div class="col-md-4">
              <div class="metric-card metric-success h-100">
                <div class="metric-label">Paid</div>
                <div class="metric-value">{{ statement.summary.total_paid }}</div>
                <div class="metric-foot">EUR</div>
              </div>
            </div>

            <div class="col-md-4">
              <div class="metric-card h-100" :class="balanceToneClass">
                <div class="metric-label">Outstanding balance</div>
                <div class="metric-value">{{ statement.summary.total_balance }}</div>
                <div class="metric-foot">
                  {{ statement.summary.contribution_count }} contribution record<span v-if="statement.summary.contribution_count !== 1">s</span>
                </div>
              </div>
            </div>
          </div>

          <div class="card border-0 shadow-sm mt-4">
            <div class="card-body p-4">
              <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
                <div>
                  <div class="text-uppercase small fw-semibold text-secondary mb-1">
                    Contribution history
                  </div>
                  <h2 class="h6 fw-bold mb-0">Your personal records only</h2>
                </div>
                <div class="small text-muted">
                  This area never exposes another member's financial data.
                </div>
              </div>

              <div v-if="statement.contributions.length === 0" class="empty-state rounded-4 p-4 text-center">
                <i class="bi bi-journal-text fs-3 d-block mb-2 text-secondary"></i>
                <div class="fw-semibold mb-1">No contribution records yet</div>
                <p class="text-muted small mb-0">
                  Your organization has not published personal contribution records for your account yet.
                </p>
              </div>

              <div v-else class="table-responsive">
                <table class="table align-middle mb-0" aria-label="Personal contribution history">
                  <thead>
                    <tr>
                      <th scope="col">Year</th>
                      <th scope="col">Expected</th>
                      <th scope="col">Paid</th>
                      <th scope="col">Balance</th>
                      <th scope="col">Status</th>
                      <th scope="col">Due date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="contribution in statement.contributions" :key="contribution.id">
                      <td class="fw-semibold">{{ contribution.year }}</td>
                      <td>{{ contribution.expected_amount }} {{ contribution.currency }}</td>
                      <td class="text-success fw-medium">{{ contribution.paid_amount }} {{ contribution.currency }}</td>
                      <td :class="Number(contribution.balance) > 0 ? 'text-danger fw-semibold' : 'text-success fw-semibold'">
                        {{ contribution.balance }} {{ contribution.currency }}
                      </td>
                      <td>
                        <span class="badge rounded-pill" :class="statusBadgeClass(contribution.status)">
                          {{ formatStatus(contribution.status) }}
                        </span>
                      </td>
                      <td>{{ contribution.due_date ? formatDate(contribution.due_date) : '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  downloadMyStatementPdf,
  getMyStatement,
  type MemberStatementResponse,
} from '@/api/membership.api'

const loading = ref(true)
const downloadingPdf = ref(false)
const error = ref<string | null>(null)
const statement = ref<MemberStatementResponse | null>(null)

const balanceToneClass = computed(() => {
  if (!statement.value) {
    return 'metric-neutral'
  }
  return Number(statement.value.summary.total_balance) > 0 ? 'metric-warning' : 'metric-success'
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function formatStatus(status: string): string {
  return status.replace('_', ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}

function statusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    paid: 'bg-success-subtle text-success border border-success-subtle',
    partial: 'bg-warning-subtle text-warning border border-warning-subtle',
    overdue: 'bg-danger-subtle text-danger border border-danger-subtle',
    waived: 'bg-secondary-subtle text-secondary border border-secondary-subtle',
    pending: 'bg-light text-dark border',
  }

  return classes[status] || 'bg-light text-dark border'
}

async function loadStatement() {
  loading.value = true

  try {
    statement.value = await getMyStatement()
    error.value = null
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Could not load your personal statement'
  } finally {
    loading.value = false
  }
}

async function handleDownloadPdf() {
  if (!statement.value || downloadingPdf.value) {
    return
  }

  downloadingPdf.value = true

  try {
    const pdfBlob = await downloadMyStatementPdf()
    const url = window.URL.createObjectURL(pdfBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `kairo-statement-${statement.value.profile.member_code}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Could not download your PDF statement'
  } finally {
    downloadingPdf.value = false
  }
}

onMounted(loadStatement)
</script>

<style scoped>
.member-self-service {
  max-width: 1180px;
}

.hero-card {
  background:
    radial-gradient(circle at top right, rgba(185, 212, 255, 0.45), transparent 30%),
    linear-gradient(135deg, #f7f4ee 0%, #ffffff 65%);
  border: 1px solid #e2ddd3;
}

.hero-copy {
  max-width: 42rem;
}

.icon-tile {
  width: 3.25rem;
  height: 3.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
  background: #eef3f8;
  color: #215d91;
}

.metric-card {
  border-radius: 1.25rem;
  padding: 1.25rem;
  border: 1px solid #dde5ec;
  background: #fff;
}

.metric-neutral {
  background: #f8fafc;
}

.metric-success {
  background: #eef9f1;
}

.metric-warning {
  background: #fff4e8;
}

.metric-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #667085;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 1.9rem;
  font-weight: 700;
  line-height: 1.05;
  margin-bottom: 0.35rem;
}

.metric-foot {
  font-size: 0.875rem;
  color: #667085;
}

.empty-state {
  background: #f8fafc;
  border: 1px dashed #c8d2dc;
}

.profile-grid dt,
.profile-grid dd {
  margin-bottom: 0.65rem;
}
</style>
