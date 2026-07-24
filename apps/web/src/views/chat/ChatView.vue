<template>
  <div class="chat-view d-flex">
    <ChatSidebar
      :conversations="chatStore.conversations"
      :active-id="chatStore.activeConversationId"
      :visible="showSidebar"
      class="chat-sidebar-wrapper"
      @new="handleNewConversation"
      @select="handleSelectConversation"
      @delete="handleDeleteConversation"
    />

    <div v-if="!showSidebar || !isNarrow" class="chat-main d-flex flex-column flex-grow-1">
      <div v-if="isNarrow && chatStore.activeConversationId" class="chat-mobile-header px-3 py-2 border-bottom bg-white">
        <button class="btn btn-link p-0 text-decoration-none d-flex align-items-center gap-2" @click="showSidebar = true">
          <i class="bi bi-chevron-left"></i>
          <span class="fw-medium small">{{ localeStore.t('chat.conversations') }}</span>
        </button>
      </div>

      <div v-if="chatStore.messages.length || chatStore.streamingContent" class="messages-area flex-grow-1 overflow-auto p-3 p-md-4">
        <ChatMessage
          v-for="(msg, i) in chatStore.messages"
          :key="i"
          :role="msg.role"
          :content="msg.content"
          :citations="msg.citations"
        />
        <ChatMessage
          v-if="chatStore.streamingContent"
          role="assistant"
          :content="chatStore.streamingContent"
          :is-streaming="true"
        />
        <FollowUpChips
          v-if="chatStore.messages.length && !chatStore.loading"
          :suggestions="suggestedPrompts.slice(0, 3)"
          @select="handleFollowUp"
        />
      </div>

      <div v-else class="empty-state flex-grow-1 d-flex flex-column align-items-center justify-content-center p-4">
        <i class="bi bi-chat-dots display-1 text-secondary mb-3"></i>
        <h2 class="h5 fw-bold mb-1">{{ localeStore.t('chat.title') }}</h2>
        <p class="text-muted mb-4 text-center" style="max-width: 400px;">
          {{ localeStore.t('chat.noAnswerText') }}
        </p>
        <div class="d-flex flex-wrap gap-2 justify-content-center">
          <button
            v-for="prompt in suggestedPrompts"
            :key="prompt"
            class="btn btn-sm btn-outline-secondary rounded-pill"
            type="button"
            @click="handleFollowUp(prompt)"
          >
            {{ prompt }}
          </button>
        </div>
      </div>

      <div class="input-area p-3 border-top bg-white">
        <form class="d-flex gap-2" @submit.prevent="handleSubmit">
          <textarea
            v-model.trim="question"
            class="form-control chat-input"
            rows="2"
            :placeholder="localeStore.t('chat.questionPlaceholder')"
            required
            @keydown.enter.exact.prevent="handleSubmit"
          />
          <button class="btn om-primary-btn flex-shrink-0" type="submit" :disabled="chatStore.loading || !question">
            <i v-if="chatStore.loading" class="bi bi-arrow-repeat spin me-1"></i>
            <i v-else class="bi bi-send me-1"></i>
            {{ chatStore.loading ? localeStore.t('chat.thinking') : localeStore.t('chat.ask') }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { getChatDomainPolicy } from "@/api/chat.api";
import ChatSidebar from "@/components/chat/ChatSidebar.vue";
import ChatMessage from "@/components/chat/ChatMessage.vue";
import FollowUpChips from "@/components/chat/FollowUpChips.vue";
import { useChatStore } from "@/stores/chat.store";
import { useLocaleStore } from "@/stores/locale.store";

const chatStore = useChatStore();
const localeStore = useLocaleStore();

const question = ref("");
const allowedDomains = ref<string[]>([]);
const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024);
const showSidebar = ref(true);

const isNarrow = computed(() => windowWidth.value < 768);

let resizeTimer: ReturnType<typeof setTimeout> | null = null;

function onResize() {
  if (resizeTimer) clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    windowWidth.value = window.innerWidth;
    if (window.innerWidth >= 768) {
      showSidebar.value = true;
    }
  }, 80);
}

