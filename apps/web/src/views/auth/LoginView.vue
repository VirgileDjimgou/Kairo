<template>
  <div
    class="auth-wrapper d-flex align-items-center justify-content-center min-vh-100"
  >
    <div
      class="auth-card card shadow-sm border-0 p-4 p-md-5 w-100"
      style="max-width: 440px"
    >
      <!-- Logo / Brand -->
      <div class="text-center mb-4">
        <div class="brand-icon mb-3">
          <i class="bi bi-building-fill-gear fs-1 text-primary"></i>
        </div>
        <h1 class="h4 fw-bold mb-1">OrgMind AI</h1>
        <p class="text-muted small mb-0">Sign in to your organization</p>
      </div>

      <!-- Login form -->
      <form @submit.prevent="handleLogin" novalidate>
        <div class="mb-3">
          <label for="email" class="form-label fw-medium">Email address</label>
          <input
            id="email"
            v-model.trim="form.email"
            type="email"
            class="form-control"
            :class="{ 'is-invalid': errors.email }"
            placeholder="you@organization.com"
            autocomplete="email"
            required
          />
          <div v-if="errors.email" class="invalid-feedback">
            {{ errors.email }}
          </div>
        </div>

        <div class="mb-3">
          <label for="password" class="form-label fw-medium">Password</label>
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
        </div>

        <!-- Error alert -->
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
          {{ loading ? "Signing in…" : "Sign in" }}
        </button>
      </form>

      <!-- Dev credentials hint -->
      <div v-if="isDev" class="mt-4 p-3 rounded bg-light border border-dashed">
        <p class="text-muted small mb-1 fw-medium">
          <i class="bi bi-info-circle me-1"></i>Development credentials
        </p>
        <code class="small d-block text-secondary">admin@demo.org</code>
        <code class="small d-block text-secondary">Admin123!</code>
        <button
          class="btn btn-outline-secondary btn-sm mt-2"
          @click="fillDemoCredentials"
        >
          Fill demo credentials
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const router = useRouter();
const authStore = useAuthStore();
const isDev = import.meta.env.DEV;

const form = reactive({ email: "", password: "" });
const errors = reactive({ email: "", password: "" });
const loading = ref(false);
const errorMessage = ref("");

function fillDemoCredentials() {
  form.email = "admin@demo.org";
  form.password = "Admin123!";
}

function validate(): boolean {
  errors.email = "";
  errors.password = "";
  if (!form.email) {
    errors.email = "Email is required";
    return false;
  }
  if (!form.password) {
    errors.password = "Password is required";
    return false;
  }
  return true;
}

async function handleLogin() {
  if (!validate()) return;

  loading.value = true;
  errorMessage.value = "";

  try {
    await authStore.login(form.email, form.password);
    const redirect =
      (router.currentRoute.value.query.redirect as string) || "/dashboard";
    await router.push(redirect);
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } };
    errorMessage.value =
      e.response?.data?.detail ||
      "Sign in failed. Please check your credentials.";
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

.border-dashed {
  border-style: dashed !important;
}
</style>
