import apiClient from './client'

export interface LoginRequest { email: string; password: string }
export interface RegisterRequest { email: string; username: string; password: string }
export interface TokenResponse { access_token: string; refresh_token: string; token_type: string }
export interface UserResponse { id: number; email: string; username: string; language: string; is_admin: boolean; is_active: boolean; created_at: string }

export const authApi = {
  login: (data: LoginRequest) => apiClient.post<TokenResponse>('/auth/login', data),
  register: (data: RegisterRequest) => apiClient.post<TokenResponse>('/auth/register', data),
  me: () => apiClient.get<UserResponse>('/auth/me'),
  refresh: (refresh_token: string) => apiClient.post<TokenResponse>('/auth/refresh', { refresh_token }),
}
