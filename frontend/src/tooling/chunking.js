const CHUNK_RULES = [
  {
    chunk: 'vendor-vue',
    patterns: ['/node_modules/vue/', '/node_modules/@vue/', '/node_modules/vue-router/']
  },
  {
    chunk: 'vendor-element-plus',
    patterns: ['/node_modules/element-plus/', '/node_modules/@element-plus/']
  },
  {
    chunk: 'vendor-echarts',
    patterns: ['/node_modules/echarts/', '/node_modules/zrender/']
  },
  {
    chunk: 'vendor-utils',
    patterns: ['/node_modules/axios/', '/node_modules/dompurify/']
  }
]

function normalizePath(id) {
  return id.replace(/\\/g, '/')
}

export function getManualChunkName(id) {
  const normalizedId = normalizePath(id)

  if (!normalizedId.includes('/node_modules/')) {
    return undefined
  }

  for (const rule of CHUNK_RULES) {
    if (rule.patterns.some((pattern) => normalizedId.includes(pattern))) {
      return rule.chunk
    }
  }

  return 'vendor-misc'
}

export function createManualChunks() {
  return (id) => getManualChunkName(id)
}
