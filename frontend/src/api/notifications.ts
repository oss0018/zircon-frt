import apiClient from './client'

export interface Notification {
  id: number
  type: string
  title: string
  message: string | null
  is_read: boolean
  created_at: string
}

export interface NotificationPrefs {
  email_enabled: boolean
  email_address: string | null
  email_types: string[] | null
  telegram_enabled: boolean
  telegram_chat_id: string | null
  telegram_types: string[] | null
  digest_mode: string
}

export const notificationsApi = {
  list: (params?: { unread_only?: boolean; type_filter?: string; limit?: number; offset?: number }) =>
    apiClient.get<Notification[]>('/notifications/', { params }),
  unreadCount: () => apiClient.get<{ count: number }>('/notifications/unread'),
  markRead: (id: number) => apiClient.put(`/notifications/${id}/read`),
  markAllRead: () => apiClient.put('/notifications/read-all'),
  delete: (id: number) => apiClient.delete(`/notifications/${id}`),
  getSettings: () => apiClient.get<NotificationPrefs>('/notifications/settings'),
  updateSettings: (data: Partial<NotificationPrefs> & { telegram_bot_token?: string }) =>
    apiClient.put<NotificationPrefs>('/notifications/settings', data),
}
