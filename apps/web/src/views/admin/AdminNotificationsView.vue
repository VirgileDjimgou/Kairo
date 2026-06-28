<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          Multi-channel
        </div>
        <h1 class="h4 fw-bold mb-1">Notification extensions</h1>
        <p class="text-muted mb-0">
          Validate optional Email, Telegram, and WhatsApp channels without changing the web-first core flow.
        </p>
      </div>
      <button class="btn om-primary-btn align-self-start" type="button" @click="refreshData" :disabled="loading">
        {{ loading ? 'Refreshing...' : 'Refresh channels' }}
      </button>
    </div>

    <div class="row g-3 mb-4">
      <div v-for="channel in channels" :key="channel.channel" class="col-md-6 col-xl-4">
        <article class="card shadow-sm border-0 h-100 channel-card">
          <div class="card-body p-4">
            <div class="d-flex align-items-start justify-content-between gap-3 mb-3">
              <div>
                <h2 class="h6 fw-bold mb-1">{{ channel.display_name }}</h2>
                <div class="small text-muted">{{ channel.channel }}</div>
              </div>
              <span class="badge" :class="channel.configured ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-secondary-subtle text-secondary border border-secondary-subtle'">
                {{ channel.configured ? 'Configured' : 'Placeholder' }}
              </span>
            </div>

            <p class="text-muted small mb-3">{{ channel.description }}</p>

            <div class="small d-flex justify-content-between gap-2 mb-2">
              <span class="text-muted">Target hint</span>
              <span class="fw-medium text-end">{{ channel.target_hint }}</span>
            </div>
            <div class="small d-flex justify-content-between gap-2">
              <span class="text-muted">Delivery mode</span>
              <span class="fw-medium text-end">
                {{ channel.simulation_only ? 'Simulation only' : 'Live capable' }}
              </span>
            </div>
          </div>
        </article>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-body p-4">
        <div class="d-flex align-items-center justify-content-between gap-3 mb-3">
          <div>
            <h2 class="h6 fw-bold mb-1">Send test notification</h2>
            <p class="text-muted small mb-0">
              Dispatches a simulated message through the selected optional providers.
            </p>
          </div>
          <span class="badge bg-warning-subtle text-warning border border-warning-subtle">
            No external delivery
          </span>
        </div>

        <div v-if="loading" class="text-muted py-4 text-center">Loading channels...</div>

        <form v-else class="row g-3" @submit.prevent="handleSendTest">
          <div class="col-12">
            <label class="form-label fw-medium small">Channels</label>
            <div class="d-flex flex-wrap gap-2">
              <label v-for="channel in channels" :key="channel.channel" class="channel-toggle">
                <input
                  :checked="selectedChannels.includes(channel.channel)"
                  type="checkbox"
                  @change="toggleChannel(channel.channel)"
                />
                <span>{{ channel.display_name }}</span>
              </label>
            </div>
          </div>

          <div class="col-md-6">
            <label class="form-label fw-medium small">Recipient / target</label>
            <input v-model.trim="form.recipient" class="form-control" type="text" placeholder="ops@example.org or @channel-id" />
          </div>

          <div class="col-md-6">
            <label class="form-label fw-medium small">Subject</label>
            <input v-model.trim="form.subject" class="form-control" type="text" placeholder="Kairo notification test" />
          </div>

          <div class="col-12">
            <label class="form-label fw-medium small">Body</label>
            <textarea v-model.trim="form.body" class="form-control" rows="4" placeholder="This message validates the placeholder notification pipeline." />
          </div>

          <div class="col-12 d-flex gap-2">
            <button class="btn btn-primary" type="submit" :disabled="saving || selectedChannels.length === 0">
              {{ saving ? 'Sending...' : 'Run simulated dispatch' }}
            </button>
            <button class="btn btn-outline-secondary" type="button" @click="resetForm">
              Reset
            </button>
          </div>
        </form>

        <div v-if="results.length > 0" class="row g-3 mt-1">
          <div v-for="result in results" :key="result.channel" class="col-md-6 col-xl-4">
            <article class="result-card h-100">
              <div class="d-flex align-items-center justify-content-between gap-2 mb-2">
                <div class="fw-semibold text-capitalize">{{ result.channel }}</div>
                <span class="badge bg-info-subtle text-info border border-info-subtle">{{ result.status }}</span>
              </div>
              <p class="small text-muted mb-2">{{ result.message }}</p>
              <div class="small">
                {{ result.simulation_only ? 'Simulation only' : 'Live-capable' }}
              </div>
            </article>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  listNotificationChannels,
  sendNotificationTest,
  type NotificationChannelResponse,
  type NotificationDispatchResponse,
} from '@/api/notifications.api'

const loading = ref(true)
const saving = ref(false)
const channels = ref<NotificationChannelResponse[]>([])
const results = ref<NotificationDispatchResponse[]>([])
const selectedChannels = ref<string[]>(['email'])
const form = ref({
  recipient: 'ops@example.org',
  subject: 'Kairo notification test',
  body: 'This message validates the placeholder notification pipeline.',
})

async function refreshData() {
  loading.value = true
  try {
    channels.value = await listNotificationChannels()
  } finally {
    loading.value = false
  }
}

function toggleChannel(channel: string) {
  selectedChannels.value = selectedChannels.value.includes(channel)
    ? selectedChannels.value.filter((item) => item !== channel)
    : [...selectedChannels.value, channel]
}

function resetForm() {
  selectedChannels.value = ['email']
  form.value = {
    recipient: 'ops@example.org',
    subject: 'Kairo notification test',
    body: 'This message validates the placeholder notification pipeline.',
  }
  results.value = []
}

async function handleSendTest() {
  if (selectedChannels.value.length === 0) {
    return
  }
  saving.value = true
  try {
    const response = await sendNotificationTest({
      channels: selectedChannels.value,
      recipient: form.value.recipient,
      subject: form.value.subject || null,
      body: form.value.body,
    })
    results.value = response.results
  } finally {
    saving.value = false
  }
}

onMounted(refreshData)
</script>

<style scoped>
.channel-card {
  border-radius: 1rem;
}

.channel-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 999px;
  background: #fff;
  font-size: 0.875rem;
}

.result-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: #fff;
  padding: 1rem;
}
</style>
