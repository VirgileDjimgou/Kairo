<template>
  <div class="p-4 p-lg-5">
    <div class="mb-4">
      <div class="text-uppercase small fw-semibold text-secondary mb-2">
        Administration
      </div>
      <h1 class="h4 fw-bold mb-1">Tenant settings</h1>
      <p class="text-muted mb-0">
        Configure your organization name, branding, and enabled modules.
      </p>
    </div>

    <div v-if="loading" class="text-muted py-5 text-center">
      Loading settings...
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <template v-else-if="settings">
      <div class="row g-4">
        <div class="col-lg-7">
          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
              <h5 class="fw-semibold mb-3">Organization</h5>
              <div class="row g-3">
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Name</label>
                  <input v-model="form.name" type="text" class="form-control" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Slug</label>
                  <input :value="settings.slug" type="text" class="form-control" disabled />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Language</label>
                  <select v-model="form.default_language" class="form-select">
                    <option value="en">English</option>
                    <option value="fr">Français</option>
                    <option value="de">Deutsch</option>
                    <option value="nl">Nederlands</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
              <h5 class="fw-semibold mb-3">Branding</h5>
              <div class="row g-3">
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Primary color</label>
                  <div class="d-flex align-items-center gap-2">
                    <input v-model="form.branding.primary_color" type="color" class="form-control form-control-color w-auto" />
                    <input v-model="form.branding.primary_color" type="text" class="form-control" placeholder="#1f4f8f" />
                  </div>
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Logo URL</label>
                  <input v-model="form.branding.logo_url" type="text" class="form-control" placeholder="https://example.com/logo.png" />
                </div>
              </div>
            </div>
          </div>

          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
              <h5 class="fw-semibold mb-3">Modules</h5>
              <p class="small text-muted mb-3">
                Enable or disable product modules for this tenant. Disabled modules are hidden from users.
              </p>
              <div class="row g-2">
                <div v-for="(enabled, key) in form.modules" :key="key" class="col-sm-6">
                  <div class="form-check">
                    <input
                      :id="'module-' + key"
                      v-model="form.modules[key]"
                      type="checkbox"
                      class="form-check-input"
                    />
                    <label :for="'module-' + key" class="form-check-label text-capitalize">
                      {{ moduleLabel(key) }}
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-5">
          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
              <h5 class="fw-semibold mb-3">Summary</h5>
              <div class="vstack gap-2 small">
                <div class="d-flex justify-content-between">
                  <span class="text-muted">Status</span>
                  <span class="badge text-bg-success">Active</span>
                </div>
                <div class="d-flex justify-content-between">
                  <span class="text-muted">Modules enabled</span>
                  <span class="fw-semibold">{{ enabledCount }} / {{ totalModules }}</span>
                </div>
                <div class="d-flex justify-content-between">
                  <span class="text-muted">Language</span>
                  <span>{{ form.default_language.toUpperCase() }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="d-flex gap-2">
        <button class="btn om-primary-btn" :disabled="saving" @click="saveSettings">
          {{ saving ? 'Saving...' : 'Save settings' }}
        </button>
        <div v-if="saved" class="text-success small d-flex align-items-center">
          <i class="bi bi-check-circle me-1"></i> Settings saved
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth.store";
import { getTenantSettings, updateTenantSettings, type TenantSettingsResponse, type ModuleToggles, type BrandingConfig } from "../../api/settings.api";

const auth = useAuthStore();
const loading = ref(true);
const saving = ref(false);
const saved = ref(false);
const error = ref("");

const settings = ref<TenantSettingsResponse | null>(null);

const form = reactive<{
  name: string;
  default_language: string;
  branding: BrandingConfig;
  modules: ModuleToggles;
}>({
  name: "",
  default_language: "en",
  branding: { primary_color: "#1f4f8f", logo_url: "" },
  modules: {
    membership: true,
    contributions: true,
    policies: true,
    disciplinary: true,
    events: true,
    announcements: true,
    chat: true,
    notifications: true,
  },
});

const enabledCount = computed(() => {
  return Object.values(form.modules).filter(Boolean).length;
});

const totalModules = computed(() => {
  return Object.keys(form.modules).length;
});

function moduleLabel(key: string): string {
  const labels: Record<string, string> = {
    membership: "Membership",
    contributions: "Contributions",
    policies: "Policies",
    disciplinary: "Disciplinary",
    events: "Events",
    announcements: "Announcements",
    chat: "AI Chat",
    notifications: "Notifications",
  };
  return labels[key] || key;
}

async function loadSettings() {
  if (!auth.user?.tenant_id) return;
  loading.value = true;
  error.value = "";
  try {
    settings.value = await getTenantSettings(auth.user.tenant_id);
    form.name = settings.value.name;
    form.default_language = settings.value.default_language;
    form.branding = { ...settings.value.branding };
    form.modules = { ...settings.value.modules };
  } catch (err: unknown) {
    error.value = "Failed to load settings. Make sure you are logged in as admin.";
  } finally {
    loading.value = false;
  }
}

async function saveSettings() {
  if (!auth.user?.tenant_id) return;
  saving.value = true;
  saved.value = false;
  error.value = "";
  try {
    const result = await updateTenantSettings(auth.user.tenant_id, {
      name: form.name !== settings.value?.name ? form.name : undefined,
      default_language: form.default_language !== settings.value?.default_language ? form.default_language : undefined,
      branding: form.branding,
      modules: form.modules,
    });
    settings.value = result;
    saved.value = true;
    setTimeout(() => { saved.value = false; }, 3000);
  } catch (err: unknown) {
    error.value = "Failed to save settings. Check your permissions.";
  } finally {
    saving.value = false;
  }
}

onMounted(() => {
  loadSettings();
});
</script>
