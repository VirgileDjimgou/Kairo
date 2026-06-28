<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h1 class="h4 fw-bold mb-1">Announcements</h1>
        <p class="text-muted mb-0 small">Current organization announcements</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5 text-muted">
      Loading announcements...
    </div>

    <div v-else-if="announcements.length === 0" class="empty-state">
      <i class="bi bi-megaphone display-6 text-secondary"></i>
      <p class="mb-1 fw-semibold">No current announcements</p>
      <p class="text-muted mb-0">There are no active announcements at this time.</p>
    </div>

    <div v-else class="row g-3">
      <div v-for="announcement in announcements" :key="announcement.id" class="col-12">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="d-flex align-items-start justify-content-between gap-3 mb-2">
              <h2 class="h5 fw-bold mb-0">{{ announcement.title }}</h2>
              <span v-if="isNew(announcement.created_at)" class="badge bg-primary-subtle text-primary border border-primary-subtle">New</span>
            </div>
            <p class="text-muted mb-3" style="white-space: pre-line">{{ announcement.body }}</p>
            <div class="d-flex gap-3 small text-muted">
              <span><i class="bi bi-calendar me-1"></i>{{ formatDate(announcement.published_at || announcement.created_at) }}</span>
              <span v-if="announcement.expires_at"><i class="bi bi-hourglass me-1"></i>Expires {{ formatDate(announcement.expires_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listActiveAnnouncements, type AnnouncementResponse } from '@/api/announcements.api'

const loading = ref(true)
const announcements = ref<AnnouncementResponse[]>([])

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function isNew(dateStr: string): boolean {
  const daysAgo = (Date.now() - new Date(dateStr).getTime()) / (1000 * 60 * 60 * 24)
  return daysAgo < 3
}

onMounted(async () => {
  try {
    announcements.value = await listActiveAnnouncements()
  } finally {
    loading.value = false
  }
})
</script>
