<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          Audit
        </div>
        <h1 class="h4 fw-bold mb-1">Chat traceability</h1>
        <p class="text-muted mb-0">
          Review minimized RAG traces, refusal reasons, source types, and citation counts.
        </p>
      </div>
      <button
        class="btn om-primary-btn align-self-start"
        type="button"
        @click="refreshQueries"
        :disabled="loading"
      >
        {{ loading ? "Refreshing..." : "Refresh log" }}
      </button>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-sm-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body text-center py-3">
            <div class="fs-4 fw-bold">{{ stats.total }}</div>
            <div class="small text-muted">Total queries</div>
          </div>
        </div>
      </div>
      <div class="col-sm-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body text-center py-3">
            <div class="fs-4 fw-bold text-success">{{ stats.answered }}</div>
            <div class="small text-muted">Answered</div>
          </div>
        </div>
      </div>
      <div class="col-sm-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body text-center py-3">
            <div class="fs-4 fw-bold text-warning">{{ stats.refused }}</div>
            <div class="small text-muted">Refused</div>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0 mb-4">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <div class="col-sm-6 col-md-4">
            <label class="form-label small fw-semibold text-muted mb-1">Search question</label>
            <input
              v-model="searchText"
              type="text"
              class="form-control form-control-sm"
              placeholder="Filter by question text..."
            />
          </div>
          <div class="col-sm-3 col-md-2">
            <label class="form-label small fw-semibold text-muted mb-1">Status</label>
            <select v-model="statusFilter" class="form-select form-select-sm">
              <option value="all">All</option>
              <option value="answered">Answered</option>
              <option value="refused">Refused</option>
            </select>
          </div>
          <div class="col-sm-3 col-md-2">
            <label class="form-label small fw-semibold text-muted mb-1">Max results</label>
            <select v-model="limit" class="form-select form-select-sm">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-body p-4">
        <div v-if="loading" class="text-muted py-5 text-center">
          Loading query log...
        </div>

        <div v-else-if="queries.length === 0" class="empty-state">
          <i class="bi bi-journal-text display-6 text-secondary"></i>
          <p class="mb-1 fw-semibold">No matching queries</p>
          <p class="text-muted mb-0">
            Try adjusting the filters or wait for users to interact with the RAG assistant.
          </p>
        </div>

        <div v-else class="vstack gap-3">
          <article v-for="query in queries" :key="query.id" class="audit-card">
            <div class="d-flex justify-content-between gap-3 flex-wrap mb-2">
              <div>
                <div class="fw-semibold">{{ query.question_preview }}</div>
                <div class="small text-muted">
                  {{ formatDate(query.created_at) }} · {{ shortUser(query.user_id) }}
                </div>
              </div>
              <div class="d-flex align-items-center gap-2">
                <span
                  :class="query.refused ? 'badge text-bg-warning-subtle text-warning border border-warning-subtle' : 'badge text-bg-success-subtle text-success border border-success-subtle'"
                >
                  {{ query.refused ? "Refused" : "Answered" }}
                </span>
                <span class="badge text-bg-light text-dark border">
                  confidence {{ formatConfidence(query.confidence) }}
                </span>
              </div>
            </div>

            <div class="mb-3">
              <div class="small text-uppercase text-muted fw-semibold mb-1">
                Answer
              </div>
              <div class="query-answer">{{ query.answer_preview }}</div>
            </div>

            <div v-if="query.refusal_reason_preview" class="mb-3">
              <div class="small text-uppercase text-muted fw-semibold mb-1">
                Refusal reason
              </div>
              <div class="text-muted">{{ query.refusal_reason_preview }}</div>
            </div>

            <div v-if="query.source_types.length" class="mb-3">
              <div class="small text-uppercase text-muted fw-semibold mb-1">
                Source types
              </div>
              <div class="d-flex flex-wrap gap-2">
                <span
                  v-for="sourceType in query.source_types"
                  :key="sourceType"
                  class="badge rounded-pill text-bg-light text-dark border"
                >
                  {{ formatSourceType(sourceType) }}
                </span>
              </div>
            </div>

            <div class="small text-muted">
              Citations referenced: {{ query.citation_count }}
            </div>
          </article>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { listChatQueries, type ChatQueryLogResponse } from "../../api/documents.api";

const loading = ref(false);
const queries = ref<ChatQueryLogResponse[]>([]);
const searchText = ref("");
const statusFilter = ref("all");
const limit = ref(20);

const stats = computed(() => {
  const total = queries.value.length;
  const refused = queries.value.filter((q) => q.refused).length;
  return { total, answered: total - refused, refused };
});

async function refreshQueries() {
  loading.value = true;
  try {
    queries.value = await listChatQueries({
      limit: limit.value,
      search: searchText.value || undefined,
      refused:
        statusFilter.value === "all"
          ? undefined
          : statusFilter.value === "refused",
    });
  } finally {
    loading.value = false;
  }
}

watch([limit, searchText, statusFilter], () => {
  refreshQueries();
});

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

function shortUser(userId: string): string {
  return `User ${userId.slice(0, 8)}`;
}

function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function formatSourceType(sourceType: string): string {
  return sourceType
    .replace(/^structured:/, "structured ")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

onMounted(async () => {
  await refreshQueries();
});
</script>

<style scoped>
.audit-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: #fff;
  padding: 1rem;
}

.query-answer {
  white-space: pre-wrap;
}

</style>
