<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center min-vh-100">
    <div class="auth-card card shadow-sm border-0 p-4 p-md-5 w-100" style="max-width: 440px">
      <div class="text-center mb-4">
        <div class="brand-icon mb-3">
          <i class="bi bi-key fs-1 text-primary"></i>
        </div>
        <h1 class="h4 fw-bold mb-1">Reset password</h1>
        <p class="text-muted small mb-0">
          Enter your email and we'll send you a reset link.
        </p>
      </div>

      <form v-if="!submitted" @submit.prevent="handleSubmit" novalidate>
        <div class="mb-3">
          <label for="email" class="form-label fw-medium">Email address</label>
          <input
            id="email"
            v-model.trim="email"
            type="email"
            class="form-control"
            :class="{ 'is-invalid': errorMessage }"
            placeholder="you@organization.com"
            autocomplete="email"
            required
          />
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
          {{ loading ? "Sending\u2026" : "Send reset link" }}
        </button>
      </form>

      <div v-else class="text-center">
        <i class="bi bi-check-circle fs-1 text-success"></i>
        <p class="mt-2 mb-1 fw-medium">Check your email</p>
        <p class="text-muted small">
          If an account with that email exists, we've sent a reset link.
        </p>
        <div v-if="devToken" class="mt-2 p-2 bg-light rounded small">
          <p class="text-muted mb-1">Development token:</p>
          <code class="text-break">{{ devToken }}</code>
          <br />
          <router-link
            :to="{ path: '/reset-password', query: { token: devToken } }"
            class="btn btn-outline-secondary btn-sm mt-2"
          >
            Reset password now
          </router-link>
        </div>
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
import { ref } from "vue";
import { forgotPassword } from "@/api/auth.api";

const email = ref("");
const loading = ref(false);
const errorMessage = ref("");
const submitted = ref(false);
const devToken = ref<string | null>(null);
const isDev = import.meta.env.DEV;

async function handleSubmit() {
  if (!email.value) return;
  loading.value = true;
  errorMessage.value = "";
  try {
    const result = await forgotPassword({ email: email.value });
    submitted.value = true;
    if (isDev && result.reset_token) {
      devToken.value = result.reset_token;
    }
  } catch {
    errorMessage.value = "Something went wrong. Please try again.";
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
