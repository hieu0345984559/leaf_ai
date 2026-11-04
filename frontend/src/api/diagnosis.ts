import { apiClient } from './client';
import type { DiagnosisResult, DiagnosisListItem } from '../types';

export async function apiPredict(file: File): Promise<DiagnosisResult> {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await apiClient.post<DiagnosisResult>('/api/predict', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return res.data;
}

export async function apiGetHistory(status?: string, search?: string): Promise<DiagnosisListItem[]> {
  const params: Record<string, string> = {};
  if (status && status !== 'all') params.status = status;
  if (search && search.trim()) params.search = search.trim();
  
  const res = await apiClient.get<DiagnosisListItem[]>('/api/history', { params });
  return res.data;
}

export async function apiGetHistoryDetail(id: number): Promise<DiagnosisResult> {
  const res = await apiClient.get<DiagnosisResult>(`/api/history/${id}`);
  return res.data;
}

export async function apiDeleteHistory(id: number): Promise<{ message: string; id: number }> {
  const res = await apiClient.delete<{ message: string; id: number }>(`/api/history/${id}`);
  return res.data;
}
