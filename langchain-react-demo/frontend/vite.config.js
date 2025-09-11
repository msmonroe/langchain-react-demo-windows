import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev proxy to backend; respects VITE_API_BASE if provided.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/ask': process.env.VITE_API_BASE || 'http://127.0.0.1:8000' }
  }
})
