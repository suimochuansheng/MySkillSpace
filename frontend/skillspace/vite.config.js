import vue from '@vitejs/plugin-vue'
import path from 'path'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@views': path.resolve(__dirname, 'src/views'),
      '@styles': path.resolve(__dirname, 'src/styles'),
      '@api': path.resolve(__dirname, 'src/api'),
    }
  },
  // 开发服务器配置
  server: {
    port: 5173, // 前端开发服务器端口
    open: true, // 自动打开浏览器
    proxy: {
      // HTTP API 代理
      '/api': {
        target: 'http://localhost:8000', // Django 后端地址
        changeOrigin: true,
        secure: false,
        // 可选：请求日志（调试用）
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('[Proxy] 请求:', req.method, req.url, '→', options.target + req.url);
          });
        }
      },
      // WebSocket 代理（用于 Django Channels）
      '/ws': {
        target: 'ws://localhost:8000', // WebSocket 后端地址
        ws: true, // 启用 WebSocket 代理
        changeOrigin: true,
        secure: false,
      },
      // 媒体文件代理（可选）
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // 静态文件代理（可选）
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

}
)
