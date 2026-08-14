import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// The frontend talks to the FastAPI backend through the Vite dev proxy so it
// stays same-origin (no CORS / port-mismatch issues). The proxy target
// defaults to http://127.0.0.1:8000 but can be overridden at startup, e.g.:
//   $env:VITE_PROXY_TARGET='http://127.0.0.1:8001'; npm run dev
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const proxyTarget = env.VITE_PROXY_TARGET || 'http://127.0.0.1:8000';

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        // Forward API calls to the FastAPI backend so the frontend is
        // same-origin (no CORS / port-mismatch issues).
        '/analyze': proxyTarget,
        '/health': proxyTarget,
        '/projects': proxyTarget,
      },
    },
    build: {
      sourcemap: true,
    },
  };
});
