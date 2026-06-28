<template>
  <div class="p-4">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-0">My Profile</h1>
        <p class="text-muted small mb-0">Your member information and balance</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-warning border-0 shadow-sm">
      <i class="bi bi-info-circle me-2"></i>{{ error }}
    </div>

    <template v-else-if="profile">
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <div class="card shadow-sm border-0 h-100">
            <div class="card-body">
              <div class="d-flex align-items-center gap-3 mb-3">
                <div class="bg-primary-subtle text-primary rounded-3 p-3">
                  <i class="bi bi-person-badge fs-4"></i>
                </div>
                <div>
                  <div class="fw-semibold">{{ profile.display_name }}</div>
                  <div class="small text-muted">{{ profile.member_code }}</div>
                </div>
              </div>
              <hr />
              <dl class="row small mb-0">
                <dt class="col-sm-5 text-muted">First name</dt>
                <dd class="col-sm-7">{{ profile.first_name }}</dd>
                <dt class="col-sm-5 text-muted">Last name</dt>
                <dd class="col-sm-7">{{ profile.last_name }}</dd>
                <dt class="col-sm-5 text-muted">Email</dt>
                <dd class="col-sm-7">{{ profile.email || '—' }}</dd>
                <dt class="col-sm-5 text-muted">Phone</dt>
                <dd class="col-sm-7">{{ profile.phone || '—' }}</dd>
                <dt class="col-sm-5 text-muted">Status</dt>
                <dd class="col-sm-7">
                  <span class="badge"
                    :class="profile.status === 'active' ? 'bg-success' : 'bg-secondary'">
                    {{ profile.status }}
                  </span>
                </dd>
                <dt class="col-sm-5 text-muted">Joined</dt>
                <dd class="col-sm-7">{{ formatDate(profile.joined_at) }}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div class="col-md-8">
          <div class="card shadow-sm border-0 h-100">
            <div class="card-header bg-transparent border-bottom py-3">
              <h5 class="mb-0 fw-semibold">Contribution Balance</h5>
            </div>
            <div class="card-body">
              <div v-if="loadingBalance" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div v-else-if="balanceError" class="alert alert-warning border-0 py-2 small">
                {{ balanceError }}
              </div>
              <div v-else-if="balance" class="row g-3">
                <div class="col-4 text-center">
                  <div class="text-muted small">Expected</div>
                  <div class="fw-bold fs-5">{{ balance.total_expected }}</div>
                  <div class="text-muted small">EUR</div>
                </div>
                <div class="col-4 text-center">
                  <div class="text-muted small">Paid</div>
                  <div class="fw-bold fs-5 text-success">{{ balance.total_paid }}</div>
                  <div class="text-muted small">EUR</div>
                </div>
                <div class="col-4 text-center">
                  <div class="text-muted small">Balance</div>
                  <div class="fw-bold fs-5"
                    :class="Number(balance.total_balance) > 0 ? 'text-danger' : 'text-success'">
                    {{ balance.total_balance }}
                  </div>
                  <div class="text-muted small">EUR</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMyProfile, getMyBalance } from '@/api/membership.api'
import type { MembershipProfileResponse, MemberBalanceResponse } from '@/api/membership.api'

const loading = ref(true)
const error = ref<string | null>(null)
const profile = ref<MembershipProfileResponse | null>(null)
const balance = ref<MemberBalanceResponse | null>(null)
const loadingBalance = ref(true)
const balanceError = ref<string | null>(null)

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(async () => {
  try {
    profile.value = await getMyProfile()
    error.value = null
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Could not load profile'
  } finally {
    loading.value = false
  }

  try {
    balance.value = await getMyBalance()
    balanceError.value = null
  } catch (err: any) {
    balanceError.value = err?.response?.data?.detail || 'Could not load balance'
  } finally {
    loadingBalance.value = false
  }
})
</script>
