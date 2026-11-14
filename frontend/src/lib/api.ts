import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 10_000,
  headers: { Accept: 'application/json' },
})

interface HealthResponse {
  status: string
}

export async function fetchHealth(signal?: AbortSignal): Promise<boolean> {
  const { data } = await api.get<HealthResponse>('/api/health', { signal })
  return data.status === 'ok'
}
