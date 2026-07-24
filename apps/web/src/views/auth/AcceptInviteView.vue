<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center om-min-viewport-height om-safe-bottom">
    <div class="auth-card card shadow-sm border-0 p-4 p-md-5 w-100" style="max-width: 440px">
      <div class="text-center mb-4">
        <div class="brand-icon mb-3">
          <i class="bi bi-envelope-paper fs-1 text-primary"></i>
        </div>
        <h1 class="h4 fw-bold mb-1">{{ t('auth.acceptInvite.title') }}</h1>
        <p class="text-muted small mb-0">
          {{ t('auth.acceptInvite.subtitle') }}
        </p>
      </div>

      <div v-if="!hasToken" class="alert alert-warning py-2 small" role="alert">
        <i class="bi bi-exclamation-triangle me-1"></i>
        {{ t('auth.acceptInvite.missingToken') }}
      </div>

      <form v-else-if="!success" @submit.prevent="handleSubmit" novalidate>
        <div class="mb-3">
          <label for="display-name" class="form-label fw-medium">{{ t('auth.acceptInvite.displayNameLabel') }}</label>
          <input
            id="display-name"
            v-model.trim="displayName"
            type="text"
            class="form-control"
            :class="{ 'is-invalid': errors.name }"
            :placeholder="t('auth.acceptInvite.displayNamePlaceholder')"
            autocomplete="name"
            required
          />
          <div v-if="errors.name" class="invalid-feedback">{{ errors.name }}</div>
        </div>

        <div class="mb-3">
          <label for="password" class="form-label fw-medium">{{ t('auth.acceptInvite.passwordLabel') }}</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-control"
            :class="{ 'is-invalid': errors.password }"
            :placeholder="t('auth.acceptInvite.passwordPlaceholder')"
            autocomplete="new-password"
            required
          />
          <div v-if="errors.password" class="invalid-feedback">{{ errors.password }}</div>
        </div>

        <div v-if="errorMessage" class="alert alert-danger py-2 small" role="alert">
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
          {{ loading ? t('auth.acceptInvite.accepting') : t('auth.acceptInvite.acceptButton') }}
        </button>
      </form>

      <div v-else class="text-center">
        <i class="bi bi-check-circle fs-1 text-success"></i>
        <p class="mt-2 mb-1 fw-medium">{{ t('auth.acceptInvite.welcomeTitle') }}</p>
        <p class="text-muted small">
          {{ t('auth.acceptInvite.welcomeMessage') }}
        </p>
        <div class="d-flex flex-column flex-sm-row justify-content-center gap-2 mt-3">
          <router-link to="/account/security" class="btn btn-primary">
            {{ t('auth.acceptInvite.secureAccount') }}
          </router-link>
          <router-link to="/dashboard" class="btn btn-outline-secondary">
            {{ t('auth.acceptInvite.goToDashboard') }}
          </router-link>
        </div>
      </div>

      <div class="text-center mt-3">
        <router-link to="/login" class="small text-muted">
          {{ t('auth.acceptInvite.alreadyHaveAccount') }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { acceptInvite } from "@/api/auth.api";
import { useAuthStore } from "@/stores/auth.store";
import { useLocaleStore } from "@/stores/locale.store";
import { getApiErrorDetail, mapAcceptInviteError } from "@/utils/authErrors";

const route = useRoute();
const authStore = useAuthStore();
const localeStore = useLocaleStore();
const t = (key: string) => localeStore.t(key);

const token = computed(() => (route.query.token as string) || "");
const hasToken = computed(() => token.value.length > 0);

const displayName = ref("");
const password = ref("");
const loading = ref(false);
const errorMessage = ref("");
const success = ref(false);
const errors = reactive({ name: "", password: "" });

async function handleSubmit() {
  errors.name = "";
  errors.password = "";
  errorMessage.value = "";

  if (!displayName.value) {
    errors.name = t('auth.acceptInvite.nameRequired');
    return;
  }
  if (!password.value || password.value.length < 8) {
    errors.password = t('auth.acceptInvite.passwordTooShort');
    return;
  }

  loading.value = true;
  try {
    const result = await acceptInvite({
      token: token.value,
      display_name: displayName.value,
      password: password.value,
    });
    localStorage.setItem("access_token", result.access_token);
    await authStore.restoreSession();
    success.value = true;
  } catch (err: unknown) {
    errorMessage.value = mapAcceptInviteError(getApiErrorDetail(err));
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-wrapper {
  background-color: var(--om-bg, #f5f7fb);
}
.auth-card {
  background-color: var(--om-card-bg, #ffffff);
  border-radius: 1rem !important;
}
.brand-icon {
  width: 64px;
  height: 64px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(31, 79, 143, 0.08);
  border-radius: 1rem;
}
</style>
