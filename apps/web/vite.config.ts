import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    // Quick Tunnel pilots use random Cloudflare hostnames; do not allow arbitrary hosts.
    allowedHosts: ['.trycloudflare.com'],
    // Proxy API calls to the backend when running outside Docker
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        // Variables are imported per-component where needed
      },
    },
  },
})
