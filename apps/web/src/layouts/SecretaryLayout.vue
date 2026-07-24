<template>
  <div class="d-flex om-min-viewport-height secretary-shell-bg">
    <aside class="secretary-sidebar d-none d-lg-flex flex-column p-3">
      <div class="d-flex align-items-center gap-2 mb-4 px-1">
        <i class="bi bi-journal-richtext fs-5" :style="{ color: primaryColor }"></i>
        <span class="fw-bold" :style="{ color: textColor }">
          {{ localeStore.t('layout.secretaryWorkspace') }}
        </span>
      </div>

      <nav class="vstack gap-2">
        <RouterLink to="/secretary" class="nav-link sidebar-link rounded" active-class="active" end>
          <i class="bi bi-speedometer2 me-2"></i>{{ localeStore.t('nav.overview') }}
        </RouterLink>
        <RouterLink to="/secretary/documents" class="nav-link sidebar-link rounded" active-class="active">
          <i class="bi bi-file-earmark-text me-2"></i>{{ localeStore.t('nav.documents') }}
        </RouterLink>
        <RouterLink to="/secretary/policies" class="nav-link sidebar-link rounded" active-class="active">
          <i class="bi bi-journal-text me-2"></i>{{ localeStore.t('nav.policies') }}
        </RouterLink>
        <RouterLink to="/secretary/announcements" class="nav-link sidebar-link rounded" active-class="active">
          <i class="bi bi-megaphone me-2"></i>{{ localeStore.t('nav.announcements') }}
        </RouterLink>
      </nav>

      <div class="mt-auto pt-3 border-top">
        <RouterLink to="/dashboard" class="nav-link sidebar-link rounded">
          <i class="bi bi-arrow-left me-2"></i>{{ localeStore.t('layout.backToPortal') }}
        </RouterLink>
      </div>
    </aside>

    <aside
      id="secretaryMobileSidebar"
      class="offcanvas offcanvas-start d-lg-none"
      tabindex="-1"
      aria-labelledby="secretaryMobileSidebarLabel"
    >
      <div class="offcanvas-header border-bottom">
        <span id="secretaryMobileSidebarLabel" class="fw-bold">
          <i class="bi bi-journal-richtext me-1" :style="{ color: primaryColor }"></i>
          {{ localeStore.t('layout.secretaryWorkspace') }}
        </span>
        <button class="btn-close" data-bs-dismiss="offcanvas" :aria-label="localeStore.t('layout.close')"></button>
      </div>
      <div class="offcanvas-body p-3 d-flex flex-column">
        <nav class="vstack gap-2">
          <RouterLink to="/secretary" class="nav-link sidebar-link rounded" active-class="active" end data-bs-dismiss="offcanvas">
            <i class="bi bi-speedometer2 me-2"></i>{{ localeStore.t('nav.overview') }}
          </RouterLink>
          <RouterLink to="/secretary/documents" class="nav-link sidebar-link rounded" active-class="active" data-bs-dismiss="offcanvas">
            <i class="bi bi-file-earmark-text me-2"></i>{{ localeStore.t('nav.documents') }}
          </RouterLink>
          <RouterLink to="/secretary/policies" class="nav-link sidebar-link rounded" active-class="active" data-bs-dismiss="offcanvas">
            <i class="bi bi-journal-text me-2"></i>{{ localeStore.t('nav.policies') }}
          </RouterLink>
          <RouterLink to="/secretary/announcements" class="nav-link sidebar-link rounded" active-class="active" data-bs-dismiss="offcanvas">
            <i class="bi bi-megaphone me-2"></i>{{ localeStore.t('nav.announcements') }}
          </RouterLink>
        </nav>
        <div class="mt-auto pt-3 border-top">
          <RouterLink to="/dashboard" class="nav-link sidebar-link rounded" data-bs-dismiss="offcanvas">
            <i class="bi bi-arrow-left me-2"></i>{{ localeStore.t('layout.backToPortal') }}
          </RouterLink>
        </div>
      </div>
    </aside>

    <main class="flex-grow-1 overflow-auto">
      <header class="topbar sticky-top bg-white border-bottom">
        <div class="d-flex align-items-center justify-content-between gap-3 px-3 px-lg-4 py-3">
          <div>
            <div class="text-muted small text-uppercase fw-semibold">
              {{ localeStore.t('layout.secretary') }}
            </div>
            <div class="fw-semibold">{{ localeStore.t('layout.secretarySubtitle') }}</div>
          </div>
          <div class="d-flex align-items-center gap-2 ms-auto">
            <button
              class="btn btn-link d-lg-none p-1 text-dark"
              data-bs-toggle="offcanvas"
              data-bs-target="#secretaryMobileSidebar"
              :aria-label="localeStore.t('layout.toggleNavigation')"
            >
              <i class="bi bi-list fs-4"></i>
            </button>
            <LanguageSelector :show-label="false" />
            <RouterLink to="/dashboard" class="btn btn-outline-secondary btn-sm">
              <i class="bi bi-arrow-left me-1 d-none d-sm-inline"></i>{{ localeStore.t('layout.backToPortal') }}
            </RouterLink>
          </div>
        </div>
      </header>

      <section class="content-shell om-content-constrain">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView } from "vue-router";
import { useTenantStore } from "@/stores/tenant.store";
import { useLocaleStore } from "@/stores/locale.store";
import LanguageSelector from "@/components/LanguageSelector.vue";

const tenantStore = useTenantStore();
const localeStore = useLocaleStore();

const primaryColor = computed(() => tenantStore.currentTenant?.branding.primary_color || "#1f4f8f");
const textColor = computed(() => "#1f2937");
</script>

<style scoped>
.secretary-shell-bg {
  background: var(--om-neutral-50);
}

.secretary-sidebar {
  background: var(--om-neutral-0);
  border-right: 1px solid var(--om-neutral-200);
  width: 250px;
  min-height: 100vh;
  min-height: 100dvh;
  flex-shrink: 0;
}

.topbar {
  z-index: 1020;
  background: var(--om-neutral-0);
}

.content-shell {
  padding: 0;
}
</style>
