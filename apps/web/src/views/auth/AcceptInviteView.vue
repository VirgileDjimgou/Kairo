<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center min-vh-100">
    <div class="auth-card card shadow-sm border-0 p-4 p-md-5 w-100" style="max-width: 440px">
      <div class="text-center mb-4">
        <div class="brand-icon mb-3">
          <i class="bi bi-envelope-paper fs-1 text-primary"></i>
        </div>
        <h1 class="h4 fw-bold mb-1">Accept invitation</h1>
        <p class="text-muted small mb-0">
          You've been invited to join an organization. Set up your account to get started.
        </p>
      </div>

      <div v-if="!hasToken" class="alert alert-warning py-2 small" role="alert">
        <i class="bi bi-exclamation-triangle me-1"></i>
        Missing invitation token. Use the link from your invitation email.
      </div>

      <form v-else-if="!success" @submit.prevent="handleSubmit" novalidate>
        <div class="mb-3">
          <label for="display-name" class="form-label fw-medium">Display name</label>
          <input
            id="display-name"
            v-model.trim="displayName"
            type="text"
            class="form-control"
            :class="{ 'is-invalid': errors.name }"
            placeholder="Your full name"
            autocomplete="name"
            required
          />
          <div v-if="errors.name" class="invalid-feedback">{{ errors.name }}</div>
        </div>

        <div class="mb-3">
          <label for="password" class="form-label fw-medium">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-control"
            :class="{ 'is-invalid': errors.password }"
            placeholder="At least 8 characters"
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
          {{ loading ? "Accepting\u2026" : "Accept invitation &amp; sign in" }}
        </button>
      </form>

      <div v-else class="text-center">
        <i class="bi bi-check-circle fs-1 text-success"></i>
        <p class="mt-2 mb-1 fw-medium">Welcome!</p>
        <p class="text-muted small">Your account has been set up and you're now signed in.</p>
        <router-link to="/dashboard" class="btn btn-primary mt-2">
          Go to dashboard
        </router-link>
      </div>

      <div class="text-center mt-3">
        <router-link to="/login" class="small text-muted">
          Already have an account? Sign in
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { acceptInvite } from "@/api/auth.api";
import { useAuthStore } from "@/stores/auth.store";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

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
    errors.name = "Display name is required";
    return;
  }
  if (!password.value || password.value.length < 8) {
    errors.password = "Password must be at least 8 characters";
    return;
  }

  loading.value = true;
  try {
    const result = await acceptInvite({
      token: token.value,
      display_name: displayName.value,
      password: password.value,
    });
    // Store the token and redirect
    localStorage.setItem("access_token", result.access_token);
    await authStore.restoreSession();
    success.value = true;
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } };
    errorMessage.value = e.response?.data?.detail || "Acceptance failed. The link may be expired.";
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
