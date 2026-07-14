import { defineStore } from "pinia";
import { ref } from "vue";
import {
  type ChatCitationResponse,
  type ChatConversationResponse,
  type ChatQueryResponse,
  listConversations,
  createConversation as apiCreateConversation,
  getConversation as apiGetConversation,
  deleteConversation as apiDeleteConversation,
  updateConversationTitle as apiUpdateConversationTitle,
  queryChat as apiQueryChat,
  queryChatStream as apiQueryChatStream,
} from "@/api/chat.api";
import { useLocaleStore } from "@/stores/locale.store";

export const useChatStore = defineStore("chat", () => {
  const localeStore = useLocaleStore();
  const conversations = ref<ChatConversationResponse[]>([]);
  const activeConversationId = ref<string | null>(null);
  const messages = ref<{ role: string; content: string; citations?: ChatCitationResponse[] }[]>([]);
  const streamingContent = ref("");
  const loading = ref(false);

  async function loadConversations() {
    try {
      conversations.value = await listConversations();
    } catch {
      // silent
    }
  }

  async function createConversation(title?: string) {
    const conv = await apiCreateConversation(title ?? localeStore.t("chat.newConversationTitle"));
    conversations.value.unshift(conv);
    activeConversationId.value = conv.id;
    messages.value = [];
    return conv;
  }

  async function selectConversation(id: string) {
    activeConversationId.value = id;
    streamingContent.value = "";
    try {
      const detail = await apiGetConversation(id);
      messages.value = detail.messages.map((m) => ({
        role: m.role,
        content: m.content,
        citations: normalizeCitations(m.citations_json),
      }));
    } catch {
      messages.value = [];
    }
  }

  async function deleteConv(id: string) {
    await apiDeleteConversation(id);
    conversations.value = conversations.value.filter((c) => c.id !== id);
    if (activeConversationId.value === id) {
      activeConversationId.value = null;
      messages.value = [];
    }
  }

  async function renameConv(id: string, title: string) {
    await apiUpdateConversationTitle(id, title);
    const conv = conversations.value.find((c) => c.id === id);
    if (conv) conv.title = title;
  }

  async function sendMessage(question: string, onToken?: (token: string) => void) {
    loading.value = true;
    streamingContent.value = "";
    messages.value.push({ role: "user", content: question });

    if (onToken) {
      // Streaming path
      const fullAnswer: string[] = [];
      await apiQueryChatStream(
        {
          question,
          conversation_id: activeConversationId.value,
          response_language: localeStore.currentLocale,
        },
          (token) => {
            fullAnswer.push(token);
            streamingContent.value = fullAnswer.join("");
            onToken(token);
          },
        (conversationId, _confidence, citations, _sourceTypes) => {
          messages.value.push({
            role: "assistant",
            content: streamingContent.value,
            citations,
          });
          streamingContent.value = "";
          activeConversationId.value = conversationId;
          loading.value = false;
          loadConversations();
        },
        (error) => {
          streamingContent.value = "";
          messages.value.push({
            role: "assistant",
            content: error || localeStore.t("chat.error"),
          });
          loading.value = false;
        },
        undefined,
        localeStore.t("chat.error"),
      );
    } else {
      // Non-streaming path
      try {
        const response: ChatQueryResponse = await apiQueryChat({
          question,
          conversation_id: activeConversationId.value,
          response_language: localeStore.currentLocale,
        });

        messages.value.push({
          role: "assistant",
          content: response.answer,
          citations: response.citations,
        });

        if (response.conversation_id) {
          activeConversationId.value = response.conversation_id;
        }

        loadConversations();
      } catch {
        messages.value.push({ role: "assistant", content: localeStore.t("chat.error") });
      } finally {
        loading.value = false;
      }
    }
  }

  return {
    conversations,
    activeConversationId,
    messages,
    streamingContent,
    loading,
    loadConversations,
    createConversation,
    selectConversation,
    deleteConv,
    renameConv,
    sendMessage,
  };
});

function normalizeCitations(raw: Array<Record<string, unknown> | ChatCitationResponse> | undefined): ChatCitationResponse[] {
  if (!raw?.length) {
    return [];
  }

  return raw.map((item) => {
    const record = item as Record<string, unknown>;
    return {
      chunk_id: String(record.chunk_id ?? record.chunkId ?? crypto.randomUUID()),
      document_id: String(record.document_id ?? record.documentId ?? crypto.randomUUID()),
      document_version_id: String(record.document_version_id ?? record.documentVersionId ?? crypto.randomUUID()),
      document_title: String(record.document_title ?? record.documentTitle ?? ""),
      excerpt: String(record.excerpt ?? ""),
      score: Number(record.score ?? 0),
    };
  });
}
