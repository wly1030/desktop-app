import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'

// https://vitejs.dev/config/
export default defineConfig({
  base: './',
  plugins: [
    vue(),
    electron([
      {
        // Main-Process entry file of the Electron App.
        entry: 'electron/main.js',
      },
      {
        entry: 'electron/preload.js',
        onstart(options) {
          options.reload()
        },
      },
    ]),
    renderer(),
  ],
})
