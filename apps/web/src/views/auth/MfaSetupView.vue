<template>
  <div class="container py-4" style="max-width: 480px">
    <div class="card shadow-sm border-0 p-4">
      <div class="text-center mb-4">
        <i class="bi bi-shield-check fs-1 text-primary"></i>
        <h2 class="h5 fw-bold mt-2 mb-1">Two-factor authentication</h2>
        <p class="text-muted small mb-0">
          Add an extra layer of security to your account.
        </p>
      </div>

      <!-- Enrollment step 1: generate secret -->
      <div v-if="step === 'enroll'">
        <p class="small text-muted">
          Scan this QR code with your authenticator app (e.g. Google Authenticator, Authy).
        </p>

        <div class="text-center mb-3">
          <div v-if="qrCodeUrl" class="border rounded d-inline-block p-2 bg-light">
            <img :src="qrCodeUrl" alt="QR Code" style="width: 180px; height: 180px" />
          </div>
          <div v-else class="border rounded d-inline-block p-3 bg-light">
            <code class="small text-break">{{ secret }}</code>
          </div>
        </div>

        <p class="small text-muted text-center">
          Can't scan? Manually enter the key: <code class="text-break">{{ secret }}</code>
        </p>

        <hr />
        <label for="verify-code" class="form-label fw-medium">Verify the code</label>
        <div class="input-group mb-3">
          <input
            id="verify-code"
            v-model="verifyCode"
            type="text"
            class="form-control text-center"
            placeholder="000000"
            maxlength="6"
            autocomplete="off"
          />
          <button
            class="btn btn-primary"
            :disabled="verifyCode.length !== 6 || loading"
            @click="handleVerify"
          >
            <span
              v-if="loading"
              class="spinner-border spinner-border-sm me-1"
              role="status"
            ></span>
            Verify
          </button>
        </div>

        <div v-if="errorMessage" class="alert alert-danger py-2 small" role="alert">
          <i class="bi bi-exclamation-circle me-1"></i>{{ errorMessage }}
        </div>
      </div>

      <!-- MFA enabled -->
      <div v-else-if="step === 'done'" class="text-center">
        <i class="bi bi-check-circle fs-1 text-success"></i>
        <p class="mt-2 mb-1 fw-medium">MFA is now enabled</p>
        <p class="text-muted small">
          You'll be prompted for a code each time you sign in.
        </p>
        <router-link to="/members/profile" class="btn btn-primary mt-2">
          Back to profile
        </router-link>
      </div>

      <!-- Error / not started -->
      <div v-else>
        <button class="btn btn-primary w-100" :disabled="loading" @click="handleEnroll">
          <span
            v-if="loading"
            class="spinner-border spinner-border-sm me-1"
            role="status"
          ></span>
          Set up two-factor authentication
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { enrollMfa, verifyMfa } from "@/api/auth.api";

type Step = "idle" | "enroll" | "done";

const step = ref<Step>("idle");
const secret = ref("");
const qrCodeUrl = ref("");
const verifyCode = ref("");
const loading = ref(false);
const errorMessage = ref("");

async function handleEnroll() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const result = await enrollMfa();
    secret.value = result.secret;
    qrCodeUrl.value = result.qr_code_url;
    step.value = "enroll";
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } };
    errorMessage.value = e.response?.data?.detail || "Failed to set up MFA.";
  } finally {
    loading.value = false;
  }
}

async function handleVerify() {
  if (verifyCode.value.length !== 6) return;
  loading.value = true;
  errorMessage.value = "";
  try {
    await verifyMfa({ code: verifyCode.value });
    step.value = "done";
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } };
    errorMessage.value = e.response?.data?.detail || "Invalid code. Try again.";
  } finally {
    loading.value = false;
  }
}
</script>
