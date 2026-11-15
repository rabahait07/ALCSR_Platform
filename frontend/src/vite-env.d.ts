/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the versioned API. Defaults to http://localhost:8000/api/v1. */
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
