<template>
  <div class="login-shell min-vh-100 position-relative overflow-hidden">
    <div class="login-orb login-orb-one"></div>
    <div class="login-orb login-orb-two"></div>
    <div class="container-fluid position-relative px-0">
      <div class="row g-0 min-vh-100 align-items-stretch">
        <section class="col-lg-7 p-3 p-md-4 p-lg-5 d-flex">
          <div class="hero-panel w-100 p-4 p-md-5 d-flex flex-column justify-content-between">
            <div>
              <div class="d-flex flex-wrap align-items-center gap-2 mb-4">
                <span class="brand-mark">
                  <i class="bi bi-building-fill-gear"></i>
                </span>
                <div>
                  <div class="text-uppercase fw-semibold small hero-kicker">
                    {{ localeStore.t('app.name') }}
                  </div>
                  <div class="small text-secondary-emphasis">
                    {{ localeStore.t('login.brandSubtitle') }}
                  </div>
                </div>
                <div class="ms-auto">
                  <LanguageSelector />
                </div>
              </div>

              <div class="mb-4" data-testid="commercial-hero">
                <p class="eyebrow mb-2">{{ localeStore.t('login.kicker') }}</p>
                <h1
                  data-testid="commercial-hero-title"
                  class="display-5 fw-bold lh-sm hero-title mb-3"
                >
                  {{ localeStore.t('login.heroTitle') }}
                </h1>
                <p class="lead hero-copy mb-4">
                  {{ localeStore.t('login.heroCopy') }}
                </p>

                <div class="d-flex flex-wrap gap-2 mb-4">
                  <span
                    v-for="badge in commercialBadges"
                    :key="badge"
                    class="badge rounded-pill text-bg-light hero-badge"
                  >
                    {{ badge }}
                  </span>
                </div>

                <div id="highlights" class="row g-3">
                  <div
                    v-for="highlight in heroHighlights"
                    :key="highlight.title"
                    class="col-md-4"
                  >
                    <article class="highlight-card h-100 p-3 p-xl-4">
                      <div class="highlight-icon mb-3">
                        <i :class="highlight.icon"></i>
                      </div>
                      <h2 class="h6 fw-bold mb-2">{{ highlight.title }}</h2>
                      <p class="small text-secondary-emphasis mb-0">
                        {{ highlight.text }}
                      </p>
                    </article>
                  </div>
                </div>
              </div>
            </div>

            <div class="trust-strip mt-4 p-3 p-md-4">
              <div class="row g-3">
                <div
                  v-for="signal in trustSignals"
                  :key="signal.label"
                  class="col-md-4"
                >
                  <div class="trust-item">
                    <div class="small text-uppercase fw-semibold trust-label">
                      {{ signal.label }}
                    </div>
                    <div class="fw-medium">{{ signal.value }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="col-lg-5 p-3 p-md-4 p-lg-5 d-flex align-items-center justify-content-center">
          <div
            id="signin-card"
            class="auth-card card shadow-lg border-0 p-4 p-md-5 w-100"
          >
            <div class="text-center mb-4">
              <div class="brand-icon mb-3">
                <i class="bi bi-shield-lock fs-1 text-primary"></i>
              </div>
              <h2 class="h4 fw-bold mb-1">{{ localeStore.t('login.signInTitle') }}</h2>
              <p class="text-muted small mb-0">
                {{ localeStore.t('login.signInSubtitle') }}
              </p>
            </div>

            <!-- Login form (hidden during MFA or tenant selection) -->
            <form v-if="!showTenantPicker && !needsMfa" @submit.prevent="handleLogin" novalidate>
              <div class="mb-3">
                <label for="email" class="form-label fw-medium">{{ localeStore.t('login.email') }}</label>
                <input
                  id="email"
                  v-model.trim="form.email"
                  type="email"
                  class="form-control"
                  :class="{ 'is-invalid': errors.email }"
                  :placeholder="localeStore.t('login.emailPlaceholder')"
                  autocomplete="email"
                  required
                />
                <div v-if="errors.email" class="invalid-feedback">
                  {{ errors.email }}
                </div>
              </div>

              <div class="mb-3">
                <label for="password" class="form-label fw-medium">{{ localeStore.t('login.password') }}</label>
                <input
                  id="password"
                  v-model="form.password"
                  type="password"
                  class="form-control"
                  :class="{ 'is-invalid': errors.password }"
                  placeholder="••••••••"
                  autocomplete="current-password"
                  required
                />
                <div v-if="errors.password" class="invalid-feedback">
                  {{ errors.password }}
                </div>
                <div class="mt-1 text-end">
                  <router-link to="/forgot-password" class="small text-muted">
                    {{ localeStore.t('login.forgotPassword') }}
                  </router-link>
                </div>
              </div>

              <div
                v-if="errorMessage"
                class="alert alert-danger py-2 small"
                role="alert"
              >
                <i class="bi bi-exclamation-circle me-1"></i>{{ errorMessage }}
              </div>

              <div class="alert alert-light border py-2 small" role="status">
                <i class="bi bi-shield-check me-1"></i>
                {{ localeStore.t('login.mfaHint') }}
              </div>

              <button
                type="submit"
                class="btn btn-primary w-100 py-2 mt-1 fw-medium"
                :disabled="loading"
              >
                <span
                  v-if="loading"
                  class="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                ></span>
                {{ loading ? localeStore.t('login.signingIn') : localeStore.t('login.signIn') }}
              </button>
            </form>

            <!-- MFA challenge step -->
            <form v-else-if="needsMfa" @submit.prevent="handleMfa" novalidate>
              <div class="text-center mb-4">
                <i class="bi bi-shield-lock fs-1 text-primary"></i>
                <h3 class="h5 fw-bold mt-2 mb-1">{{ localeStore.t('login.mfaTitle') }}</h3>
                <p class="text-muted small mb-0">
                  {{ localeStore.t('login.mfaSubtitle') }}
                </p>
              </div>

              <div class="mb-3">
                <label for="mfa-code" class="form-label fw-medium">{{ localeStore.t('login.mfaCode') }}</label>
                <input
                  id="mfa-code"
                  v-model="mfaCode"
                  type="text"
                  class="form-control text-center"
                  :class="{ 'is-invalid': errors.mfaCode }"
                  placeholder="000000"
                  maxlength="6"
                  autocomplete="off"
                  required
                />
                <div v-if="errors.mfaCode" class="invalid-feedback">
                  {{ errors.mfaCode }}
                </div>
              </div>

              <div
                v-if="errorMessage"
                class="alert alert-danger py-2 small"
                role="alert"
              >
                <i class="bi bi-exclamation-circle me-1"></i>{{ errorMessage }}
              </div>

              <button
                type="submit"
                class="btn btn-primary w-100 py-2 mt-1 fw-medium"
                :disabled="loading"
              >
                <span
                  v-if="loading"
                  class="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                ></span>
                {{ loading ? localeStore.t('login.verifying') : localeStore.t('login.verify') }}
              </button>

              <button
                type="button"
                class="btn btn-link btn-sm w-100 mt-2 text-muted"
                @click="cancelMfa"
              >
                {{ localeStore.t('login.backToSignIn') }}
              </button>
            </form>

            <!-- Tenant picker (after login when multiple memberships) -->
            <div v-else>
              <div class="text-center mb-4">
                <i class="bi bi-building fs-1 text-primary"></i>
                <h3 class="h5 fw-bold mt-2 mb-1">{{ localeStore.t('login.chooseOrganization') }}</h3>
                <p class="text-muted small mb-0">
                  {{ localeStore.t('login.chooseOrganizationSubtitle') }}
                </p>
              </div>

              <div class="vstack gap-2">
                <button
                  v-for="membership in tenantStore.memberships"
                  :key="membership.tenant_id"
                  class="btn btn-outline-secondary text-start p-3 tenant-option"
                  :disabled="switchingTenant"
                  @click="selectTenant(membership.tenant_id)"
                >
                  <div class="fw-medium">{{ membership.name }}</div>
                  <div class="small text-muted">
                    <span class="badge bg-light text-dark me-1">{{ membership.slug }}</span>
                    {{ membership.roles.join(', ') }}
                  </div>
                </button>
              </div>

              <hr class="my-3" />
              <button
                class="btn btn-link btn-sm w-100 text-muted"
                @click="handleLogout"
              >
                {{ localeStore.t('login.signOutTryAnother') }}
              </button>
            </div>

            <!-- Dev credentials hint -->
            <div
              v-if="isDev && !showTenantPicker && !needsMfa"
              class="mt-4 p-3 rounded bg-light border border-dashed"
            >
              <p class="text-muted small mb-1 fw-medium">
                <i class="bi bi-info-circle me-1"></i>{{ localeStore.t('login.devCredentials') }}
              </p>
              <code class="small d-block text-secondary">admin@demo.org</code>
              <code class="small d-block text-secondary">Admin123!</code>
              <code class="small d-block text-secondary">alice@demo.org</code>
              <code class="small d-block text-secondary">Member123!</code>
              <button
                class="btn btn-outline-secondary btn-sm mt-2"
                @click="fillDemoCredentials"
              >
                {{ localeStore.t('login.fillDemoCredentials') }}
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";
import { useTenantStore } from "@/stores/tenant.store";
import { useLocaleStore } from "@/stores/locale.store";
import { getApiErrorDetail, mapLoginError, mapMfaError } from "@/utils/authErrors";
import LanguageSelector from "@/components/LanguageSelector.vue";

const router = useRouter();
const authStore = useAuthStore();
const tenantStore = useTenantStore();
const localeStore = useLocaleStore();
const isDev = import.meta.env.DEV;

const commercialBadges = computed(() => [
  localeStore.t('login.badge1'),
  localeStore.t('login.badge2'),
  localeStore.t('login.badge3'),
  localeStore.t('login.badge4'),
]);

const heroHighlights = computed(() => [
  {
    icon: "bi bi-file-earmark-text",
    title: localeStore.t('login.highlight1Title'),
    text: localeStore.t('login.highlight1Text'),
  },
  {
    icon: "bi bi-people",
    title: localeStore.t('login.highlight2Title'),
    text: localeStore.t('login.highlight2Text'),
  },
  {
    icon: "bi bi-shield-check",
    title: localeStore.t('login.highlight3Title'),
    text: localeStore.t('login.highlight3Text'),
  },
]);

const trustSignals = computed(() => [
  { label: localeStore.t('login.trustArchitecture'), value: localeStore.t('login.trustArchitectureValue') },
  { label: localeStore.t('login.trustSafety'), value: localeStore.t('login.trustSafetyValue') },
  { label: localeStore.t('login.trustOffer'), value: localeStore.t('login.trustOfferValue') },
]);

const form = reactive({ email: "", password: "" });
const errors = reactive({ email: "", password: "", mfaCode: "" });
const loading = ref(false);
const errorMessage = ref("");
const showTenantPicker = ref(false);
const switchingTenant = ref(false);
const needsMfa = ref(false);
const mfaCode = ref("");

function fillDemoCredentials() {
  form.email = "admin@demo.org";
  form.password = "Admin123!";
}

function validate(): boolean {
  errors.email = "";
  errors.password = "";
  if (!form.email) {
    errors.email = localeStore.t('login.errorEmailRequired');
    return false;
  }
  if (!form.password) {
    errors.password = localeStore.t('login.errorPasswordRequired');
    return false;
  }
  return true;
}

async function handleLogin() {
  if (!validate()) return;

  loading.value = true;
  errorMessage.value = "";
  showTenantPicker.value = false;
  needsMfa.value = false;

  try {
    const result = await authStore.login(form.email, form.password);

    if (result === "mfa_required") {
      needsMfa.value = true;
      return;
    }

    await continueAfterAuthentication();
  } catch (err: unknown) {
    errorMessage.value = mapLoginError(getApiErrorDetail(err));
  } finally {
    loading.value = false;
  }
}

async function handleMfa() {
  errors.mfaCode = "";
  if (!mfaCode.value || mfaCode.value.length !== 6) {
    errors.mfaCode = localeStore.t('login.errorMfaCode');
    return;
  }

  loading.value = true;
  errorMessage.value = "";

  try {
    const ok = await authStore.completeMfa(mfaCode.value);
    if (!ok) {
      errorMessage.value = localeStore.t('login.errorExpiredMfa');
      cancelMfa();
      return;
    }
    needsMfa.value = false;
    await continueAfterAuthentication();
  } catch (err: unknown) {
    errorMessage.value = mapMfaError(getApiErrorDetail(err));
  } finally {
    loading.value = false;
  }
}

async function continueAfterAuthentication() {
  const memberships = tenantStore.memberships;
  const redirect = (router.currentRoute.value.query.redirect as string) || "/dashboard";

  if (memberships.length === 0) {
    errorMessage.value = localeStore.t('login.errorNoMembership');
    authStore.logout();
    return;
  }

  if (memberships.length === 1) {
    showTenantPicker.value = false;
    await router.push(redirect);
    return;
  }

  showTenantPicker.value = true;
}

function cancelMfa() {
  needsMfa.value = false;
  mfaCode.value = "";
  authStore.mfaToken = null;
}

async function selectTenant(tenantId: string) {
  switchingTenant.value = true;
  try {
    const ok = await tenantStore.selectTenant(tenantId);
    if (ok) {
      const redirect = (router.currentRoute.value.query.redirect as string) || "/dashboard";
      await router.push(redirect);
    }
  } finally {
    switchingTenant.value = false;
  }
}

function handleLogout() {
  authStore.logout();
  showTenantPicker.value = false;
}
</script>

<style scoped>
.login-shell {
  background:
    radial-gradient(circle at top left, rgba(31, 79, 143, 0.14), transparent 32%),
    radial-gradient(circle at bottom right, rgba(15, 23, 42, 0.12), transparent 28%),
    linear-gradient(180deg, #f5f7fb 0%, #eef3f8 100%);
}

.login-orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(28px);
  opacity: 0.4;
  pointer-events: none;
}

.login-orb-one {
  width: 18rem;
  height: 18rem;
  top: -4rem;
  right: -6rem;
  background: rgba(31, 79, 143, 0.26);
}

.login-orb-two {
  width: 14rem;
  height: 14rem;
  bottom: 2rem;
  left: -4rem;
  background: rgba(90, 120, 170, 0.18);
}

.hero-panel {
  border-radius: 1.5rem;
  color: #eaf1fb;
  background:
    linear-gradient(160deg, rgba(15, 23, 42, 0.97) 0%, rgba(17, 46, 86, 0.92) 100%);
  box-shadow: 0 1.5rem 3.5rem rgba(15, 23, 42, 0.18);
}

.hero-kicker {
  color: rgba(234, 241, 251, 0.72);
  letter-spacing: 0.12em;
}

.hero-title {
  max-width: 12ch;
}

.hero-copy {
  max-width: 62ch;
  color: rgba(234, 241, 251, 0.82);
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.68);
}

