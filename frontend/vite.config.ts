import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import commonjs from 'vite-plugin-commonjs'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Загружаем env файлы на основе текущего режима
  const env = loadEnv(mode, process.cwd());
  
  return {
    plugins: [
      react(),
      commonjs()
    ],
    define: {
      'process.env': env
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    optimizeDeps: {
      include: ['@ant-design/graphs']
    },
    server: {
      port: 3003, // Обновляем порт, так как мы видели, что сервер запущен на 3003
      /* proxy: {  // <-- Комментируем начало блока proxy
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          // Возвращаем rewrite на место. Текущие запросы (без /api) он не тронет
          rewrite: (path) => path.replace(/^\/api/, ''), 
        },
      }, */ // <-- Комментируем конец блока proxy
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: true,
    }
  }
}) 