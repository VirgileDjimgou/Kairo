import http from "./http";

export interface ChatQueryRequest {
  question: string;
  top_k?: number;
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
  citations: ChatCitationResponse[];
  source_types: string[];
  confidence: number;
  refused: boolean;
  refusal_reason: string | null;
}

export async function queryChat(payload: ChatQueryRequest): Promise<ChatQueryResponse> {
  const response = await http.post<ChatQueryResponse>("/chat/query", payload);
  return response.data;
}
