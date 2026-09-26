import http from './http'

export type SearchType =
  | 'members'
  | 'documents'
  | 'events'
  | 'announcements'
  | 'payments'
  | 'receipts'
  | 'audit'
  | 'discipline'

export interface SearchResult {
  id: string
  type: SearchType
  type_key: string
  title: string
  subtitle: string | null
  target_path: string
  score: number
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
}

export async function globalSearch(query: string, limit = 20): Promise<SearchResponse> {
  const response = await http.get<SearchResponse>('/search', { params: { q: query, limit } })
  return response.data
}
