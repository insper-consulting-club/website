import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import siteConfig from './plugins/siteConfig'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')

  return {
    plugins: [react(), siteConfig(env.VITE_API_URL)],
    server: {
      watch: {
        usePolling: true,
        interval: 500,
      },
    },
  }
})