const suggestedPrompts = computed(() => {
  const prompts = {
    fr: {
      governanceSummary: "Donne-moi un résumé de gouvernance.",
      officialPublication: "Montre-moi le contexte officiel de publication.",
      disciplinarySummary: "Donne-moi un résumé disciplinaire.",
      sportsCalendar: "Montre-moi le calendrier sportif.",
      activeMembers: "Combien de membres sont actifs ?",
      orgOverview: "Quel est l'aperçu actuel de l'organisation ?",
      activeAnnouncements: "Quelles annonces sont actives ?",
      readyDocuments: "Quels documents sont prêts à être publiés ?",
      financeSummary: "Donne-moi le résumé financier du tenant.",
      remainingBalance: "Quel est le solde restant ?",
      collectionRate: "Quel est le taux de recouvrement ?",
      openCases: "Combien de dossiers sont ouverts ?",
      sanctionsOverview: "Quel est l'aperçu des sanctions ?",
      nextSportsEvent: "Quel est le prochain événement sportif ?",
      nextTrainings: "Quelles séances d'entraînement arrivent ?",
      myBalance: "Quel est mon solde ?",
      visibleEvents: "Quels événements sont visibles pour moi ?",
    },
    en: {
      governanceSummary: "Give me a governance summary.",
      officialPublication: "Show me the official publication context.",
      disciplinarySummary: "Give me a disciplinary summary.",
      sportsCalendar: "Show me the sports calendar.",
      activeMembers: "How many members are active?",
      orgOverview: "What is the current organization overview?",
      activeAnnouncements: "Which announcements are active?",
      readyDocuments: "Which documents are ready to be published?",
      financeSummary: "Give me the tenant finance summary.",
      remainingBalance: "What is the remaining balance?",
      collectionRate: "What is the collection rate?",
      openCases: "How many cases are open?",
      sanctionsOverview: "What is the sanctions overview?",
      nextSportsEvent: "What is the next sports event?",
      nextTrainings: "Which training sessions are coming up?",
      myBalance: "What is my balance?",
      visibleEvents: "Which events are visible to me?",
    },
    de: {
      governanceSummary: "Gib mir eine Governance-Zusammenfassung.",
      officialPublication: "Zeige mir den offiziellen Publikationskontext.",
      disciplinarySummary: "Gib mir eine disziplinarische Zusammenfassung.",
      sportsCalendar: "Zeige mir den Sportkalender.",
      activeMembers: "Wie viele Mitglieder sind aktiv?",
      orgOverview: "Wie sieht der aktuelle Vereinsueberblick aus?",
      activeAnnouncements: "Welche Ankuendigungen sind aktiv?",
      readyDocuments: "Welche Dokumente sind zur Veroeffentlichung bereit?",
      financeSummary: "Gib mir die Finanzzusammenfassung des Tenants.",
      remainingBalance: "Wie hoch ist der Restsaldo?",
      collectionRate: "Wie hoch ist die Einzugsquote?",
      openCases: "Wie viele Faelle sind offen?",
      sanctionsOverview: "Wie sieht die Sanktionsuebersicht aus?",
      nextSportsEvent: "Was ist das naechste Sportereignis?",
      nextTrainings: "Welche Trainingseinheiten kommen als naechstes?",
      myBalance: "Wie hoch ist mein Saldo?",
      visibleEvents: "Welche Veranstaltungen sind fuer mich sichtbar?",
    },
  }[localeStore.currentLocale];

  const suggestions: string[] = [];

  if (allowedDomains.value.includes("member_finance")) {
    suggestions.push(prompts.myBalance);
  }
  if (allowedDomains.value.includes("tenant_finance")) {
    suggestions.push(prompts.financeSummary, prompts.remainingBalance, prompts.collectionRate);
  }
  if (allowedDomains.value.includes("governance")) {
    suggestions.push(prompts.governanceSummary, prompts.activeMembers, prompts.orgOverview);
  }
  if (allowedDomains.value.includes("publication")) {
    suggestions.push(prompts.officialPublication, prompts.activeAnnouncements);
  }
  if (allowedDomains.value.includes("disciplinary")) {
    suggestions.push(prompts.disciplinarySummary, prompts.openCases, prompts.sanctionsOverview);
  }
  if (allowedDomains.value.includes("sports")) {
    suggestions.push(prompts.sportsCalendar, prompts.nextSportsEvent, prompts.nextTrainings);
  }
  if (!suggestions.includes(prompts.visibleEvents)) {
    suggestions.push(prompts.visibleEvents);
  }

  return suggestions.slice(0, 4);
});

onMounted(() => {
  chatStore.loadConversations();
  void loadDomainPolicy();
  window.addEventListener('resize', onResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', onResize);
  if (resizeTimer) clearTimeout(resizeTimer);
});

async function loadDomainPolicy() {
  try {
    const response = await getChatDomainPolicy();
    allowedDomains.value = response.allowed_domains;
  } catch {
    allowedDomains.value = [];
  }
}

async function handleSubmit() {
  const q = question.value;
  if (!q.trim()) {
    return;
  }
  question.value = "";

  if (!chatStore.activeConversationId) {
    await chatStore.createConversation(localeStore.t('chat.newConversationTitle'));
  }

  await chatStore.sendMessage(q, () => undefined);
}

async function handleNewConversation() {
  await chatStore.createConversation(localeStore.t('chat.newConversationTitle'));
  if (isNarrow.value) {
    showSidebar.value = false;
  }
}

function handleSelectConversation(id: string) {
  chatStore.selectConversation(id);
  if (isNarrow.value) {
    showSidebar.value = false;
  }
}

function handleDeleteConversation(id: string) {
  chatStore.deleteConv(id);
}

function handleFollowUp(text: string) {
  question.value = text;
}
</script>

<style scoped>
.chat-view {
  height: calc(100vh - 60px);
  height: calc(100dvh - 60px);
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

.chat-sidebar-wrapper {
  flex-shrink: 0;
}

@media (max-width: 767.98px) {
  .chat-sidebar-wrapper {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 10;
    width: 100%;
    display: none;
  }

  .chat-sidebar-wrapper.chat-sidebar--visible {
    display: flex;
  }
}

.chat-mobile-header button {
  color: var(--om-neutral-700);
}

.chat-mobile-header button:hover {
  color: var(--om-primary);
}

.messages-area {
  background: var(--om-neutral-50);
}

.input-area {
  flex-shrink: 0;
}

.chat-input {
  resize: none;
  min-height: 72px;
  border-radius: var(--om-radius-base);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
