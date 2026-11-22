import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Local development only: browser uses Vite on 5173; /api goes to Django on 8000.
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: false },
      '/media': { target: 'http://127.0.0.1:8000', changeOrigin: false },
    },
  },
})
