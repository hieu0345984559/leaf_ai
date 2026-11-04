import { apiClient } from './client';
import type { AuthResponse, User } from '../types';

export async function apiRegister(email: string, password: string, password_confirmation: string): Promise<AuthResponse> {
  const res = await apiClient.post<AuthResponse>('/api/auth/register', {
    email,
    password,
    password_confirmation,
  });
  return res.data;
}

export async function apiLogin(email: string, password: string): Promise<AuthResponse> {
  const res = await apiClient.post<AuthResponse>('/api/auth/login', {
    email,
    password,
  });
  return res.data;
}

export async function apiGetMe(): Promise<User> {
  const res = await apiClient.get<User>('/api/auth/me');
  return res.data;
}

export async function apiLogout(): Promise<void> {
  try {
    await apiClient.post('/api/auth/logout');
  } catch {
    // Ignore network error on logout
  }
}
