<template>
  <div v-if="authStore.isDemoSession" class="demo-banner" role="status">
    <div class="demo-banner__inner">
      <i class="bi bi-easel2-fill me-2" aria-hidden="true"></i>
      <span class="fw-semibold">{{ localeStore.t("demo.bannerText") }}</span>
      <span class="d-none d-md-inline text-white-50">· {{ localeStore.t("demo.bannerData") }}</span>
      <span class="ms-auto d-flex align-items-center gap-2">
        <RouterLink to="/demo" class="btn btn-sm btn-light">
          {{ localeStore.t("demo.switchRole") }}
        </RouterLink>
        <button type="button" class="btn btn-sm btn-outline-light" @click="exitDemo">
          {{ localeStore.t("demo.exit") }}
        </button>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { useLocaleStore } from "@/stores/locale.store";

const router = useRouter();
const authStore = useAuthStore();
const localeStore = useLocaleStore();

function exitDemo() {
  authStore.logout();
  void router.push("/demo");
}
</script>

<style scoped>
.demo-banner {
  position: sticky;
  top: 0;
  z-index: 1090;
  background: #14233a;
  color: #eaf1fb;
  font-size: 0.85rem;
}

.demo-banner__inner {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.4rem 0.75rem;
  width: min(100%, 90rem);
  margin: 0 auto;
}

.demo-banner__inner .btn {
  --bs-btn-padding-y: 0.15rem;
  --bs-btn-padding-x: 0.5rem;
  --bs-btn-font-size: 0.78rem;
}
</style>
