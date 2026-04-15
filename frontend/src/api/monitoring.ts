import apiClient from './client'

export interface WatchlistItem {
  id: number
  type: string
  value: string
  services: string[] | null
  schedule: string | null
  is_active: boolean
  last_checked: string | null
  created_at: string
  history?: WatchlistResult[]
}

export interface WatchlistResult {
  id: number
  has_findings: boolean
  result_data: Record<string, unknown> | null
  checked_at: string
}

export interface SearchTemplate {
  id: number
  name: string
  query: string
  filters: Record<string, unknown> | null
  schedule: string | null
  is_active: boolean
  created_at: string
}

export interface FolderStatus {
  monitored_dir: string
  exists: boolean
  tracked_files: number
  last_known_hashes: string[]
}

// Watchlist
export const monitoringApi = {
  // Watchlist
  listWatchlist: () => apiClient.get<WatchlistItem[]>('/monitoring/watchlist'),
  getWatchlistItem: (id: number) => apiClient.get<WatchlistItem>(`/monitoring/watchlist/${id}`),
  createWatchlistItem: (data: { type: string; value: string; services?: string[]; schedule?: string }) =>
    apiClient.post<WatchlistItem>('/monitoring/watchlist', data),
  updateWatchlistItem: (id: number, data: Partial<WatchlistItem>) =>
    apiClient.put<WatchlistItem>(`/monitoring/watchlist/${id}`, data),
  deleteWatchlistItem: (id: number) => apiClient.delete(`/monitoring/watchlist/${id}`),
  checkWatchlistItem: (id: number) => apiClient.post(`/monitoring/watchlist/${id}/check`),

  // Saved searches
  listSearchTemplates: () => apiClient.get<SearchTemplate[]>('/monitoring/searches'),
  createSearchTemplate: (data: { name: string; query: string; filters?: Record<string, unknown>; schedule?: string }) =>
    apiClient.post<SearchTemplate>('/monitoring/searches', data),
  updateSearchTemplate: (id: number, data: Partial<SearchTemplate>) =>
    apiClient.put<SearchTemplate>(`/monitoring/searches/${id}`, data),
  deleteSearchTemplate: (id: number) => apiClient.delete(`/monitoring/searches/${id}`),
  runSearchTemplate: (id: number) => apiClient.post(`/monitoring/searches/${id}/run`),

  // Folder monitoring
  getFolderStatus: () => apiClient.get<FolderStatus>('/monitoring/folder/status'),
  triggerFolderScan: () => apiClient.post('/monitoring/folder/scan'),

  // Jobs & history
  listJobs: () => apiClient.get('/monitoring/jobs'),
  getHistory: (limit?: number) => apiClient.get('/monitoring/history', { params: { limit } }),
}
