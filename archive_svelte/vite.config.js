import { sveltekit } from '@sveltejs/kit/vite';

/** @type {import('vite').UserConfig} */
const config = {
  plugins: [sveltekit()],
  server: {
    proxy: {
      // En dev, /api/* est redirigé vers l'API Backend (port 8000). Lancer ./start_api.sh pour que /studio fonctionne.
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
};

export default config;
