import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    // Only use proxy in development mode
    ...(mode === 'development' ? {
      proxy: {
        // Proxy API requests to FastAPI during development
        // In Docker: Use service name 'api', outside Docker: use localhost
        '/api': {
          target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true,
        },
      }
    } : {})
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
}))
