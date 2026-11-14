import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // The backend CORS allow-list only includes port 5173, so never fall back to another port.
    port: 5173,
    strictPort: true,
  },
})
