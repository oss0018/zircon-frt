import apiClient from './client'

export interface FileRecord {
  id: number
  filename: string
  file_type: string | null
  size_bytes: number | null
  project_id: number | null
  user_id: number
  indexed: boolean
  quarantined: boolean
  created_at: string
  updated_at: string
}

export interface FileListResponse {
  total: number
  items: FileRecord[]
}

export const filesApi = {
  upload: (file: File, projectId?: number) => {
    const formData = new FormData()
    formData.append('file', file)
    if (projectId) formData.append('project_id', String(projectId))
    return apiClient.post<FileRecord>('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: (page = 1, perPage = 20, projectId?: number) =>
    apiClient.get<FileListResponse>('/files/', { params: { page, per_page: perPage, project_id: projectId } }),
  get: (id: number) => apiClient.get<FileRecord>(`/files/${id}`),
  download: (id: number) => apiClient.get(`/files/${id}/download`, { responseType: 'blob' }),
  rename: (id: number, filename: string) => apiClient.patch<FileRecord>(`/files/${id}/rename`, { filename }),
  delete: (id: number) => apiClient.delete(`/files/${id}`),
}
