<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

const loading = ref(false)
const predictionLoading = ref(false)
const chartRef = ref(null)
const predictionChartRef = ref(null)
const chartInstance = ref(null)
const predictionChartInstance = ref(null)

const searchForm = reactive({
  category: '',
  keyword: '',
  minPrice: null,
  maxPrice: null
})

const categories = ref([])
const priceData = ref({
  records: [],
  total: 0,
  trendData: [],
  priceRange: { min: 0, max: 0, avg: 0 }
})

// 价格预测数据
const predictionData = ref(null)
const predictionKeyword = ref('')
const predictionMonths = ref(3)

// 市场洞察数据
const marketInsights = ref(null)

const handleSearch = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/price-reference', {
      params: {
        category: searchForm.category || undefined,
        keyword: searchForm.keyword || undefined,
        min_price: searchForm.minPrice || undefined,
        max_price: searchForm.maxPrice || undefined
      }
    })

    if (response.data.success) {
      const apiData = response.data.data
      priceData.value = {
        records: apiData.records || [],
        total: apiData.total || 0,
        trendData: apiData.trend_data || [],
        priceRange: apiData.price_range || { min: 0, max: 0, avg: 0 }
      }
      categories.value = apiData.categories || []

      if (chartRef.value && priceData.value.trendData.length > 0) {
        nextTick(() => {
          initChart()
        })
      }
    }
  } catch (error) {
    ElMessage.error('查询失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  searchForm.category = ''
  searchForm.keyword = ''
  searchForm.minPrice = null
  searchForm.maxPrice = null
  priceData.value = {
    records: [],
    total: 0,
    trendData: [],
    priceRange: { min: 0, max: 0, avg: 0 }
  }
  loadCategories()
}

const loadCategories = async () => {
  try {
    const response = await axios.get('/api/price-reference/categories')
    if (response.data.success) {
      categories.value = response.data.data
    }
  } catch (error) {
    ElMessage.error('加载分类失败: ' + error.message)
  }
}

// 价格预测
const handlePredict = async () => {
  if (!predictionKeyword.value.trim()) {
    ElMessage.warning('请输入产品关键词')
    return
  }

  predictionLoading.value = true
  try {
    const response = await axios.get('/api/price-reference/predict', {
      params: {
        keyword: predictionKeyword.value,
        months: predictionMonths.value
      }
    })

    if (response.data.success && response.data.data.success) {
      predictionData.value = response.data.data

      nextTick(() => {
        initPredictionChart()
      })
    } else {
      ElMessage.warning(response.data.data?.message || '无法生成预测')
    }
  } catch (error) {
    ElMessage.error('预测失败: ' + error.message)
  } finally {
    predictionLoading.value = false
  }
}

// 加载市场洞察
const loadMarketInsights = async () => {
  try {
    const response = await axios.get('/api/price-reference/market-insights')
    if (response.data.success) {
      marketInsights.value = response.data.data
    }
  } catch (error) {
    console.error('加载市场洞察失败:', error)
  }
}

const initChart = () => {
  if (!chartRef.value) return

  if (chartInstance.value) {
    chartInstance.value.dispose()
  }

  chartInstance.value = echarts.init(chartRef.value)

  const trendData = priceData.value.trendData
  const dates = trendData.map(d => d.date)

  const allCategories = new Set()
  trendData.forEach(d => {
    Object.keys(d).forEach(key => {
      if (key !== 'date') {
        allCategories.add(key)
      }
    })
  })

  const series = Array.from(allCategories).map(category => ({
    name: category,
    type: 'line',
    smooth: true,
    data: trendData.map(d => d[category] || null),
    emphasis: { focus: 'series' }
  }))

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#409EFF',
      textStyle: { color: '#ffffff' }
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#ffffff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.3)' } },
      axisLabel: { color: 'rgba(255, 255, 255, 0.7)' }
    },
    yAxis: {
      type: 'value',
      name: '价格 (元)',
      nameTextStyle: { color: 'rgba(255, 255, 255, 0.7)' },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.3)' } },
      axisLabel: { color: 'rgba(255, 255, 255, 0.7)' },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
    },
    series: series,
    color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  }

  chartInstance.value.setOption(option)
}

