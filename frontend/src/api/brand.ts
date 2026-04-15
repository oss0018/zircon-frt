import apiClient from './client'

export interface BrandWatch {
  id: number
  name: string
  original_url: string
  keywords: string[] | null
  description: string | null
  similarity_threshold: number
  scan_schedule: string | null
  last_scan: string | null
  is_active: boolean
  alert_count: number
  new_alert_count: number
  created_at: string
}

export interface BrandAlert {
  id: number
  brand_watch_id: number
  found_domain: string
  similarity_score: number
  detection_sources: string[] | null
  screenshot_url: string | null
  status: 'new' | 'reviewed' | 'dismissed'
  notes: string | null
  created_at: string
}

export interface BrandReport {
  brand_watch: BrandWatch
  alerts: BrandAlert[]
  generated_at: string
  summary: {
    total_alerts: number
    new: number
    reviewed: number
    dismissed: number
    avg_similarity: number
  }
}

export const brandApi = {
  listWatches: () => apiClient.get<BrandWatch[]>('/brand/watches'),
  getWatch: (id: number) => apiClient.get<BrandWatch>(`/brand/watches/${id}`),
  createWatch: (data: {
    name: string
    original_url: string
    keywords?: string[]
    description?: string
    similarity_threshold?: number
    scan_schedule?: string
  }) => apiClient.post<BrandWatch>('/brand/watches', data),
  updateWatch: (id: number, data: Partial<BrandWatch>) =>
    apiClient.put<BrandWatch>(`/brand/watches/${id}`, data),
  deleteWatch: (id: number) => apiClient.delete(`/brand/watches/${id}`),
  triggerScan: (id: number) => apiClient.post(`/brand/watches/${id}/scan`),
  listAlerts: (watchId: number) => apiClient.get<BrandAlert[]>(`/brand/watches/${watchId}/alerts`),
  updateAlertStatus: (alertId: number, status: string, notes?: string) =>
    apiClient.put<BrandAlert>(`/brand/alerts/${alertId}/status`, { status, notes }),
  getReport: (watchId: number) => apiClient.get<BrandReport>(`/brand/report/${watchId}`),
}
