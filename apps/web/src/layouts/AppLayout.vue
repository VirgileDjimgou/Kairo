<template>
  <div class="d-flex om-min-viewport-height shell-bg" :style="brandStyle">
    <aside class="sidebar d-none d-md-flex flex-column p-3">
      <div class="brand d-flex align-items-center gap-2 mb-4 px-1">
        <i class="bi bi-building-fill-gear" :style="{ color: primaryColor, fontSize: '1.25rem' }"></i>
        <span class="fw-bold" :style="{ color: textColor }">{{ tenantStore.currentTenantName }}</span>
      </div>

      <nav class="vstack gap-3">
        <section v-for="section in appNavigation" :key="section.label">
          <div class="small text-muted px-2 mb-1 fw-semibold text-uppercase">{{ section.label }}</div>
          <div class="nav flex-column gap-1">
            <RouterLink
              v-for="item in section.items"
              :key="item.to"
              :to="item.to"
              class="nav-link sidebar-link rounded"
              active-class="active"
            >
              <i class="me-2" :class="`bi ${item.icon}`"></i>{{ item.label }}
            </RouterLink>
          </div>
        </section>
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
        <button class="btn btn-outline-secondary btn-sm w-100" @click="handleLogout">
          <i class="bi bi-box-arrow-right me-1"></i>{{ localeStore.t('layout.signOut') }}
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
        <button class="btn-close" data-bs-dismiss="offcanvas" :aria-label="localeStore.t('layout.close')"></button>
      </div>
      <div class="offcanvas-body p-3 d-flex flex-column">
        <nav class="vstack gap-3">
          <section v-for="section in appNavigation" :key="section.label">
            <div class="small text-muted px-2 mb-1 fw-semibold text-uppercase">{{ section.label }}</div>
            <div class="nav flex-column gap-1">
              <RouterLink
                v-for="item in section.items"
                :key="item.to"
                :to="item.to"
                class="nav-link sidebar-link rounded"
                active-class="active"
                data-bs-dismiss="offcanvas"
              >
                <i class="me-2" :class="`bi ${item.icon}`"></i>{{ item.label }}
              </RouterLink>
            </div>
          </section>
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
          <button class="btn btn-outline-secondary btn-sm w-100" @click="handleLogout">
            <i class="bi bi-box-arrow-right me-1"></i>{{ localeStore.t('layout.signOut') }}
          </button>
        </div>
      </div>
    </aside>

    <main class="flex-grow-1 overflow-auto app-main-content">
      <header class="topbar sticky-top border-bottom" :style="{ backgroundColor: headerBg }">
        <div class="d-flex align-items-center justify-content-between gap-3 px-3 px-lg-4 py-3">
          <div>
            <div class="small text-uppercase fw-semibold" :style="{ color: mutedColor }">
              {{ appHomeLabel }}
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
              :aria-label="localeStore.t('layout.toggleNavigation')"
            >
              <i class="bi bi-list fs-4"></i>
            </button>

            <LanguageSelector :show-label="false" />

            <div v-if="tenantStore.hasMultipleTenants" class="dropdown tenant-switcher d-none d-sm-flex">
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
                  <button class="dropdown-item" @click="switchTenant(membership.tenant_id)">
                    <div class="fw-medium">{{ membership.name }}</div>
                    <div class="small text-muted">{{ membership.slug }}</div>
                  </button>
                </li>
              </ul>
            </div>

            <div class="dropdown">
              <button class="btn btn-primary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                <i class="bi bi-person-circle me-1"></i>{{ authStore.user?.display_name || localeStore.t('layout.account') }}
              </button>
              <ul class="dropdown-menu dropdown-menu-end shadow-sm">
                <li><h6 class="dropdown-header">{{ localeStore.t('layout.signedInAs') }}</h6></li>
                <li>
                  <span class="dropdown-item-text small text-muted">{{ authStore.user?.email }}</span>
                </li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <RouterLink to="/account/security" class="dropdown-item">{{ localeStore.t('layout.accountSecurity') }}</RouterLink>
                </li>
                <li>
                  <button class="dropdown-item text-danger" @click="handleLogout">{{ localeStore.t('layout.signOut') }}</button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </header>

      <section class="content-shell" :class="{ 'content-shell--with-bottom-nav': hasBottomNav }">
        <RouterView />
      </section>
    </main>

    <MobileBottomNavigation
      v-if="hasBottomNav"
      :items="bottomNavItems"
      class="d-md-none"
      @navigate="handleBottomNav"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { useRoleNavigation } from "@/composables/useRoleNavigation";
import { useTenantStore } from "@/stores/tenant.store";
import { useLocaleStore } from "@/stores/locale.store";
import LanguageSelector from "@/components/LanguageSelector.vue";
import MobileBottomNavigation from "@/components/ui/MobileBottomNavigation.vue";
import type { BottomNavItem } from "@/components/ui/MobileBottomNavigation.vue";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const tenantStore = useTenantStore();
const localeStore = useLocaleStore();
const { appNavigation, appHomeLabel } = useRoleNavigation();

const primaryColor = computed(() => tenantStore.currentTenant?.branding.primary_color || "#1f4f8f");
const textColor = computed(() => "#1f2937");
const mutedColor = computed(() => "#6c757d");
const headerBg = computed(() => "#ffffff");

const brandStyle = computed(() => ({
  "--om-primary": primaryColor.value,
}));

const bottomNavItems = computed<BottomNavItem[]>(() => {
  const allItems = appNavigation.value.flatMap((s) => s.items);
  const items: BottomNavItem[] = allItems.slice(0, 5).map((item) => ({
    id: item.to,
    label: item.label,
    icon: item.icon,
    active: route.path === item.to || (item.to !== '/dashboard' && route.path.startsWith(item.to)),
  }));
  if (items.length < 5) {
    items.push({
      id: '__more__',
      label: localeStore.t('nav.more'),
      icon: 'bi-three-dots',
      active: false,
    });
  }
  return items;
});

const hasBottomNav = computed(() => bottomNavItems.value.length > 0);

function handleBottomNav(id: string) {
  if (id === '__more__') {
    const offcanvasEl = document.getElementById('appMobileSidebar');
    if (offcanvasEl) {
      const bs = (window as any).bootstrap;
      if (bs?.Offcanvas) {
        const instance = bs.Offcanvas.getInstance(offcanvasEl) || new bs.Offcanvas(offcanvasEl);
        instance.show();
      }
    }
    return;
  }
  router.push(id);
}

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
  background: var(--om-neutral-50);
}

.sidebar {
  background: var(--om-neutral-0);
  border-right: 1px solid var(--om-neutral-200);
  width: var(--om-sidebar-width);
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

.app-main-content {
  padding-bottom: 0;
}

.smaller {
  font-size: 0.75rem;
}
</style>
