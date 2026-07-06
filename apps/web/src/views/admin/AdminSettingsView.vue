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

          <div class="card shadow-sm border-0 mb-4">
            <div class="card-body p-4">
              <div class="d-flex flex-column flex-md-row justify-content-between gap-2 mb-3">
                <div>
                  <h5 class="fw-semibold mb-1">Recovery evidence</h5>
                  <p class="small text-muted mb-0">
                    Record the latest backup and restore drill evidence so operators can see whether recovery posture is fresh.
                  </p>
                </div>
                <span class="badge text-bg-light border align-self-start text-capitalize">
                  {{ settings?.operations.overall_status || 'unknown' }}
                </span>
              </div>

              <div v-if="settings?.operations.status_message" class="alert" :class="recoveryAlertClass(settings.operations.overall_status)">
                {{ settings.operations.status_message }}
              </div>

              <div class="row g-3">
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Last backup at</label>
                  <input v-model="form.operations.last_backup_at" type="datetime-local" class="form-control" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Backup status</label>
                  <select v-model="form.operations.last_backup_status" class="form-select">
                    <option value="unknown">Unknown</option>
                    <option value="scheduled">Scheduled</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Backup reference</label>
                  <input v-model="form.operations.last_backup_reference" type="text" class="form-control" placeholder="kairo-backup-20260704_030000.tar.gz" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Retention days</label>
                  <input v-model.number="form.operations.backup_retention_days" type="number" min="1" class="form-control" placeholder="30" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Last restore drill at</label>
                  <input v-model="form.operations.last_restore_drill_at" type="datetime-local" class="form-control" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Restore drill status</label>
                  <select v-model="form.operations.last_restore_drill_status" class="form-select">
                    <option value="unknown">Unknown</option>
                    <option value="not_run">Not run</option>
                    <option value="passed">Passed</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>
                <div class="col-sm-6">
                  <label class="form-label small fw-semibold text-muted">Alert posture</label>
                  <select v-model="form.operations.alert_posture" class="form-select">
                    <option value="unknown">Unknown</option>
                    <option value="healthy">Healthy</option>
                    <option value="warning">Warning</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div class="col-sm-6 d-flex align-items-end">
                  <div class="form-check mt-4">
                    <input
                      id="alert-contacts-configured"
                      v-model="form.operations.alert_contacts_configured"
                      type="checkbox"
                      class="form-check-input"
                    />
                    <label class="form-check-label" for="alert-contacts-configured">
                      Alert contacts configured
                    </label>
                  </div>
                </div>
                <div class="col-12">
                  <label class="form-label small fw-semibold text-muted">Notes</label>
                  <textarea v-model="form.operations.notes" rows="3" class="form-control" placeholder="Add a short note about the latest recovery drill or backup handoff."></textarea>
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
import {
  getTenantSettings,
  updateTenantSettings,
  checkModuleHasData,
  type TenantSettingsResponse,
  type ModuleToggles,
  type BrandingConfig,
  type RecoveryEvidenceConfig,
} from "../../api/settings.api";

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
  operations: {
    last_backup_at: string;
    last_backup_status: string;
    last_backup_reference: string;
    last_restore_drill_at: string;
    last_restore_drill_status: string;
    alert_posture: string;
    alert_contacts_configured: boolean;
    backup_retention_days: number | null;
    notes: string;
  };
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
  operations: {
    last_backup_at: "",
    last_backup_status: "unknown",
    last_backup_reference: "",
    last_restore_drill_at: "",
    last_restore_drill_status: "unknown",
    alert_posture: "unknown",
    alert_contacts_configured: false,
    backup_retention_days: null,
    notes: "",
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
    form.operations = {
      last_backup_at: toDateTimeLocal(settings.value.operations.last_backup_at),
      last_backup_status: settings.value.operations.last_backup_status || "unknown",
      last_backup_reference: settings.value.operations.last_backup_reference || "",
      last_restore_drill_at: toDateTimeLocal(settings.value.operations.last_restore_drill_at),
      last_restore_drill_status: settings.value.operations.last_restore_drill_status || "unknown",
      alert_posture: settings.value.operations.alert_posture || "unknown",
      alert_contacts_configured: settings.value.operations.alert_contacts_configured,
      backup_retention_days: settings.value.operations.backup_retention_days,
      notes: settings.value.operations.notes || "",
    };
  } catch (err: unknown) {
    error.value = "Failed to load settings. Make sure you are logged in as admin.";
  } finally {
    loading.value = false;
  }
}

async function saveSettings() {
  if (!auth.user?.tenant_id) return;

  // Warn if disabling a module that has existing data
  const disabledModules = Object.keys(form.modules).filter(
    (key) => !form.modules[key as keyof ModuleToggles]
  );
  for (const module of disabledModules) {
    const hasData = await checkModuleHasData(auth.user.tenant_id, module);
    if (hasData) {
      const confirmed = confirm(
        `"${moduleLabel(module)}" has existing data. Disabling it will hide that data from users. Are you sure?`
      );
      if (!confirmed) return;
      break;
    }
  }

  saving.value = true;
  saved.value = false;
  error.value = "";
  try {
    const result = await updateTenantSettings(auth.user.tenant_id, {
      name: form.name !== settings.value?.name ? form.name : undefined,
      default_language: form.default_language !== settings.value?.default_language ? form.default_language : undefined,
      branding: form.branding,
      modules: form.modules,
      operations: buildOperationsPayload(),
    });
    settings.value = result;
    form.operations = {
      last_backup_at: toDateTimeLocal(result.operations.last_backup_at),
      last_backup_status: result.operations.last_backup_status || "unknown",
      last_backup_reference: result.operations.last_backup_reference || "",
      last_restore_drill_at: toDateTimeLocal(result.operations.last_restore_drill_at),
      last_restore_drill_status: result.operations.last_restore_drill_status || "unknown",
      alert_posture: result.operations.alert_posture || "unknown",
      alert_contacts_configured: result.operations.alert_contacts_configured,
      backup_retention_days: result.operations.backup_retention_days,
      notes: result.operations.notes || "",
    };
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

function toDateTimeLocal(value: string | null): string {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toIsoOrNull(value: string): string | null {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function buildOperationsPayload(): Partial<RecoveryEvidenceConfig> {
  return {
    last_backup_at: toIsoOrNull(form.operations.last_backup_at),
    last_backup_status: form.operations.last_backup_status,
    last_backup_reference: form.operations.last_backup_reference,
    last_restore_drill_at: toIsoOrNull(form.operations.last_restore_drill_at),
    last_restore_drill_status: form.operations.last_restore_drill_status,
    alert_posture: form.operations.alert_posture,
    alert_contacts_configured: form.operations.alert_contacts_configured,
    backup_retention_days: form.operations.backup_retention_days ?? undefined,
    notes: form.operations.notes,
  };
}

function recoveryAlertClass(status: string): string {
  if (status === "healthy") return "alert-success";
  if (status === "critical") return "alert-danger";
  return "alert-warning";
}
</script>
