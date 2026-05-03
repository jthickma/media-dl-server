import { sveltekit } from '@sveltejs/vite-plugin-svelte';

export default {
  plugins: [sveltekit()],
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8080', ws: true, changeOrigin: true },
      '/media': { target: 'http://localhost:8080', changeOrigin: true }
    }
  }
};
