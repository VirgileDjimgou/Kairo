<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-1">Upcoming events</h1>
        <p class="text-muted mb-0 small">Calendar of scheduled organization events</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5 text-muted">
      Loading events...
    </div>

    <div v-else-if="events.length === 0" class="empty-state">
      <i class="bi bi-calendar-event display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">No upcoming events</p>
      <p class="text-muted mb-0">Check back later for scheduled events.</p>
    </div>

    <div v-else class="row g-3">
      <div v-for="event in events" :key="event.id" class="col-md-6 col-xl-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <div class="d-flex align-items-start gap-3 mb-3">
              <div class="text-center flex-shrink-0" style="width: 50px">
                <div class="fw-bold text-primary fs-5">{{ formatDay(event.start_at) }}</div>
                <div class="small text-muted text-uppercase">{{ formatMonth(event.start_at) }}</div>
              </div>
              <div class="min-w-0">
                <h2 class="h6 fw-bold mb-1">{{ event.title }}</h2>
                <div v-if="event.location" class="small text-muted">
                  <i class="bi bi-geo-alt me-1"></i>{{ event.location }}
                </div>
              </div>
            </div>
            <p v-if="event.description" class="text-muted small mb-3">
              {{ event.description }}
            </p>
            <div class="d-flex justify-content-between align-items-center small">
              <span class="text-muted">
                <i class="bi bi-clock me-1"></i>{{ formatTime(event.start_at) }}
                <span v-if="event.end_at"> – {{ formatTime(event.end_at) }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listPublicEvents, type EventResponse } from '@/api/events.api'

const loading = ref(true)
const events = ref<EventResponse[]>([])

function formatDay(dateStr: string): string {
  return new Date(dateStr).getDate().toString()
}

function formatMonth(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short' })
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  try {
    events.value = await listPublicEvents()
  } finally {
    loading.value = false
  }
})
</script>
