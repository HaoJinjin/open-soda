import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// 添加路径别名@
import path from 'path'
// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
})
