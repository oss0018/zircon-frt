import apiClient from './client'

export interface SearchFilters {
  file_type?: string
  project_id?: number
  date_from?: string
  date_to?: string
}

export interface SearchRequest {
  query: string
  filters?: SearchFilters
  page?: number
  per_page?: number
}

export interface SearchHit {
  file_id: number
  filename: string
  file_type: string | null
  score: number
  highlights: string[]
  created_at: string | null
}

export interface SearchResponse {
  total: number
  page: number
  per_page: number
  hits: SearchHit[]
  took_ms: number
}

export const searchApi = {
  search: (data: SearchRequest) => apiClient.post<SearchResponse>('/search/', data),
}
