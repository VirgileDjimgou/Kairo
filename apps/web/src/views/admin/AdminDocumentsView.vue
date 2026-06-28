<template>
  <div class="p-4 p-lg-5">
    <div
      class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4"
    >
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          Documents
        </div>
        <h1 class="h4 fw-bold mb-1">Document intake</h1>
        <p class="text-muted mb-0">
          Upload tenant documents into object storage and review the latest
          version metadata.
        </p>
      </div>
      <button
        class="btn om-primary-btn align-self-start"
        type="button"
        @click="refreshDocuments"
        :disabled="loading"
      >
        {{ loading ? "Refreshing..." : "Refresh list" }}
      </button>
    </div>

    <div class="row g-4">
      <div class="col-lg-5">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-3">Upload a document</h2>

            <form class="vstack gap-3" @submit.prevent="submitUpload">
              <div>
                <label class="form-label">Title</label>
                <input
                  v-model.trim="title"
                  class="form-control"
                  type="text"
                  placeholder="Tenant policy"
                  required
                />
              </div>

              <div>
                <label class="form-label">Description</label>
                <textarea
                  v-model.trim="description"
                  class="form-control"
                  rows="3"
                  placeholder="Optional context for reviewers"
                />
              </div>

              <div>
                <label class="form-label">File</label>
                <input
                  class="form-control"
                  type="file"
                  accept=".pdf,.docx,.txt,.md,.csv,.png,.jpg,.jpeg,.webp"
                  @change="handleFileChange"
                  required
                />
                <div class="form-text">
                  Allowed: PDF, DOCX, TXT, MD, CSV, PNG, JPG, JPEG, WEBP.
                </div>
              </div>

              <div>
                <label class="form-label">Access scope</label>
                <select v-model="accessScope" class="form-select">
                  <option value="tenant_public">Tenant public</option>
                  <option value="members_only">Members only</option>
                  <option value="role_restricted">Role restricted</option>
                  <option value="user_private">User private</option>
                  <option value="admin_only">Admin only</option>
                </select>
              </div>

              <div class="d-flex gap-2">
                <button
                  class="btn om-primary-btn"
                  type="submit"
                  :disabled="uploading || !selectedFile"
                >
                  {{ uploading ? "Uploading..." : "Upload document" }}
                </button>
                <button
                  class="btn btn-outline-secondary"
                  type="button"
                  @click="resetForm"
                >
                  Reset
                </button>
              </div>

              <div v-if="statusMessage" class="alert alert-info mb-0">
                {{ statusMessage }}
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-lg-7">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">Latest documents</h2>
              <span class="badge bg-light text-dark"
                >{{ documents.length }} items</span
              >
            </div>

            <div v-if="loading" class="text-muted py-5 text-center">
              Loading documents...
            </div>

            <div v-else-if="documents.length === 0" class="empty-state">
              <i class="bi bi-file-earmark-text display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">No documents yet</p>
              <p class="text-muted mb-0">
                Upload the first tenant document to populate this list.
              </p>
            </div>

            <div v-else class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Access</th>
                    <th>Ingestion</th>
                    <th>File</th>
                    <th>Size</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="document in documents" :key="document.id">
                    <td>
                      <div class="fw-semibold">{{ document.title }}</div>
                      <div class="small text-muted">
                        {{ document.description || "No description" }}
                      </div>
                    </td>
                    <td>
                      <span
                        class="badge text-bg-success-subtle text-success border border-success-subtle"
                      >
                        {{ document.status }}
                      </span>
                    </td>
                    <td>
                      <div class="vstack gap-2">
                        <select
                          v-model="draftAccessScopeByDocument[document.id]"
                          class="form-select form-select-sm"
                        >
                          <option value="tenant_public">Tenant public</option>
                          <option value="members_only">Members only</option>
                          <option value="role_restricted">
                            Role restricted
                          </option>
                          <option value="user_private">User private</option>
                          <option value="admin_only">Admin only</option>
                        </select>
                        <input
                          v-model="draftAllowedRolesByDocument[document.id]"
                          class="form-control form-control-sm"
                          type="text"
                          placeholder="admin, member"
                          :disabled="
                            draftAccessScopeByDocument[document.id] !==
                            'role_restricted'
                          "
                        />
                        <div class="small text-muted">
                          {{
                            formatAllowedRoles(
                              document.allowed_role_ids,
                              document.id
                            )
                          }}
                        </div>
                      </div>
                    </td>
                    <td>
                      <span class="badge text-bg-light text-dark border">
                        {{ formatIngestionStatus(document.id) }}
                      </span>
                    </td>
                    <td>
                      <div class="fw-semibold">
                        {{ document.current_version?.file_name || "N/A" }}
                      </div>
                      <div class="small text-muted">
                        {{
                          document.current_version?.mime_type || "unknown type"
                        }}
                      </div>
                    </td>
                    <td>
                      {{
                        formatBytes(
                          document.current_version?.file_size_bytes ?? 0
                        )
                      }}
                    </td>
                    <td>
                      <div class="d-flex flex-column gap-2">
                        <button
                          class="btn btn-sm btn-outline-primary"
                          type="button"
                          @click="saveAccess(document.id)"
                          :disabled="busyDocumentId === document.id"
                        >
                          Save access
                        </button>
                        <button
                          class="btn btn-sm btn-outline-secondary"
                          type="button"
                          @click="queueReindex(document.id)"
                          :disabled="busyDocumentId === document.id"
                        >
                          Reindex
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  getIngestionJob,
  listDocuments,
  reindexDocument,
  updateDocumentAccess,
  uploadDocument,
  type DocumentListItemResponse,
} from "../../api/documents.api";

