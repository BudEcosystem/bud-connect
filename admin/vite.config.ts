import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')
  
  // Determine the API target from environment or use default
  // For production URLs, we'll proxy them in development to avoid CORS
  const apiTarget = env.VITE_API_BASE_URL || 'http://localhost:9088'
  
  // Always use proxy in development mode to avoid CORS issues
  const shouldUseProxy = mode === 'development'
  
  // Use the actual target URL for proxying (even if it's production)
  const proxyTarget = apiTarget.includes('bud.studio') 
    ? apiTarget 
    : apiTarget
  
  console.log('Vite Config:', {
    mode,
    apiTarget,
    proxyTarget,
    shouldUseProxy,
    baseUrl: env.VITE_API_BASE_URL
  })

  return {
    base: process.env.VITE_BASE_PATH || '/',
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 3000,
      proxy: shouldUseProxy ? {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
          secure: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          followRedirects: true,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('proxy error', err);
            });
            proxy.on('proxyReq', (_proxyReq, req, _res) => {
              console.log('Sending Request to the Target:', req.method, req.url);
            });
            proxy.on('proxyRes', (proxyRes, req, _res) => {
              console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
            });
          },
        },
      } : undefined,
    },
    // Define environment variables that should be exposed to the client
    define: {
      __APP_ENV__: JSON.stringify(env.APP_ENV),
    }
  }
})
