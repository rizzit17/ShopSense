import type { DatasetOverview, SegmentProfile, EvaluationResponse, VisualizationResponse, PredictRequest, PredictResponse } from '../types/api';

export const API_BASE = import.meta.env.VITE_API_BASE || '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { ...init, signal: AbortSignal.timeout(15000) });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    const message = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map((e: { msg: string }) => e.msg).join('; ') : `API request failed (${response.status})`;
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export const fetchOverview = () => request<DatasetOverview>('/overview');
export const fetchSegments = () => request<SegmentProfile[]>('/segments');
export const fetchEvaluation = () => request<EvaluationResponse>('/evaluation');
export const fetchVisualization = (sampleLimit = 5000) => request<VisualizationResponse>(`/visualization?sample_limit=${sampleLimit}`);
export const predictPersonality = (data: PredictRequest) => request<PredictResponse>('/predict', {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data),
});
