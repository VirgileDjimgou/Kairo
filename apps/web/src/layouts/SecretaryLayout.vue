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
      <MobileShellHeader
        class="d-lg-none"
        :eyebrow="localeStore.t('layout.secretary')"
        :title="localeStore.t('layout.secretaryWorkspace')"
        icon="bi-journal-richtext"
        :menu-label="localeStore.t('layout.toggleNavigation')"
        @open-menu="showMobileMenu"
      >
        <template #actions>
          <LanguageSelector :show-label="false" />
        </template>
      </MobileShellHeader>

      <header class="topbar sticky-top bg-white border-bottom d-none d-lg-block">
        <div class="d-flex align-items-center justify-content-between gap-3 px-3 px-lg-4 py-3">
          <div>
            <div class="text-muted small text-uppercase fw-semibold">
              {{ localeStore.t('layout.secretary') }}
            </div>
            <div class="fw-semibold">{{ localeStore.t('layout.secretarySubtitle') }}</div>
          </div>
          <div class="d-flex align-items-center gap-2 ms-auto">
            <LanguageSelector :show-label="false" />
            <RouterLink to="/dashboard" class="btn btn-outline-secondary btn-sm">
              <i class="bi bi-arrow-left me-1 d-none d-sm-inline"></i>{{ localeStore.t('layout.backToPortal') }}
            </RouterLink>
          </div>
        </div>
      </header>

      <section class="content-shell content-shell--with-bottom-nav om-content-constrain">
        <RouterView v-slot="{ Component }">
          <Transition name="app-route" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </section>
    </main>

    <MobileBottomNavigation
      :items="bottomNavItems"
      :aria-label="localeStore.t('layout.mobileNavigation')"
      class="d-lg-none"
      @navigate="handleBottomNav"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";
import { Offcanvas } from "bootstrap";
import { useTenantStore } from "@/stores/tenant.store";
import { useLocaleStore } from "@/stores/locale.store";
import LanguageSelector from "@/components/LanguageSelector.vue";
import MobileBottomNavigation from "@/components/ui/MobileBottomNavigation.vue";
import MobileShellHeader from "@/components/ui/MobileShellHeader.vue";
import type { BottomNavItem } from "@/components/ui/MobileBottomNavigation.vue";

const route = useRoute();
const router = useRouter();
const tenantStore = useTenantStore();
const localeStore = useLocaleStore();

const primaryColor = computed(() => tenantStore.currentTenant?.branding.primary_color || "#1f4f8f");
const textColor = computed(() => "#1f2937");

const bottomNavItems = computed<BottomNavItem[]>(() => [
  { id: '/secretary', label: localeStore.t('nav.overview'), icon: 'bi-speedometer2', active: route.path === '/secretary' },
  { id: '/secretary/documents', label: localeStore.t('nav.documents'), icon: 'bi-file-earmark-text', active: route.path === '/secretary/documents' },
  { id: '/secretary/policies', label: localeStore.t('nav.policies'), icon: 'bi-journal-text', active: route.path === '/secretary/policies' },
  { id: '/secretary/announcements', label: localeStore.t('nav.announcements'), icon: 'bi-megaphone', active: route.path === '/secretary/announcements' },
  { id: '__more__', label: localeStore.t('nav.more'), icon: 'bi-grid-3x3-gap', active: false },
]);

function handleBottomNav(id: string) {
  if (id === '__more__') {
    showMobileMenu();
    return;
  }
  void router.push(id);
}

function showMobileMenu() {
  const element = document.getElementById('secretaryMobileSidebar');
  if (!element) return;
  (Offcanvas.getInstance(element) || new Offcanvas(element)).show();
}
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

.content-shell--with-bottom-nav {
  padding-bottom: calc(var(--om-bottomnav-height) + env(safe-area-inset-bottom, 0px));
}

@media (min-width: 992px) {
  .content-shell--with-bottom-nav {
    padding-bottom: 0;
  }
}
</style>
