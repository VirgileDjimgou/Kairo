import http from './http'

export type AttentionPriority = 'urgent' | 'attention' | 'normal' | 'informational'

export interface AttentionItem {
  id: string
  priority: AttentionPriority
  category: 'finance' | 'governance' | 'community' | 'account' | 'knowledge'
  title_key: string
  count: number
  target_path: string
}

export interface AttentionOverview {
  items: AttentionItem[]
}

export async function getAttentionOverview(): Promise<AttentionOverview> {
  const response = await http.get<AttentionOverview>('/attention')
  return response.data
}
