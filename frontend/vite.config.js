import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'logo-oficial.png', 'texto_logo.png'],
      manifest: {
        name: 'Dra. Gisele Santos — Estética e Saúde',
        short_name: 'Dra. Gisele',
        description: 'Sistema de Gestão — Clínica de Estética e Saúde',
        theme_color: '#C6A77D',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait-primary',
        icons: [
          {
            src: '/logo-oficial.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      },
      workbox: {
        cleanupOutdatedCaches: true,
        skipWaiting: true,
        clientsClaim: true,
      }
    })
  ],
})
