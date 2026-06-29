<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center min-vh-100">
    <div class="auth-card card shadow-sm border-0 p-4 p-md-5 w-100" style="max-width: 440px">
      <div class="text-center mb-4">
        <div class="brand-icon mb-3">
          <i class="bi bi-shield-lock fs-1 text-primary"></i>
        </div>
        <h1 class="h4 fw-bold mb-1">Set new password</h1>
        <p class="text-muted small mb-0">
          Choose a strong password for your account.
        </p>
      </div>

      <div v-if="!hasToken" class="alert alert-warning py-2 small" role="alert">
        <i class="bi bi-exclamation-triangle me-1"></i>
        Missing reset token. Use the link from your email.
      </div>

      <form v-else-if="!success" @submit.prevent="handleSubmit" novalidate>
        <div class="mb-3">
          <label for="new-password" class="form-label fw-medium">New password</label>
          <input
            id="new-password"
            v-model="password"
            type="password"
            class="form-control"
            :class="{ 'is-invalid': errorMessage }"
            placeholder="At least 8 characters"
            autocomplete="new-password"
            required
          />
        </div>

        <div class="mb-3">
          <label for="confirm-password" class="form-label fw-medium">Confirm password</label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            class="form-control"
            :class="{ 'is-invalid': mismatch }"
            placeholder="Repeat your password"
            autocomplete="new-password"
            required
          />
          <div v-if="mismatch" class="invalid-feedback">Passwords do not match</div>
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
          {{ loading ? "Resetting\u2026" : "Reset password" }}
        </button>
      </form>

      <div v-else class="text-center">
        <i class="bi bi-check-circle fs-1 text-success"></i>
        <p class="mt-2 mb-1 fw-medium">Password reset successful</p>
        <p class="text-muted small">You can now sign in with your new password.</p>
        <router-link to="/login" class="btn btn-primary mt-2">
          Sign in
        </router-link>
      </div>

      <div class="text-center mt-3">
        <router-link to="/login" class="small text-muted">
          Back to sign in
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import { resetPassword } from "@/api/auth.api";

const route = useRoute();
const token = computed(() => (route.query.token as string) || "");
const hasToken = computed(() => token.value.length > 0);

const password = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const errorMessage = ref("");
const success = ref(false);

const mismatch = computed(() => {
  return confirmPassword.value.length > 0 && password.value !== confirmPassword.value;
});

async function handleSubmit() {
  if (!password.value || password.value.length < 8) {
    errorMessage.value = "Password must be at least 8 characters";
    return;
  }
  if (password.value !== confirmPassword.value) {
    errorMessage.value = "Passwords do not match";
    return;
  }

  loading.value = true;
  errorMessage.value = "";
  try {
    await resetPassword({ token: token.value, new_password: password.value });
    success.value = true;
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } };
    errorMessage.value = e.response?.data?.detail || "Reset failed. The link may be expired.";
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
