<template>
  <div class="chat-sidebar d-flex flex-column h-100 bg-light border-end">
    <div class="p-3 border-bottom">
      <button class="btn om-primary-btn w-100" @click="$emit('new')">
        <i class="bi bi-plus-lg me-1"></i>
        {{ localeStore.t('chat.newConversation') }}
      </button>
    </div>
    <div class="flex-grow-1 overflow-auto">
      <div
        v-for="conv in conversations"
        :key="conv.id"
        class="sidebar-item p-3 border-bottom cursor-pointer"
        :class="{ active: conv.id === activeId }"
        @click="$emit('select', conv.id)"
      >
        <div class="d-flex justify-content-between align-items-start">
          <div class="text-truncate fw-medium small">{{ conv.title }}</div>
          <button
            class="btn btn-sm btn-link text-muted p-0 ms-1 flex-shrink-0"
            @click.stop="handleDelete(conv.id)"
            :title="localeStore.t('chat.delete')"
          >
            <i class="bi bi-trash3"></i>
          </button>
        </div>
        <div v-if="conv.last_message_preview" class="text-muted text-truncate small mt-1">
          {{ conv.last_message_preview }}
        </div>
        <div class="text-muted small mt-1">
          {{ conv.message_count }} {{ localeStore.t('chat.messages') }}
        </div>
      </div>
      <div v-if="!conversations.length" class="p-4 text-center text-muted small">
        {{ localeStore.t('chat.noConversations') }}
      </div>
    </div>
    <div class="p-3 border-top small text-muted">
      <i class="bi bi-clock-history me-1"></i>
      {{ conversations.length }} {{ localeStore.t('chat.conversations') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatConversationResponse } from "@/api/chat.api";
import { useLocaleStore } from "@/stores/locale.store";

defineProps<{
  conversations: ChatConversationResponse[];
  activeId: string | null;
}>();

const emit = defineEmits<{
  (e: "new"): void;
  (e: "select", id: string): void;
  (e: "delete", id: string): void;
}>();

const localeStore = useLocaleStore();

function handleDelete(id: string) {
  if (confirm(localeStore.t("chat.confirmDelete"))) {
    emit("delete", id);
  }
}
</script>

<style scoped>
.chat-sidebar {
  width: 280px;
  min-width: 280px;
}

.sidebar-item {
  transition: background 0.15s;
}

.sidebar-item:hover {
  background: rgba(31, 79, 143, 0.04);
}

.sidebar-item.active {
  background: rgba(31, 79, 143, 0.1);
  border-left: 3px solid var(--om-primary, #1f4f8f);
}

.cursor-pointer {
  cursor: pointer;
}
</style>
