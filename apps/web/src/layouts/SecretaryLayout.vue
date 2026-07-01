<template>
  <div class="d-flex min-vh-100 secretary-shell-bg">
    <aside class="secretary-sidebar d-none d-lg-flex flex-column p-3">
      <div class="d-flex align-items-center gap-2 mb-4 px-1">
        <i class="bi bi-journal-richtext fs-5" :style="{ color: primaryColor }"></i>
        <span class="fw-bold" :style="{ color: textColor }">Secretary Workspace</span>
      </div>

      <nav class="nav flex-column gap-1">
        <RouterLink to="/secretary" class="nav-link sidebar-link rounded" active-class="active" end>
          <i class="bi bi-house-door me-2"></i>Overview
        </RouterLink>
        <RouterLink to="/secretary/documents" class="nav-link sidebar-link rounded" active-class="active">
          <i class="bi bi-file-earmark-text me-2"></i>Documents
        </RouterLink>
        <RouterLink
          v-if="modules.policies"
          to="/secretary/policies"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-journal-text me-2"></i>Policies
        </RouterLink>
        <RouterLink
          v-if="modules.announcements"
          to="/secretary/announcements"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-megaphone me-2"></i>Announcements
        </RouterLink>
        <hr class="my-2" />
        <RouterLink to="/dashboard" class="nav-link sidebar-link rounded" active-class="active">
          <i class="bi bi-arrow-left-circle me-2"></i>Back to portal
        </RouterLink>
      </nav>
    </aside>

    <main class="flex-grow-1 overflow-auto">
      <header class="topbar sticky-top bg-white border-bottom">
        <div class="d-flex align-items-center justify-content-between gap-3 px-3 px-lg-4 py-3">
          <div>
            <div class="text-muted small text-uppercase fw-semibold">
              {{ tenantStore.currentTenantName }}
            </div>
            <div class="fw-semibold">Governance documents and official communication</div>
          </div>
          <div class="badge bg-info-subtle text-info border border-info-subtle px-3 py-2">
            Secretary
          </div>
        </div>
      </header>

      <section class="content-shell">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useTenantStore } from '@/stores/tenant.store'

const tenantStore = useTenantStore()

const modules = computed(() => ({
  policies: tenantStore.isModuleEnabled('policies'),
  announcements: tenantStore.isModuleEnabled('announcements'),
}))

const primaryColor = computed(() => tenantStore.currentTenant?.branding.primary_color || '#1f4f8f')
const textColor = computed(() => '#1f2937')
</script>

<style scoped>
.secretary-shell-bg {
  background: linear-gradient(180deg, #f7f6f2 0%, #f4f6fa 100%);
}

.secretary-sidebar {
  width: 250px;
  background: #fffefb;
  border-right: 1px solid #e6e0d5;
}

.sidebar-link {
  color: #475467;
}

.sidebar-link.active,
.sidebar-link:hover {
  background: rgba(31, 79, 143, 0.08);
  color: #16395f;
}

.content-shell {
  max-width: 1280px;
}
</style>
