import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
    server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000", // Adresse de ton backend Django
        changeOrigin: true,
        secure: false, // Désactive SSL (si applicable)
        rewrite: (path) => path.replace(/^\/api/, "/api"),
      },
      "/chat": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/chat/, "/chat"),
      },
    },
  },
})
