import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  // Vue Material and the other Vue 2 plugins still require compat templates.
  plugins: [vue({
    template: {
      compilerOptions: {
        compatConfig: { MODE: 2 },
      },
    },
  })],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      vue: '@vue/compat',
    },
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue'],
  },
  server: {
    port: 8080,
    proxy: {
      '/days': 'http://localhost:3000',
      '/attendees': 'http://localhost:3000',
      '/login': 'http://localhost:3000',
      '/logout': 'http://localhost:3000',
      '/user': 'http://localhost:3000',
      '/users': 'http://localhost:3000',
      '/groups': 'http://localhost:3000',
      '/settings': 'http://localhost:3000',
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
});
