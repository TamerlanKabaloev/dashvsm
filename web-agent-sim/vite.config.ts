import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        // Ignore specific warning from three-mesh-bvh
        if (warning.code === 'UNUSED_EXTERNAL_IMPORT' && warning.source?.includes('three-mesh-bvh')) return
        if (warning.message.includes('"BatchedMesh" is not exported')) return
        warn(warning)
      }
    }
  }
})
