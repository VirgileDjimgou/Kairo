<template>
  <div class="chat-message d-flex gap-3 mb-4" :class="{ 'flex-row-reverse': role === 'user' }">
    <div
      class="avatar d-flex align-items-center justify-content-center rounded-circle flex-shrink-0"
      :class="role === 'user' ? 'bg-primary-subtle text-primary' : 'bg-success-subtle text-success'"
    >
      <i :class="role === 'user' ? 'bi bi-person' : 'bi bi-robot'"></i>
    </div>
    <div
      class="message-content p-3 rounded-3 flex-grow-1"
      :class="role === 'user' ? 'bg-primary-subtle border border-primary-subtle' : 'bg-white border'"
    >
      <div class="message-text" v-html="renderedContent"></div>
      <div v-if="citations && citations.length" class="mt-3 pt-2 border-top">
        <div class="small text-uppercase text-muted fw-semibold mb-1">{{ localeStore.t('chat.sources') }}</div>
        <div v-for="cite in citations" :key="cite.chunk_id" class="small text-muted mb-1">
          <i class="bi bi-file-text me-1"></i>
          {{ cite.document_title }}
          <span class="ms-1">
            <span class="badge bg-light text-dark">{{ (cite.score * 100).toFixed(0) }}%</span>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { ChatCitationResponse } from "@/api/chat.api";
import { useLocaleStore } from "@/stores/locale.store";

const props = defineProps<{
  role: string;
  content: string;
  citations?: ChatCitationResponse[] | undefined;
  isStreaming?: boolean;
}>();

const localeStore = useLocaleStore();

function simpleMarkdown(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/```(\w*)\n([\s\S]*?)```/g, "<pre class='bg-light p-2 rounded small'><code>$2</code></pre>")
    .replace(/`([^`]+)`/g, "<code class='bg-light px-1 rounded'>$1</code>")
    .replace(/\n/g, "<br>");
}

const renderedContent = computed(() => {
  const html = simpleMarkdown(props.content);
  if (props.isStreaming) {
    return html + '<span class="typing-cursor ms-1"></span>';
  }
  return html;
});
</script>

<style scoped>
.avatar {
  width: 36px;
  height: 36px;
  font-size: 1rem;
}

.message-content {
  max-width: 80%;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

:deep(.typing-cursor) {
  display: inline-block;
  width: 2px;
  height: 1.1em;
  background: var(--om-primary, #1f4f8f);
  animation: blink 0.8s step-end infinite;
  vertical-align: text-bottom;
}
</style>
