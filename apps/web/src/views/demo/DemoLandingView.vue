<template>
  <div class="demo-shell">
    <header class="demo-header">
      <div class="d-flex align-items-center gap-2 min-w-0">
        <span class="demo-brand">
          <i class="bi bi-building-fill-gear"></i>
        </span>
        <div class="min-w-0">
          <strong class="d-block lh-1">{{ localeStore.t("app.name") }}</strong>
          <span class="demo-brand-sub">{{ localeStore.t("demo.brandSubtitle") }}</span>
        </div>
      </div>
      <div class="d-flex align-items-center gap-2">
        <LanguageSelector compact :show-label="false" />
        <RouterLink to="/login" class="btn btn-sm btn-outline-light">
          {{ localeStore.t("demo.signInInstead") }}
        </RouterLink>
      </div>
    </header>

    <main class="demo-main">
      <section class="demo-hero text-center">
        <p class="demo-kicker mb-2">{{ localeStore.t("demo.heroKicker") }}</p>
        <h1 class="demo-title mb-3">{{ localeStore.t("demo.heroTitle") }}</h1>
        <p class="demo-copy mx-auto mb-0">{{ localeStore.t("demo.heroCopy") }}</p>
      </section>

      <div v-if="!isDemoMode" class="alert alert-warning border-0 shadow-sm" role="alert">
        <i class="bi bi-info-circle me-2"></i>{{ localeStore.t("demo.disabled") }}
      </div>

      <template v-else>
        <div v-if="errorMessage" class="alert alert-danger border-0 shadow-sm" role="alert">
          <i class="bi bi-exclamation-circle me-2"></i>{{ errorMessage }}
        </div>

        <section data-testid="demo-role-picker">
          <div class="text-center mb-3">
            <h2 class="h5 fw-bold mb-1">{{ localeStore.t("demo.chooseRoleTitle") }}</h2>
            <p class="text-muted small mb-0">{{ localeStore.t("demo.chooseRoleSubtitle") }}</p>
          </div>

          <div class="row g-3">
            <div v-for="account in primaryAccounts" :key="account.key" class="col-12 col-sm-6 col-lg-4">
              <article class="demo-role-card h-100 p-3 d-flex flex-column">
                <div class="demo-role-icon mb-2">
                  <i :class="account.icon"></i>
                </div>
                <h3 class="h6 fw-bold mb-1">{{ localeStore.t(account.roleLabelKey) }}</h3>
                <p class="small text-muted flex-grow-1 mb-3">
                  {{ localeStore.t(account.descriptionKey) }}
                </p>
                <button
                  type="button"
                  class="btn btn-primary btn-sm w-100"
                  :disabled="loadingKey !== null"
                  data-testid="demo-explore-role"
                  @click="explore(account)"
                >
                  <span
                    v-if="loadingKey === account.key"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  {{ loadingKey === account.key ? localeStore.t("demo.loading") : localeStore.t("demo.explore") }}
                </button>
              </article>
            </div>
          </div>
        </section>

        <section v-if="advancedAccounts.length" class="mt-4">
          <details class="demo-advanced">
            <summary class="fw-semibold">
              <i class="bi bi-shield-lock me-1"></i>{{ localeStore.t("demo.advancedRoles") }}
            </summary>
            <p class="small text-muted mt-2 mb-3">{{ localeStore.t("demo.advancedHint") }}</p>
            <div class="row g-3">
              <div v-for="account in advancedAccounts" :key="account.key" class="col-12 col-sm-6">
                <article class="demo-role-card h-100 p-3 d-flex flex-column">
                  <div class="demo-role-icon mb-2">
                    <i :class="account.icon"></i>
                  </div>
                  <h3 class="h6 fw-bold mb-1">{{ localeStore.t(account.roleLabelKey) }}</h3>
                  <p class="small text-muted flex-grow-1 mb-3">
                    {{ localeStore.t(account.descriptionKey) }}
                  </p>
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm w-100"
                    :disabled="loadingKey !== null"
                    @click="explore(account)"
                  >
                    <span
                      v-if="loadingKey === account.key"
                      class="spinner-border spinner-border-sm me-2"
                      role="status"
                      aria-hidden="true"
                    ></span>
                    {{ loadingKey === account.key ? localeStore.t("demo.loading") : localeStore.t("demo.explore") }}
                  </button>
                </article>
              </div>
            </div>
          </details>
        </section>

        <section class="demo-steps mt-5">
          <div class="row g-3">
            <div v-for="(step, index) in steps" :key="step.titleKey" class="col-12 col-md-4">
              <div class="demo-step h-100 p-3">
                <span class="demo-step-index">{{ index + 1 }}</span>
                <strong class="d-block mb-1">{{ localeStore.t(step.titleKey) }}</strong>
                <span class="small text-muted">{{ localeStore.t(step.textKey) }}</span>
              </div>
            </div>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { useLocaleStore } from "@/stores/locale.store";
