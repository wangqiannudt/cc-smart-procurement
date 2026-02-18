import { describe, expect, it } from 'vitest'

import { createManualChunks, getManualChunkName } from '../chunking'

describe('chunking strategy', () => {
  it('creates dedicated chunk for vue ecosystem', () => {
    expect(
      getManualChunkName('/app/node_modules/vue/dist/vue.runtime.esm-bundler.js')
    ).toBe('vendor-vue')
    expect(
      getManualChunkName('/app/node_modules/vue-router/dist/vue-router.mjs')
    ).toBe('vendor-vue')
  })

  it('creates dedicated chunk for element-plus dependencies', () => {
    expect(
      getManualChunkName('/app/node_modules/element-plus/es/components/button/index.mjs')
    ).toBe('vendor-element-plus')
    expect(
      getManualChunkName('/app/node_modules/@element-plus/icons-vue/dist/index.js')
    ).toBe('vendor-element-plus')
  })

  it('creates dedicated chunk for echarts runtime', () => {
    expect(getManualChunkName('/app/node_modules/echarts/core.js')).toBe('vendor-echarts')
    expect(getManualChunkName('/app/node_modules/zrender/lib/core/env.js')).toBe('vendor-echarts')
  })

  it('creates utility chunk for request and sanitize libraries', () => {
    expect(getManualChunkName('/app/node_modules/axios/index.js')).toBe('vendor-utils')
    expect(getManualChunkName('/app/node_modules/dompurify/dist/purify.es.mjs')).toBe('vendor-utils')
  })

  it('puts uncategorized third-party dependencies into misc vendor chunk', () => {
    expect(getManualChunkName('/app/node_modules/dayjs/dayjs.min.js')).toBe('vendor-misc')
  })

  it('returns undefined for application source modules', () => {
    expect(getManualChunkName('/app/src/views/Home.vue')).toBeUndefined()
  })

  it('supports windows path separators', () => {
    expect(getManualChunkName('C:\\repo\\node_modules\\axios\\index.js')).toBe('vendor-utils')
  })

  it('createManualChunks delegates to getManualChunkName', () => {
    const manualChunks = createManualChunks()
    expect(manualChunks('/app/node_modules/vue/dist/vue.runtime.esm-bundler.js')).toBe('vendor-vue')
    expect(manualChunks('/app/src/main.js')).toBeUndefined()
  })
})