// 初始化预测图表
const initPredictionChart = () => {
  if (!predictionChartRef.value || !predictionData.value) return

  if (predictionChartInstance.value) {
    predictionChartInstance.value.dispose()
  }

  predictionChartInstance.value = echarts.init(predictionChartRef.value)

  const predictions = predictionData.value.predictions
  if (!predictions || predictions.length === 0) return

  // 取第一个产品的预测数据
  const firstProduct = predictions[0]
  const predData = firstProduct.predictions

  const dates = predData.map(p => p.date)
  const predictedPrices = predData.map(p => p.predicted_price)
  const lowerBounds = predData.map(p => p.lower_bound)
  const upperBounds = predData.map(p => p.upper_bound)

  // 添加当前价格点
  dates.unshift('当前')
  predictedPrices.unshift(firstProduct.current_price)
  lowerBounds.unshift(firstProduct.current_price)
  upperBounds.unshift(firstProduct.current_price)

  const option = {
    backgroundColor: 'transparent',
    title: {
      text: `${firstProduct.product_name} 价格预测`,
      left: 'center',
      textStyle: { color: '#ffffff', fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#409EFF',
      textStyle: { color: '#ffffff' },
      formatter: function(params) {
        let result = params[0].axisValue + '<br/>'
        params.forEach(p => {
          result += p.marker + p.seriesName + ': ¥' + p.value?.toLocaleString() + '<br/>'
        })
        return result
      }
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#ffffff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '18%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.3)' } },
      axisLabel: { color: 'rgba(255, 255, 255, 0.7)' }
    },
    yAxis: {
      type: 'value',
      name: '价格 (元)',
      nameTextStyle: { color: 'rgba(255, 255, 255, 0.7)' },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.3)' } },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        formatter: val => (val / 10000).toFixed(0) + '万'
      },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
    },
    series: [
      {
        name: '预测价格',
        type: 'line',
        data: predictedPrices,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        itemStyle: { color: '#409EFF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      },
      {
        name: '置信区间上限',
        type: 'line',
        data: upperBounds,
        lineStyle: { color: '#67C23A', type: 'dashed' },
        itemStyle: { color: '#67C23A' },
        symbol: 'none'
      },
      {
        name: '置信区间下限',
        type: 'line',
        data: lowerBounds,
        lineStyle: { color: '#F56C6C', type: 'dashed' },
        itemStyle: { color: '#F56C6C' },
        symbol: 'none',
        areaStyle: {
          color: 'rgba(255, 255, 255, 0.05)',
          origin: 'auto'
        }
      }
    ]
  }

  predictionChartInstance.value.setOption(option)
}

// 获取趋势颜色
const getTrendColor = (direction) => {
  const colors = {
    '上升': '#F56C6C',
    '下降': '#67C23A',
    '稳定': '#409EFF'
  }
  return colors[direction] || '#909399'
}

// 获取建议颜色
const getAdviceColor = (recommendation) => {
  if (recommendation?.includes('尽快')) return '#F56C6C'
  if (recommendation?.includes('延后')) return '#67C23A'
  return '#409EFF'
}

const formatPrice = (price) => {
  return '¥' + price?.toLocaleString('zh-CN') || '0'
}

const getCategoryColor = (category) => {
  const colors = {
    '服务器': '#409EFF',
    '工作站': '#67C23A',
    '终端': '#E6A23C',
    '无人平台': '#F56C6C',
    '通信': '#909399',
    '显示': '#8e44ad',
    '仪器仪表': '#16a085'
  }
  return colors[category] || '#607D8B'
}

onMounted(() => {
  loadCategories()
  loadMarketInsights()

  window.addEventListener('resize', () => {
    if (chartInstance.value) chartInstance.value.resize()
    if (predictionChartInstance.value) predictionChartInstance.value.resize()
  })
})
</script>

<template>
  <div class="price-container">
    <div class="page-header">
      <h1>价格参考与审价</h1>
      <p>查询历史价格数据，分析价格趋势，智能预测未来走势</p>
    </div>

    <!-- 搜索表单 -->
    <div class="card search-card">
      <div class="card-header">
        <h3>搜索筛选</h3>
        <el-icon><Search /></el-icon>
      </div>
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="商品分类">
          <el-select v-model="searchForm.category" placeholder="请选择分类" clearable style="width: 180px">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="产品名称或规格" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="价格范围">
          <el-input-number v-model="searchForm.minPrice" :min="0" :step="10000" controls-position="right" style="width: 130px" />
          <span class="price-separator">-</span>
          <el-input-number v-model="searchForm.maxPrice" :min="0" :step="10000" controls-position="right" style="width: 130px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshRight /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 价格预测模块 -->
    <div class="card prediction-card">
      <div class="card-header">
        <h3>智能价格预测</h3>
        <el-icon><TrendCharts /></el-icon>
      </div>

      <div class="prediction-form">
        <el-input v-model="predictionKeyword" placeholder="输入产品关键词（如：服务器、工作站）" style="width: 300px" />
        <el-select v-model="predictionMonths" style="width: 120px">
          <el-option :value="1" label="1个月" />
          <el-option :value="3" label="3个月" />
          <el-option :value="6" label="6个月" />
        </el-select>
        <el-button type="primary" @click="handlePredict" :loading="predictionLoading">
          <el-icon><Aim /></el-icon> 开始预测
        </el-button>
      </div>

      <!-- 预测结果 -->
      <div v-if="predictionData" class="prediction-results">
        <!-- 购买建议 -->
        <div class="advice-banner" :style="{ borderColor: getAdviceColor(predictionData.buying_advice?.recommendation) }">
          <div class="advice-icon">
            <el-icon :size="32">
              <component :is="predictionData.buying_advice?.recommendation?.includes('尽快') ? 'Warning' : predictionData.buying_advice?.recommendation?.includes('延后') ? 'Timer' : 'Check'" />
            </el-icon>
          </div>
          <div class="advice-content">
            <div class="advice-title">{{ predictionData.buying_advice?.recommendation }}</div>
            <div class="advice-reason">{{ predictionData.buying_advice?.reason }}</div>
          </div>
          <div class="advice-urgency" :class="predictionData.buying_advice?.urgency?.toLowerCase()">
            {{ predictionData.buying_advice?.urgency }}紧迫度
          </div>
        </div>

        <div class="prediction-grid">
          <!-- 预测图表 -->
          <div class="prediction-chart-wrapper">
            <div ref="predictionChartRef" class="prediction-chart"></div>
          </div>

          <!-- 产品预测列表 -->
          <div class="prediction-list">
            <h4>分析产品 ({{ predictionData.products_analyzed }}个)</h4>
            <div class="product-predictions">
              <div v-for="pred in predictionData.predictions" :key="pred.product_name" class="product-prediction-item">
                <div class="pred-header">
                  <span class="pred-name">{{ pred.product_name }}</span>
                  <el-tag :color="getTrendColor(pred.trend_direction) + '33'" size="small">
                    {{ pred.trend_direction }}
                  </el-tag>
                </div>
                <div class="pred-details">
                  <div class="pred-current">当前: {{ formatPrice(pred.current_price) }}</div>
                  <div class="pred-slope">趋势斜率: {{ pred.trend_slope > 0 ? '+' : '' }}{{ pred.trend_slope.toFixed(2) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 整体趋势 -->
        <div class="overall-trend">
          <span class="trend-label">整体趋势:</span>
          <el-tag :type="predictionData.overall_trend?.direction === '下降' ? 'success' : predictionData.overall_trend?.direction === '上升' ? 'danger' : 'info'">
            {{ predictionData.overall_trend?.direction }}
          </el-tag>
          <span class="trend-confidence">置信度: {{ predictionData.overall_trend?.confidence }}%</span>
        </div>
      </div>

      <div v-else class="prediction-empty">
        <el-icon :size="48"><TrendCharts /></el-icon>
        <p>输入关键词开始智能价格预测</p>
      </div>
    </div>

    <div class="content-grid">
      <!-- 价格列表 -->
      <div class="card table-card">
        <div class="card-header">
          <h3>价格列表</h3>
          <span class="header-stats">共 {{ priceData.total }} 条记录</span>
        </div>
        <el-table :data="priceData.records" v-loading="loading" stripe height="350">
          <el-table-column prop="name" label="产品名称" min-width="180">
            <template #default="{ row }">
              <div class="product-name">{{ row.name }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="category" label="分类" width="100">
            <template #default="{ row }">
              <el-tag :color="getCategoryColor(row.category) + '33'">{{ row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="specs" label="规格参数" min-width="200" show-overflow-tooltip />
          <el-table-column prop="price" label="价格" width="120" align="right">
            <template #default="{ row }">
              <span class="price-value">{{ formatPrice(row.price) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="date" label="更新时间" width="100" />
        </el-table>
      </div>

      <!-- 价格趋势图 -->
      <div class="card chart-card">
        <div class="card-header">
          <h3>历史价格趋势</h3>
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div ref="chartRef" class="chart-container"></div>
        <div class="chart-empty" v-if="priceData.trendData.length === 0">
          <el-icon :size="48"><TrendCharts /></el-icon>
          <p>执行搜索后显示趋势图</p>
        </div>
      </div>
    </div>

    <!-- 价格统计 -->
    <div class="card stats-card">
      <div class="card-header">
        <h3>价格统计</h3>
        <el-icon><DataBoard /></el-icon>
      </div>
      <div class="stats-grid">
        <div class="stat-box">
          <div class="stat-label">最低价</div>
          <div class="stat-value min">{{ formatPrice(priceData.priceRange.min) }}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">最高价</div>
          <div class="stat-value max">{{ formatPrice(priceData.priceRange.max) }}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">平均价</div>
          <div class="stat-value avg">{{ formatPrice(priceData.priceRange.avg) }}</div>
        </div>
      </div>
    </div>

    <!-- 市场洞察 -->
    <div v-if="marketInsights?.insights?.length" class="card insights-card">
      <div class="card-header">
        <h3>市场洞察</h3>
        <el-icon><Opportunity /></el-icon>
      </div>
      <div class="insights-grid">
        <div v-for="insight in marketInsights.insights" :key="insight.category" class="insight-item">
          <div class="insight-category">
            <el-tag :color="getCategoryColor(insight.category) + '33'">{{ insight.category }}</el-tag>
          </div>
          <div class="insight-text">{{ insight.insight }}</div>
          <div class="insight-meta">
            <span>{{ insight.product_count }}个产品</span>
            <span>均价: {{ formatPrice(insight.avg_price) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.price-container { animation: fadeIn 0.5s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

.page-header { margin-bottom: 25px; }
.page-header h1 { color: var(--text-primary); font-size: 28px; margin: 0 0 8px 0; font-weight: 600; }
.page-header p { color: var(--text-secondary); font-size: 14px; margin: 0; }

.card { background: var(--bg-card); border-radius: 16px; padding: 20px; border: 1px solid var(--border-color); margin-bottom: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }
.card-header h3 { color: var(--text-primary); font-size: 16px; margin: 0; font-weight: 600; }
.card-header .el-icon { color: #409EFF; font-size: 22px; }
.header-stats { color: var(--text-muted); font-size: 13px; }

/* Search Form */
.search-form { display: flex; flex-wrap: wrap; gap: 12px; }
.search-form :deep(.el-form-item) { margin-bottom: 0; }
.search-form :deep(.el-form-item__label) { color: var(--text-secondary); }
.price-separator { color: var(--text-muted); margin: 0 8px; }

/* Prediction Card */
.prediction-form { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.prediction-results { animation: fadeIn 0.3s ease; }

.advice-banner { display: flex; align-items: center; gap: 16px; padding: 16px 20px; background: var(--bg-card); border-radius: 12px; border-left: 4px solid #409EFF; margin-bottom: 20px; }
.advice-icon { color: #409EFF; }
.advice-content { flex: 1; }
.advice-title { color: var(--text-primary); font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.advice-reason { color: var(--text-secondary); font-size: 13px; }
.advice-urgency { padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.advice-urgency.高 { background: rgba(245, 108, 108, 0.2); color: #F56C6C; }
.advice-urgency.中 { background: rgba(230, 162, 60, 0.2); color: #E6A23C; }
.advice-urgency.低 { background: rgba(103, 194, 58, 0.2); color: #67C23A; }

.prediction-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 20px; margin-bottom: 16px; }
.prediction-chart-wrapper { background: rgba(0, 0, 0, 0.2); border-radius: 12px; padding: 15px; }
.prediction-chart { height: 280px; width: 100%; }

.prediction-list h4 { color: var(--text-primary); font-size: 14px; margin: 0 0 12px 0; }
.product-predictions { max-height: 260px; overflow-y: auto; }
.product-prediction-item { padding: 12px; background: var(--bg-card); border-radius: 8px; margin-bottom: 8px; transition: all 0.2s; }
.product-prediction-item:hover { background: var(--bg-card-hover); }
.pred-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.pred-name { color: var(--text-primary); font-size: 13px; font-weight: 500; }
.pred-details { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary); }
.pred-current { color: #67C23A; }

.overall-trend { display: flex; align-items: center; gap: 10px; padding: 12px 16px; background: var(--bg-card); border-radius: 8px; }
.trend-label { color: var(--text-secondary); font-size: 13px; }
.trend-confidence { color: var(--text-muted); font-size: 12px; margin-left: auto; }

.prediction-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; color: var(--text-muted); }
.prediction-empty .el-icon { margin-bottom: 12px; }

/* Content Grid */
.content-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 20px; }

/* Table */
.product-name { color: var(--text-primary); font-weight: 500; }
.price-value { color: #67C23A; font-weight: 600; }
:deep(.el-table) { background: transparent; }
:deep(.el-table th) { background: var(--bg-card); color: var(--text-primary); border-color: var(--border-color); }
:deep(.el-table td) { background: transparent; border-color: var(--border-color); color: var(--text-primary); }
:deep(.el-table tr:hover > td) { background: rgba(64, 158, 255, 0.05); }

/* Chart */
.chart-container { height: 320px; }
.chart-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 320px; color: var(--text-muted); }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat-box { text-align: center; padding: 20px; background: var(--bg-card); border-radius: 12px; transition: all 0.3s; }
.stat-box:hover { background: var(--bg-card-hover); transform: translateY(-2px); }
.stat-label { color: var(--text-secondary); font-size: 13px; margin-bottom: 8px; }
.stat-value { font-size: 24px; font-weight: 700; }
.stat-value.min { color: #67C23A; }
.stat-value.max { color: #F56C6C; }
.stat-value.avg { color: #409EFF; }

/* Insights */
.insights-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.insight-item { padding: 16px; background: var(--bg-card); border-radius: 12px; transition: all 0.3s; }
.insight-item:hover { background: var(--bg-card-hover); }
.insight-category { margin-bottom: 10px; }
.insight-text { color: var(--text-primary); font-size: 14px; line-height: 1.5; margin-bottom: 10px; }
.insight-meta { display: flex; justify-content: space-between; color: var(--text-muted); font-size: 12px; }

/* Responsive */
@media (max-width: 1200px) {
  .content-grid { grid-template-columns: 1fr; }
  .prediction-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
  .advice-banner { flex-direction: column; text-align: center; }
  .advice-urgency { margin-top: 10px; }
}
</style>