import LanguageSelector from "@/components/LanguageSelector.vue";
import {
  IS_DEMO_MODE,
  advancedDemoAccounts,
  primaryDemoAccounts,
  type DemoAccount,
} from "@/config/demoAccounts";

const router = useRouter();
const authStore = useAuthStore();
const localeStore = useLocaleStore();

const isDemoMode = IS_DEMO_MODE;
const primaryAccounts = primaryDemoAccounts();
const advancedAccounts = advancedDemoAccounts();
const loadingKey = ref<string | null>(null);
const errorMessage = ref("");

const steps = [
  { titleKey: "demo.role.member", textKey: "demo.heroCopy" },
  { titleKey: "demo.chooseRoleTitle", textKey: "demo.chooseRoleSubtitle" },
  { titleKey: "demo.tourTitle", textKey: "demo.tourSubtitle" },
];

async function explore(account: DemoAccount) {
  if (loadingKey.value) return;
  loadingKey.value = account.key;
  errorMessage.value = "";
  try {
    const ok = await authStore.loginAsDemo(account.email, account.password);
    if (!ok) {
      errorMessage.value = localeStore.t("demo.loginFailed");
      return;
    }
    await router.push("/dashboard");
  } catch {
    errorMessage.value = localeStore.t("demo.loginFailed");
  } finally {
    loadingKey.value = null;
  }
}
</script>

<style scoped>
.demo-shell {
  min-height: 100dvh;
  background: #eef2f7;
}

.demo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #14233a;
  color: #eaf1fb;
}

.demo-brand {
  display: inline-flex;
  width: 2rem;
  height: 2rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.6rem;
  background: rgba(255, 255, 255, 0.12);
  flex: 0 0 auto;
}

.demo-header strong {
  color: #fff;
  font-size: 0.9rem;
}

.demo-brand-sub {
  font-size: 0.7rem;
  color: rgba(234, 241, 251, 0.72);
}

.demo-main {
  width: min(100%, 64rem);
  margin: 0 auto;
  padding: 2rem 1rem 3rem;
}

.demo-kicker {
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 700;
  color: #1e63b5;
}

.demo-title {
  font-size: clamp(1.6rem, 4vw, 2.6rem);
  font-weight: 800;
  color: #14233a;
  letter-spacing: -0.02em;
}

.demo-copy {
  max-width: 46rem;
  color: #5a6472;
}

.demo-role-card {
  border-radius: 1rem;
  background: #fff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 0.5rem 1.5rem rgba(15, 33, 56, 0.06);
}

.demo-role-icon {
  display: inline-flex;
  width: 2.5rem;
  height: 2.5rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
  background: rgba(31, 79, 143, 0.08);
  color: #1e63b5;
  font-size: 1.1rem;
}

.demo-advanced {
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.6);
  border: 1px dashed #cbd5e1;
  padding: 1rem;
}

.demo-advanced summary {
  cursor: pointer;
  color: #14233a;
}

.demo-step {
  border-radius: 1rem;
  background: #fff;
  border: 1px solid #e2e8f0;
}

.demo-step-index {
  display: inline-flex;
  width: 1.75rem;
  height: 1.75rem;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #14233a;
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}
</style>
