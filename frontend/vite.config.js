import { sveltekit } from '@sveltejs/kit/vite';

export default {
  plugins: [sveltekit()],
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8080', ws: true, changeOrigin: true },
      '/media': { target: 'http://localhost:8080', changeOrigin: true }
    }
  }
};
