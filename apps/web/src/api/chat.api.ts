import http from "./http";

export interface ChatQueryRequest {
  question: string;
  conversation_id?: string | null;
  top_k?: number;
  response_language?: string;
}

export interface ChatCitationResponse {
  chunk_id: string;
  document_id: string;
  document_version_id: string;
  document_title: string;
  excerpt: string;
  score: number;
}

export interface ChatQueryResponse {
  answer: string;
  conversation_id?: string | null;
  citations: ChatCitationResponse[];
  source_types: string[];
  confidence: number;
  refused: boolean;
  refusal_reason: string | null;
}

export interface ChatConversationResponse {
  id: string;
  tenant_id: string;
  user_id: string;
  title: string;
  message_count: number;
  last_message_preview: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessageResponse {
  id: string;
  role: string;
  content: string;
  citations_json: ChatCitationResponse[];
  created_at: string;
}

export interface ChatConversationDetailResponse {
  id: string;
  tenant_id: string;
  user_id: string;
  title: string;
  messages: ChatMessageResponse[];
  created_at: string;
  updated_at: string;
}

export async function queryChat(payload: ChatQueryRequest): Promise<ChatQueryResponse> {
  const response = await http.post<ChatQueryResponse>("/chat/query", payload);
  return response.data;
}

export async function queryChatStream(
  payload: ChatQueryRequest,
  onToken: (token: string) => void,
  onDone: (conversationId: string, confidence: number, citations: ChatCitationResponse[], sourceTypes: string[]) => void,
  onError: (error: string) => void,
  signal?: AbortSignal,
  fallbackError = "Chat error",
): Promise<void> {
  try {
    const token = localStorage.getItem("access_token");
    const baseUrl = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");
    const response = await fetch(`${baseUrl}/chat/query-stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
      signal,
    });

    if (!response.ok) {
      onError(fallbackError);
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      onError(fallbackError);
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        try {
          const data = JSON.parse(line.slice(6));
          switch (data.type) {
            case "token":
              onToken(data.content);
              break;
            case "done":
              onDone(
                data.conversation_id,
                data.confidence,
                Array.isArray(data.citations) ? data.citations : [],
                Array.isArray(data.source_types) ? data.source_types : [],
              );
              break;
            case "error":
              onError(data.content || fallbackError);
              return;
          }
        } catch {
          // skip malformed JSON
        }
      }
    }
  } catch {
    onError(fallbackError);
  }
}

// --- Conversation CRUD ---

export async function listConversations(): Promise<ChatConversationResponse[]> {
  const response = await http.get<ChatConversationResponse[]>("/chat/conversations");
  return response.data;
}

export async function createConversation(title = "New conversation"): Promise<ChatConversationResponse> {
  const response = await http.post<ChatConversationResponse>("/chat/conversations", { title });
  return response.data;
}

export async function getConversation(id: string): Promise<ChatConversationDetailResponse> {
  const response = await http.get<ChatConversationDetailResponse>(`/chat/conversations/${id}`);
  return response.data;
}

export async function updateConversationTitle(id: string, title: string): Promise<ChatConversationResponse> {
  const response = await http.patch<ChatConversationResponse>(`/chat/conversations/${id}`, { title });
  return response.data;
}

export async function deleteConversation(id: string): Promise<void> {
  await http.delete(`/chat/conversations/${id}`);
}
