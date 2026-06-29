<template>
  <div class="d-flex min-vh-100 shell-bg" :style="brandStyle">
    <aside class="sidebar d-none d-md-flex flex-column p-3">
      <div class="brand d-flex align-items-center gap-2 mb-4 px-1">
        <i class="bi bi-building-fill-gear" :style="{ color: primaryColor, fontSize: '1.25rem' }"></i>
        <span class="fw-bold" :style="{ color: textColor }">{{ tenantStore.currentTenantName }}</span>
      </div>

      <nav class="nav flex-column gap-1">
        <RouterLink
          to="/dashboard"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-grid-1x2 me-2"></i>Dashboard
        </RouterLink>
        <RouterLink
          v-if="modules.chat"
          to="/chat"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-chat-dots me-2"></i>Chat
        </RouterLink>
        <RouterLink
          v-if="modules.membership"
          to="/members/profile"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-person-badge me-2"></i>My Profile
        </RouterLink>
        <RouterLink
          v-if="modules.policies"
          to="/policies"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-journal-text me-2"></i>Policies
        </RouterLink>
        <RouterLink
          v-if="modules.disciplinary"
          to="/disciplinary"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-shield-check me-2"></i>Disciplinary
        </RouterLink>
        <RouterLink
          v-if="authStore.hasRole('admin')"
          to="/admin"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-shield-lock me-2"></i>Admin
        </RouterLink>
        <hr class="my-2" />
        <div class="small text-muted px-2 mb-1 fw-semibold text-uppercase">Organization</div>
        <RouterLink
          v-if="modules.events"
          to="/events"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-calendar-event me-2"></i>Events
        </RouterLink>
        <RouterLink
          v-if="modules.announcements"
          to="/announcements"
          class="nav-link sidebar-link rounded"
          active-class="active"
        >
          <i class="bi bi-megaphone me-2"></i>Announcements
        </RouterLink>
      </nav>

      <div class="mt-auto pt-3 border-top">
        <div class="d-flex align-items-center gap-2 px-2 mb-2">
          <i class="bi bi-person-circle text-muted"></i>
          <div class="overflow-hidden">
            <div class="small fw-medium text-truncate">
              {{ authStore.user?.display_name }}
            </div>
            <div class="smaller text-muted text-truncate">
              {{ authStore.user?.email }}
            </div>
          </div>
        </div>
        <button
          class="btn btn-outline-secondary btn-sm w-100"
          @click="handleLogout"
        >
          <i class="bi bi-box-arrow-right me-1"></i>Sign out
        </button>
      </div>
    </aside>

    <aside
      id="appMobileSidebar"
      class="offcanvas offcanvas-start d-md-none"
      tabindex="-1"
      aria-labelledby="appMobileSidebarLabel"
    >
      <div class="offcanvas-header border-bottom">
        <span id="appMobileSidebarLabel" class="fw-bold">
          <i class="bi bi-building-fill-gear me-1" :style="{ color: primaryColor }"></i>
          {{ tenantStore.currentTenantName }}
        </span>
        <button class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div class="offcanvas-body p-3">
        <nav class="nav flex-column gap-1">
          <RouterLink
            to="/dashboard"
            class="nav-link sidebar-link rounded"
            active-class="active"
            data-bs-dismiss="offcanvas"
          >
            <i class="bi bi-grid-1x2 me-2"></i>Dashboard
          </RouterLink>
          <RouterLink
            v-if="modules.chat"
            to="/chat"
            class="nav-link sidebar-link rounded"
            active-class="active"
            data-bs-dismiss="offcanvas"
          >
            <i class="bi bi-chat-dots me-2"></i>Chat
          </RouterLink>
          <RouterLink
            v-if="modules.membership"
            to="/members/profile"
            class="nav-link sidebar-link rounded"
            active-class="active"
            data-bs-dismiss="offcanvas"
          >
            <i class="bi bi-person-badge me-2"></i>My Profile
          </RouterLink>
          <RouterLink
            v-if="modules.policies"
            to="/policies"
            class="nav-link sidebar-link rounded"
            active-class="active"
            data-bs-dismiss="offcanvas"
          >
            <i class="bi bi-journal-text me-2"></i>Policies
          </RouterLink>
          <RouterLink
            v-if="modules.disciplinary"
            to="/disciplinary"
            class="nav-link sidebar-link rounded"
            active-class="active"
            data-bs-dismiss="offcanvas"
          >
            <i class="bi bi-shield-check me-2"></i>Disciplinary
          </RouterLink>
          <RouterLink
            v-if="authStore.hasRole('admin')"
            to="/admin"
            class="nav-link sidebar-link rounded"
            active-class="active"
            data-bs-dismiss="offcanvas"
          >
            <i class="bi bi-shield-lock me-2"></i>Admin
          </RouterLink>
          <hr class="my-2" />
          <div class="small text-muted px-2 mb-1 fw-semibold text-uppercase">Organization</div>
          <RouterLink
            v-if="modules.events"
            to="/events"
            class="nav-link sidebar-link rounded"
            active-class="active"
            data-bs-dismiss="offcanvas"
          >
            <i class="bi bi-calendar-event me-2"></i>Events
          </RouterLink>
          <RouterLink
            v-if="modules.announcements"
            to="/announcements"
            class="nav-link sidebar-link rounded"
            active-class="active"
            data-bs-dismiss="offcanvas"
          >
            <i class="bi bi-megaphone me-2"></i>Announcements
          </RouterLink>
        </nav>

        <div class="mt-auto pt-3 border-top">
          <div class="d-flex align-items-center gap-2 px-2 mb-2">
            <i class="bi bi-person-circle text-muted"></i>
            <div class="overflow-hidden">
              <div class="small fw-medium text-truncate">
                {{ authStore.user?.display_name }}
              </div>
              <div class="smaller text-muted text-truncate">
                {{ authStore.user?.email }}
              </div>
            </div>
          </div>
          <button
            class="btn btn-outline-secondary btn-sm w-100"
            @click="handleLogout"
          >
            <i class="bi bi-box-arrow-right me-1"></i>Sign out
          </button>
        </div>
      </div>
    </aside>

    <main class="flex-grow-1 overflow-auto">
      <header class="topbar sticky-top border-bottom" :style="{ backgroundColor: headerBg }">
        <div
          class="d-flex align-items-center justify-content-between gap-3 px-3 px-lg-4 py-3"
        >
          <div>
            <div class="small text-uppercase fw-semibold" :style="{ color: mutedColor }">
              Organization portal
            </div>
            <div class="fw-semibold" :style="{ color: textColor }">
              {{ tenantStore.currentTenantName }}
            </div>
          </div>

          <div class="d-flex align-items-center gap-2 ms-auto">
            <button
              class="btn btn-link d-md-none p-1 text-dark"
              data-bs-toggle="offcanvas"
              data-bs-target="#appMobileSidebar"
              aria-label="Toggle navigation"
            >
              <i class="bi bi-list fs-4"></i>
            </button>

            <div v-if="tenantStore.hasMultipleTenants" class="dropdown tenant-switcher">
              <button
                class="btn btn-outline-secondary btn-sm dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <i class="bi bi-building me-1"></i>{{ tenantStore.currentTenantName }}
              </button>
              <ul class="dropdown-menu dropdown-menu-end shadow-sm">
                <li v-for="membership in tenantStore.memberships" :key="membership.tenant_id">
                  <button
                    class="dropdown-item"
                    @click="switchTenant(membership.tenant_id)"
                  >
                    <div class="fw-medium">{{ membership.name }}</div>
                    <div class="small text-muted">{{ membership.slug }}</div>
                  </button>
                </li>
              </ul>
            </div>

            <div class="dropdown">
              <button
                class="btn btn-primary btn-sm dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown"
              >
                <i class="bi bi-person-circle me-1"></i
                >{{ authStore.user?.display_name || "Account" }}
              </button>
              <ul class="dropdown-menu dropdown-menu-end shadow-sm">
                <li><h6 class="dropdown-header">Signed in as</h6></li>
                <li>
                  <span class="dropdown-item-text small text-muted">{{
                    authStore.user?.email
                  }}</span>
                </li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <button
                    class="dropdown-item text-danger"
                    @click="handleLogout"
                  >
                    Sign out
                  </button>
                </li>
              </ul>
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
import { RouterLink, RouterView, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { useTenantStore } from "@/stores/tenant.store";

const router = useRouter();
const authStore = useAuthStore();
const tenantStore = useTenantStore();

const modules = computed(() => ({
  membership: tenantStore.isModuleEnabled("membership"),
  contributions: tenantStore.isModuleEnabled("contributions"),
  policies: tenantStore.isModuleEnabled("policies"),
  disciplinary: tenantStore.isModuleEnabled("disciplinary"),
  events: tenantStore.isModuleEnabled("events"),
  announcements: tenantStore.isModuleEnabled("announcements"),
  chat: tenantStore.isModuleEnabled("chat"),
  notifications: tenantStore.isModuleEnabled("notifications"),
}));

const primaryColor = computed(() => {
  return tenantStore.currentTenant?.branding.primary_color || "#1f4f8f";
});

const textColor = computed(() => "#1f2937");
const mutedColor = computed(() => "#6c757d");
const headerBg = computed(() => "#ffffff");

const brandStyle = computed(() => ({
  "--om-primary": primaryColor.value,
}));

async function switchTenant(tenantId: string) {
  const ok = await tenantStore.selectTenant(tenantId);
  if (ok) {
    window.location.href = "/dashboard";
  }
}

async function handleLogout() {
  authStore.logout();
  await router.push("/login");
}
</script>

<style scoped>
.shell-bg {
  background: linear-gradient(
    180deg,
    rgba(245, 247, 251, 1) 0%,
    rgba(245, 247, 251, 0.92) 100%
  );
}

.sidebar {
  background: #ffffff;
  border-right: 1px solid var(--om-border, #d9e2ec);
  width: 260px;
  min-height: 100vh;
  box-shadow: inset -1px 0 0 rgba(0, 0, 0, 0.02);
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

.smaller {
  font-size: 0.75rem;
}
</style>
