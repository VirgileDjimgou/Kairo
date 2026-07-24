<template>
  <div class="d-flex om-min-viewport-height admin-shell-bg">
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
        <button class="btn-close" data-bs-dismiss="offcanvas" :aria-label="localeStore.t('layout.close')"></button>
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
      <MobileShellHeader
        class="d-lg-none"
        :eyebrow="consoleSubtitle"
        :title="tenantStore.currentTenantName"
        icon="bi-shield-lock"
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
              {{ tenantStore.currentTenantName }}
            </div>
            <div class="fw-semibold">{{ consoleSubtitle }}</div>
          </div>
          <div class="d-flex align-items-center gap-2 ms-auto">
            <LanguageSelector :show-label="false" />
            <div class="badge bg-warning-subtle text-warning border border-warning-subtle px-3 py-2">
              {{ consoleBadge }}
            </div>
          </div>
        </div>
      </header>

      <section class="content-shell content-shell--with-bottom-nav">
        <RouterView v-slot="{ Component }">
          <Transition name="app-route" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </section>
    </main>

    <MobileBottomNavigation
      :items="adminBottomNavItems"
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
import { useRoleNavigation } from "@/composables/useRoleNavigation";
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
const { adminNavigation, isPrincipalAdmin } = useRoleNavigation();

const primaryColor = computed(() => tenantStore.currentTenant?.branding.primary_color || "#1f4f8f");
const textColor = computed(() => "#1f2937");
const consoleTitle = computed(() =>
  isPrincipalAdmin.value ? localeStore.t('layout.principalAdminConsole') : localeStore.t('layout.adminConsole'),
);
const consoleSubtitle = computed(() =>
  isPrincipalAdmin.value ? localeStore.t('layout.principalAdminSubtitle') : localeStore.t('layout.adminSubtitle'),
);
const consoleBadge = computed(() => (isPrincipalAdmin.value ? "principal_admin" : "admin"));

const adminBottomNavItems = computed<BottomNavItem[]>(() => {
  const allItems = adminNavigation.value.flatMap((section) => section.items);
  const primaryRoutes = ['/admin', '/admin/members', '/admin/documents', '/admin/settings'];
  const selected = primaryRoutes.reduce<typeof allItems>((items, destination) => {
    const item = allItems.find((candidate) => candidate.to === destination);
    if (item) items.push(item);
    return items;
  }, []);

  return [
    ...selected.map((item) => ({
      id: item.to,
      label: item.label,
      icon: item.icon,
      active: route.path === item.to,
    })),
    { id: '__more__', label: localeStore.t('nav.more'), icon: 'bi-grid-3x3-gap', active: false },
  ];
});

function handleBottomNav(id: string) {
  if (id === '__more__') {
    showMobileMenu();
    return;
  }
  void router.push(id);
}

function showMobileMenu() {
  const element = document.getElementById('adminMobileSidebar');
  if (!element) return;
  (Offcanvas.getInstance(element) || new Offcanvas(element)).show();
}
</script>

<style scoped>
.admin-shell-bg {
  background: var(--om-neutral-50);
}

.admin-sidebar {
  background: var(--om-neutral-0);
  border-right: 1px solid var(--om-neutral-200);
  width: 260px;
  min-height: 100vh;
  min-height: 100dvh;
  flex-shrink: 0;
}

.topbar {
  z-index: 1020;
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