.eyebrow::before {
  content: "";
  width: 2.25rem;
  height: 1px;
  background: rgba(255, 255, 255, 0.5);
}

.brand-mark {
  width: 3rem;
  height: 3rem;
  border-radius: 0.95rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  font-size: 1.15rem;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.hero-badge {
  background: rgba(255, 255, 255, 0.12) !important;
  color: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.highlight-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1.1rem;
  backdrop-filter: blur(10px);
}

.highlight-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.12);
  font-size: 1.05rem;
  color: #fff;
}

.trust-strip {
  border-radius: 1.1rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.trust-label {
  color: rgba(234, 241, 251, 0.72);
  letter-spacing: 0.08em;
}

.trust-item {
  min-height: 4.25rem;
}

.auth-card {
  background-color: var(--om-card-bg, #ffffff);
  border-radius: 1.25rem !important;
  max-width: 460px;
}

.brand-icon {
  width: 68px;
  height: 68px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(31, 79, 143, 0.08);
  border-radius: 1rem;
}

.border-dashed {
  border-style: dashed !important;
}

.tenant-option {
  border-radius: 0.85rem;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.tenant-option:hover {
  background: rgba(31, 79, 143, 0.06);
}

@media (max-width: 991.98px) {
  .hero-title {
    max-width: none;
    font-size: calc(1.5rem + 2vw);
  }

  .hero-panel {
    min-height: auto;
  }
}
</style>
