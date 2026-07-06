<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          AI chat
        </div>
        <h1 class="h4 fw-bold mb-1">Grounded organizational assistant</h1>
        <p class="text-muted mb-0">
          Ask a question and get answers grounded in authorized documents and role-safe structured facts.
        </p>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-5">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <h2 class="h6 fw-bold mb-3">Ask a question</h2>
            <form class="vstack gap-3" @submit.prevent="submitQuestion">
              <div>
                <label class="form-label">Question</label>
                <textarea
                  v-model.trim="question"
                  class="form-control"
                  rows="6"
                  placeholder="What is the membership fee due date?"
                  required
                />
              </div>
              <button class="btn om-primary-btn" type="submit" :disabled="loading || !question">
                {{ loading ? "Thinking..." : "Ask question" }}
              </button>
            </form>

            <div v-if="suggestedPrompts.length" class="mt-4">
              <div class="small text-uppercase text-muted fw-semibold mb-2">
                Suggested prompts for your role
              </div>
              <div class="d-flex flex-wrap gap-2">
                <button
                  v-for="prompt in suggestedPrompts"
                  :key="prompt"
                  class="btn btn-sm btn-outline-secondary rounded-pill"
                  type="button"
                  @click="setQuestion(prompt)"
                >
                  {{ prompt }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-7">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between mb-3">
              <h2 class="h6 fw-bold mb-0">Answer</h2>
              <span class="badge bg-light text-dark">
                Confidence {{ result?.confidence.toFixed(2) ?? "0.00" }}
              </span>
            </div>

            <div v-if="errorMessage" class="alert alert-danger">
              {{ errorMessage }}
            </div>

            <div v-else-if="!result" class="empty-state">
              <i class="bi bi-chat-dots display-6 text-secondary"></i>
              <p class="mb-1 fw-semibold">No answer yet</p>
              <p class="text-muted mb-0">
                Submit a question to retrieve and cite authorized sources.
              </p>
            </div>

            <template v-else>
              <div class="answer-box rounded-3 p-3 mb-3">
                <div class="small text-uppercase text-muted fw-semibold mb-2">
                  {{ result.refused ? "Refused" : "Answer" }}
                </div>
                <p class="mb-0">{{ result.answer }}</p>
              </div>

              <div class="mb-2">
                <span
                  class="badge"
                  :class="result.refused ? 'bg-warning-subtle text-warning border border-warning-subtle' : 'bg-success-subtle text-success border border-success-subtle'"
                >
                  {{ result.refused ? "No source found" : "Sources found" }}
                </span>
                <span v-if="result.refusal_reason" class="ms-2 small text-muted">
                  {{ result.refusal_reason }}
                </span>
              </div>

              <div v-if="result.source_types.length" class="mb-3">
                <div class="small text-uppercase text-muted fw-semibold mb-1">
                  Source types
                </div>
                <div class="d-flex flex-wrap gap-2">
                  <span
                    v-for="sourceType in result.source_types"
                    :key="sourceType"
                    class="badge rounded-pill text-bg-light text-dark border"
                  >
                    {{ formatSourceType(sourceType) }}
                  </span>
                </div>
              </div>

              <div v-if="result.citations.length" class="vstack gap-2">
                <div
                  v-for="citation in result.citations"
                  :key="citation.chunk_id"
                  class="border rounded-3 p-3"
                >
                  <div class="fw-semibold">{{ citation.document_title }}</div>
                  <div class="small text-muted mb-2">
                    Score {{ citation.score.toFixed(2) }} · Chunk {{ citation.chunk_id.slice(0, 8) }}
                  </div>
                  <div>{{ citation.excerpt }}</div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { queryChat, type ChatQueryResponse } from "@/api/chat.api";
import { useAuthStore } from "@/stores/auth.store";

const authStore = useAuthStore();
const question = ref("");
const loading = ref(false);
const errorMessage = ref("");
const result = ref<ChatQueryResponse | null>(null);
const roles = computed(() => authStore.user?.roles ?? []);

const suggestedPrompts = computed(() => {
  if (roles.value.includes("principal_admin") || roles.value.includes("admin")) {
    return [
      "Give me a governance summary.",
      "Show the official publication context.",
      "Give me a disciplinary summary.",
      "Show the sports schedule.",
    ];
  }

  if (roles.value.includes("president") || roles.value.includes("vice_president")) {
    return [
      "Give me a governance summary.",
      "How many members are active?",
      "What is the current organization overview?",
    ];
  }

  if (roles.value.includes("secretary_general")) {
    return [
      "Show the official publication context.",
      "What announcements are active?",
      "Which policies are ready to publish?",
    ];
  }

  if (roles.value.includes("auditor")) {
    return [
      "Give me the tenant finance summary.",
      "What is the outstanding balance?",
      "What is the collection rate?",
    ];
  }

  if (roles.value.includes("censor")) {
    return [
      "Give me a disciplinary summary.",
      "How many cases are open?",
      "What is the sanctions overview?",
    ];
  }

  if (roles.value.includes("sports_manager")) {
    return [
      "Show the sports schedule.",
      "What is the next sports event?",
      "Which training sessions are upcoming?",
    ];
  }

  return [
    "What is my balance?",
    "What announcements are active?",
    "What events are visible to me?",
  ];
});

async function submitQuestion() {
  loading.value = true;
  errorMessage.value = "";

  try {
    result.value = await queryChat({ question: question.value, top_k: 4 });
  } catch (error) {
    errorMessage.value = "Chat query failed. Please try again.";
    throw error;
  } finally {
    loading.value = false;
  }
}

function setQuestion(prompt: string) {
  question.value = prompt;
}

function formatSourceType(sourceType: string): string {
  return sourceType
    .replace(/^structured:/, "structured ")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}
</script>

<style scoped>
.answer-box {
  background: rgba(31, 79, 143, 0.06);
  border: 1px solid rgba(31, 79, 143, 0.12);
}
</style>
