import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// During development, /api requests are proxied to the FastAPI backend.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
