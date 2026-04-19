import { defineConfig } from 'vite'
import { resolve, join } from 'path'
import { readdirSync, cpSync, mkdirSync, copyFileSync, existsSync } from 'fs'

const frontendRoot = resolve(process.cwd(), 'src/frontend')
const distRoot = resolve(process.cwd(), 'dist')

// Collect all HTML files as multi-page app inputs (skip ARCHIVED and .bak files)
function collectHtmlInputs() {
  const inputs = {}
  for (const file of readdirSync(frontendRoot)) {
    if (file.endsWith('.html') && !file.startsWith('ARCHIVED') && !file.includes('.bak.')) {
      inputs[file.replace('.html', '')] = join(frontendRoot, file)
    }
  }
  return inputs
}

// Plugin: copy non-module static script/asset directories + GLB models after build
const copyStaticAssetsPlugin = {
  name: 'copy-static-assets',
  closeBundle() {
    const targets = [
      { src: join(frontendRoot, 'js'), dest: join(distRoot, 'js') },
      { src: join(frontendRoot, 'css'), dest: join(distRoot, 'css') },
      { src: join(frontendRoot, 'digital-twin'), dest: join(distRoot, 'digital-twin') },
    ]
    for (const { src, dest } of targets) {
      try {
        mkdirSync(dest, { recursive: true })
        cpSync(src, dest, { recursive: true, filter: (s) => !s.endsWith('.bak') })
      } catch { /* skip if source dir missing */ }
    }
    // Copy GLB 3D model files (required by digital-twin viewer)
    for (const file of readdirSync(frontendRoot)) {
      if (file.endsWith('.glb')) {
        const src = join(frontendRoot, file)
        const dest = join(distRoot, file)
        try { copyFileSync(src, dest) } catch { /* skip */ }
      }
    }
  }
}

export default defineConfig({
  root: 'src/frontend',
  plugins: [copyStaticAssetsPlugin],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/health': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true
      },
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://127.0.0.1:8080',
        ws: true,
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: resolve(process.cwd(), 'dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: collectHtmlInputs()
    }
  }
})