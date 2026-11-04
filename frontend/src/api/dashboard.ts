import { apiClient } from './client';
import type { DashboardStats } from '../types';

export async function apiGetDashboardStats(): Promise<DashboardStats> {
  const res = await apiClient.get<DashboardStats>('/api/dashboard/stats');
  return res.data;
}
