<template>
  <div class="d-flex min-vh-100 admin-shell-bg">
    <aside class="admin-sidebar d-none d-lg-flex flex-column p-3">
      <div class="d-flex align-items-center gap-2 mb-4 px-1">
        <i class="bi bi-shield-lock fs-5" :style="{ color: primaryColor }"></i>
        <span class="fw-bold" :style="{ color: textColor }" data-testid="admin-layout-title">
          {{ consoleTitle }}
        </span>
      </div>

      <nav class="vstack gap-3">
        <section v-for="section in adminNavigation" :key="section.label">
          <div class="small text-muted px-2 mb-1 fw-semibold text-uppercase">{{ section.label }}</div>
          <div class="nav flex-column gap-1">
            <RouterLink
              v-for="item in section.items"
              :key="item.to"
              :to="item.to"
              class="nav-link sidebar-link rounded"
              active-class="active"
              :end="item.to === '/admin'"
            >
              <i class="me-2" :class="`bi ${item.icon}`"></i>{{ item.label }}
            </RouterLink>
          </div>
        </section>
      </nav>
    </aside>

    <aside
      id="adminMobileSidebar"
      class="offcanvas offcanvas-start d-lg-none"
      tabindex="-1"
      aria-labelledby="adminMobileSidebarLabel"
    >
      <div class="offcanvas-header border-bottom">
        <span id="adminMobileSidebarLabel" class="fw-bold" data-testid="admin-layout-mobile-title">
          <i class="bi bi-shield-lock me-1" :style="{ color: primaryColor }"></i>
          {{ consoleTitle }}
        </span>
        <button class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div class="offcanvas-body p-3 d-flex flex-column">
        <nav class="vstack gap-3">
          <section v-for="section in adminNavigation" :key="section.label">
            <div class="small text-muted px-2 mb-1 fw-semibold text-uppercase">{{ section.label }}</div>
            <div class="nav flex-column gap-1">
              <RouterLink
                v-for="item in section.items"
                :key="item.to"
                :to="item.to"
                class="nav-link sidebar-link rounded"
                active-class="active"
                data-bs-dismiss="offcanvas"
                :end="item.to === '/admin'"
              >
                <i class="me-2" :class="`bi ${item.icon}`"></i>{{ item.label }}
              </RouterLink>
            </div>
          </section>
        </nav>
      </div>
    </aside>

    <main class="flex-grow-1 overflow-auto">
      <header class="topbar sticky-top bg-white border-bottom">
        <div class="d-flex align-items-center justify-content-between gap-3 px-3 px-lg-4 py-3">
          <div>
            <div class="text-muted small text-uppercase fw-semibold">
              {{ tenantStore.currentTenantName }}
            </div>
            <div class="fw-semibold">{{ consoleSubtitle }}</div>
          </div>
          <div class="d-flex align-items-center gap-2 ms-auto">
            <button
              class="btn btn-link d-lg-none p-1 text-dark"
              data-bs-toggle="offcanvas"
              data-bs-target="#adminMobileSidebar"
              aria-label="Toggle navigation"
            >
              <i class="bi bi-list fs-4"></i>
            </button>
            <div class="badge bg-warning-subtle text-warning border border-warning-subtle px-3 py-2">
              {{ consoleBadge }}
            </div>
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
import { computed } from "vue";
import { RouterLink, RouterView } from "vue-router";
import { useRoleNavigation } from "@/composables/useRoleNavigation";
import { useTenantStore } from "@/stores/tenant.store";

const tenantStore = useTenantStore();
const { adminNavigation, isPrincipalAdmin } = useRoleNavigation();

const primaryColor = computed(() => tenantStore.currentTenant?.branding.primary_color || "#1f4f8f");
const textColor = computed(() => "#1f2937");
const consoleTitle = computed(() => (isPrincipalAdmin.value ? "Principal Admin Control Plane" : "Admin Console"));
const consoleSubtitle = computed(() => (isPrincipalAdmin.value ? "Tenant-wide governance control" : "Operational control center"));
const consoleBadge = computed(() => (isPrincipalAdmin.value ? "principal_admin" : "admin"));
</script>

<style scoped>
.admin-shell-bg {
  background: linear-gradient(180deg, rgba(245, 247, 251, 1) 0%, rgba(245, 247, 251, 0.92) 100%);
}

.admin-sidebar {
  background: #ffffff;
  border-right: 1px solid var(--om-border, #d9e2ec);
  width: 260px;
  min-height: 100vh;
}

.topbar {
  z-index: 1020;
}

.sidebar-link {
  color: var(--om-text, #1f2937);
  font-size: 0.875rem;
  padding: 0.45rem 0.75rem;
  text-decoration: none;
}

.sidebar-link:hover,
.sidebar-link.active {
  background: rgba(31, 79, 143, 0.08);
  color: var(--om-primary, #1f4f8f);
  font-weight: 500;
}

.content-shell {
  padding: 0;
}
</style>
