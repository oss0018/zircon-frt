import apiClient from './client'

export interface ServiceCatalogueEntry {
  name: string
  display_name: string
  description: string
  category: string
  website: string
  query_types: string[]
  rate_limit: number
  docs_url: string
  is_configured: boolean
  is_active: boolean
}

export interface IntegrationResponse {
  id: number
  service_name: string
  is_active: boolean
  rate_limit_remaining: number | null
  last_check: string | null
  created_at?: string
  updated_at?: string | null
}

export interface UnifiedSearchResult {
  service: string
  display_name: string
  results: Record<string, unknown>[]
  error: string | null
  cached: boolean
  duration_ms: number
}

export interface UnifiedSearchResponse {
  query: string
  query_type: string
  results: UnifiedSearchResult[]
  total_services: number
  successful_services: number
}

export interface UsageStatsEntry {
  service: string
  today: number
  this_week: number
  this_month: number
  total: number
}

export interface TestConnectionResponse {
  service: string
  status: string
  message: string
  details?: Record<string, unknown> | null
}

export const integrationsApi = {
  listAvailable: (): Promise<ServiceCatalogueEntry[]> =>
    apiClient.get('/integrations/available').then((r) => r.data),

  list: (): Promise<IntegrationResponse[]> =>
    apiClient.get('/integrations/').then((r) => r.data),

  create: (service_name: string, api_key: string): Promise<IntegrationResponse> =>
    apiClient.post('/integrations/', { service_name, api_key }).then((r) => r.data),

  update: (id: number, data: { api_key?: string; is_active?: boolean }): Promise<IntegrationResponse> =>
    apiClient.put(`/integrations/${id}`, data).then((r) => r.data),

  delete: (id: number): Promise<void> =>
    apiClient.delete(`/integrations/${id}`).then((r) => r.data),

  test: (id: number): Promise<TestConnectionResponse> =>
    apiClient.post(`/integrations/${id}/test`).then((r) => r.data),

  search: (payload: {
    query: string
    query_type: string
    services?: string[]
    use_cache?: boolean
  }): Promise<UnifiedSearchResponse> =>
    apiClient.post('/integrations/search', payload).then((r) => r.data),

  getUsage: (): Promise<UsageStatsEntry[]> =>
    apiClient.get('/integrations/usage').then((r) => r.data),

  getServiceUsage: (service: string): Promise<UsageStatsEntry> =>
    apiClient.get(`/integrations/usage/${service}`).then((r) => r.data),
}
