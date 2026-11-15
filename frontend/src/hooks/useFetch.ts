import { useCallback, useEffect, useState } from 'react'

import { api, getErrorMessage } from '../services/api'

export interface FetchState<T> {
  data: T | null
  /** A message ready to show to the user, or null if the request has not failed. */
  error: string | null
  isLoading: boolean
  /** Run the request again, for example from a "Try again" button. */
  reload: () => void
}

interface FetchResult<T> {
  requestKey: string
  data: T | null
  error: string | null
}

/**
 * GET `path` from the API and track its loading, data and error state.
 * The request is repeated when `path` changes and cancelled when the component unmounts.
 */
export function useFetch<T>(path: string): FetchState<T> {
  const [attempt, setAttempt] = useState(0)
  const [result, setResult] = useState<FetchResult<T> | null>(null)
  const requestKey = `${attempt}:${path}`

  useEffect(() => {
    const controller = new AbortController()
    api
      .get<T>(path, { signal: controller.signal })
      .then(({ data }) => setResult({ requestKey, data, error: null }))
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setResult({ requestKey, data: null, error: getErrorMessage(error) })
        }
      })
    return () => controller.abort()
  }, [path, requestKey])

  const reload = useCallback(() => setAttempt((current) => current + 1), [])

  // A result from an earlier path or attempt is stale, so the request counts as loading.
  const current = result?.requestKey === requestKey ? result : null
  return {
    data: current?.data ?? null,
    error: current?.error ?? null,
    isLoading: current === null,
    reload,
  }
}
