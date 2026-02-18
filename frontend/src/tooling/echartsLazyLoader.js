const defaultImportRuntime = () =>
  import('./echartsRuntime.js').then((module) => module.echarts)

export function createEchartsLoader(importRuntime = defaultImportRuntime) {
  let runtimePromise = null

  return async () => {
    if (!runtimePromise) {
      runtimePromise = importRuntime().catch((error) => {
        runtimePromise = null
        throw error
      })
    }

    return runtimePromise
  }
}

export const ensureEcharts = createEchartsLoader()