const documents = ref<DocumentListItemResponse[]>([]);
const loading = ref(false);
const uploading = ref(false);
const title = ref("");
const description = ref("");
const accessScope = ref("tenant_public");
const selectedFile = ref<File | null>(null);
const statusMessage = ref("");
const busyDocumentId = ref<string | null>(null);
const ingestionStatusByDocument = ref<Record<string, string>>({});
const ingestionJobByDocument = ref<Record<string, string>>({});
const draftAccessScopeByDocument = ref<Record<string, string>>({});
const draftAllowedRolesByDocument = ref<Record<string, string>>({});

function formatIngestionStatus(documentId: string): string {
  const status = ingestionStatusByDocument.value[documentId];
  const detail = ingestionDetailByDocument.value[documentId];
  if (!status) {
    return "unknown";
  }
  if (detail && status === "completed") {
    return `${status} (${detail.indexed}/${detail.chunks} indexed)`;
  }
  return status;
}

const ingestionDetailByDocument = ref<
  Record<string, { chunks: number; indexed: number }>
>({});

async function refreshDocuments() {
  loading.value = true;
  try {
    documents.value = await listDocuments();
    syncDocumentDrafts();
    await refreshIngestionStatuses();
  } finally {
    loading.value = false;
  }
}

function syncDocumentDrafts() {
  const nextScopes: Record<string, string> = {};
  const nextRoles: Record<string, string> = {};

  for (const document of documents.value) {
    nextScopes[document.id] = document.access_scope;
    nextRoles[document.id] = (document.allowed_role_ids ?? []).join(", ");
  }

  draftAccessScopeByDocument.value = nextScopes;
  draftAllowedRolesByDocument.value = nextRoles;
}

async function refreshIngestionStatuses() {
  const nextStatuses: Record<string, string> = {};
  const nextDetails: Record<string, { chunks: number; indexed: number }> = {};

  await Promise.all(
    Object.entries(ingestionJobByDocument.value).map(
      async ([documentId, jobId]) => {
        if (!documents.value.some((doc) => doc.id === documentId)) {
          return;
        }
        try {
          const job = await getIngestionJob(jobId);
          nextStatuses[documentId] = job.status;
          nextDetails[documentId] = {
            chunks: job.chunk_count,
            indexed: job.indexed_chunk_count,
          };
        } catch {
          nextStatuses[documentId] = "unknown";
        }
      }
    )
  );

  ingestionStatusByDocument.value = nextStatuses;
  ingestionDetailByDocument.value = nextDetails;
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  selectedFile.value = input.files?.[0] ?? null;
}

function formatAllowedRoles(roles: string[] | null, documentId: string): string {
  const draftScope = draftAccessScopeByDocument.value[documentId];
  const draftRoles = draftAllowedRolesByDocument.value[documentId]?.trim();

  if (draftScope === "role_restricted") {
    return draftRoles ? `Draft roles: ${draftRoles}` : "No roles selected yet";
  }

  if (!roles || roles.length === 0) {
    return "No role restriction";
  }

  return `Allowed roles: ${roles.join(", ")}`;
}

function parseAllowedRoles(documentId: string): string[] {
  const draftRoles = draftAllowedRolesByDocument.value[documentId] ?? "";
  return draftRoles
    .split(",")
    .map((role) => role.trim())
    .filter(Boolean);
}

async function saveAccess(documentId: string) {
  busyDocumentId.value = documentId;
  try {
    const updated = await updateDocumentAccess(documentId, {
      access_scope: draftAccessScopeByDocument.value[documentId] ?? "tenant_public",
      allowed_role_ids:
        draftAccessScopeByDocument.value[documentId] === "role_restricted"
          ? parseAllowedRoles(documentId)
          : null,
    });
    documents.value = documents.value.map((doc) =>
      doc.id === documentId ? updated : doc
    );
    syncDocumentDrafts();
    statusMessage.value = `Updated access for ${updated.title}.`;
  } finally {
    busyDocumentId.value = null;
  }
}

async function queueReindex(documentId: string) {
  busyDocumentId.value = documentId;
  try {
    const job = await reindexDocument(documentId);
    ingestionJobByDocument.value[documentId] = job.id;
    ingestionStatusByDocument.value[documentId] = job.status;
    statusMessage.value = `Reindex queued for document ${documentId}.`;
    await refreshDocuments();
  } finally {
    busyDocumentId.value = null;
  }
}

async function submitUpload() {
  if (!selectedFile.value) {
    statusMessage.value = "Choose a file before uploading.";
    return;
  }

  uploading.value = true;
  statusMessage.value = "";

  try {
    const uploaded = await uploadDocument({
      file: selectedFile.value,
      title: title.value,
      description: description.value || undefined,
      access_scope: accessScope.value,
    });
    ingestionJobByDocument.value[uploaded.id] = uploaded.ingestion_job_id;
    ingestionStatusByDocument.value[uploaded.id] = "pending";
    statusMessage.value = `Document uploaded. Ingestion job ${uploaded.ingestion_job_id} queued.`;
    resetForm();
    await refreshDocuments();
  } catch (error) {
    statusMessage.value = "Upload failed. Check the file type and size.";
    throw error;
  } finally {
    uploading.value = false;
  }
}

function resetForm() {
  title.value = "";
  description.value = "";
  accessScope.value = "tenant_public";
  selectedFile.value = null;
}

function formatBytes(value: number): string {
  if (value === 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];
  const unitIndex = Math.min(
    Math.floor(Math.log(value) / Math.log(1024)),
    units.length - 1
  );
  const scaled = value / 1024 ** unitIndex;
  return `${scaled.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

onMounted(async () => {
  await refreshDocuments();
});
</script>
