<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const loading = ref(false)
const stats = ref({
  reviewedRequirements: 156,
  priceRecords: 2840,
  analyzedContracts: 98
})

// 智能推荐
const smartRecommendations = ref([])
const recommendationsLoading = ref(false)

// 市场洞察
const marketInsights = ref([])
const insightsLoading = ref(false)

// 价格预警
const priceAlerts = ref([])

const recentActivities = ref([
  { type: 'requirement', desc: '审查服务器采购需求', time: '10分钟前', status: '完成' },
  { type: 'price', desc: '查询网络设备价格', time: '30分钟前', status: '完成' },
  { type: 'contract', desc: '分析软件采购合同', time: '1小时前', status: '完成' },
  { type: 'requirement', desc: '审查存储设备需求', time: '2小时前', status: '完成' },
  { type: 'price', desc: '查询防火墙价格', time: '3小时前', status: '完成' }
])

const systemStatus = ref([
  { name: '需求审查智能体', status: '正常', uptime: '99.9%', icon: 'Document' },
  { name: '价格参考智能体', status: '正常', uptime: '99.8%', icon: 'TrendCharts' },
  { name: '合同分析智能体', status: '正常', uptime: '99.7%', icon: 'DocumentCopy' },
  { name: '知识库智能体', status: '正常', uptime: '99.5%', icon: 'Collection' }
])

// 加载智能推荐
const loadRecommendations = async () => {
  recommendationsLoading.value = true
  try {
    // 获取市场洞察作为推荐基础
    const response = await axios.get('/api/price-reference/market-insights')
    if (response.data.success && response.data.data?.insights) {
      marketInsights.value = response.data.data.insights

      // 基于市场洞察生成智能推荐
      smartRecommendations.value = response.data.data.insights.slice(0, 3).map(insight => ({
        type: insight.trend_slope > 0 ? 'price_up' : insight.trend_slope < 0 ? 'price_down' : 'stable',
        title: insight.insight,
        category: insight.category,
        action: insight.trend_slope > 0 ? '建议尽快采购' : insight.trend_slope < 0 ? '可延后采购' : '按需采购',
        priority: Math.abs(insight.trend_slope) > 1000 ? 'high' : 'medium'
      }))

      // 生成价格预警
      priceAlerts.value = response.data.data.insights
        .filter(i => Math.abs(i.trend_slope) > 500)
        .map(i => ({
          category: i.category,
          alert: i.trend_slope > 0 ? '价格上涨趋势' : '价格下降趋势',
          severity: Math.abs(i.trend_slope) > 1000 ? 'high' : 'medium'
        }))
    }
  } catch (error) {
    console.error('加载推荐失败:', error)
  } finally {
    recommendationsLoading.value = false
  }
}

// 快速分析
const quickAnalyze = async (type) => {
  router.push({
    path: '/chat',
    query: { action: type }
  })
}

const getTypeIcon = (type) => {
  const icons = {
    requirement: 'Document',
    price: 'TrendCharts',
    contract: 'DocumentCopy'
  }
  return icons[type] || 'Document'
}

// 获取 CSS 变量值（用于动态颜色）
const getCSSVar = (name) => {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

const getTypeColor = (type) => {
  // 使用 CSS 变量，跟随主题变化
  const colors = {
    requirement: 'var(--color-primary)',
    price: 'var(--color-success)',
    contract: 'var(--color-warning)'
  }
  return colors[type] || 'var(--text-muted)'
}

const getRecommendationIcon = (type) => {
  const icons = {
    price_up: 'Top',
    price_down: 'Bottom',
    stable: 'Minus'
  }
  return icons[type] || 'InfoFilled'
}

const getRecommendationColor = (type) => {
  // 使用 CSS 变量，跟随主题变化
  const colors = {
    price_up: 'var(--color-danger)',
    price_down: 'var(--color-success)',
    stable: 'var(--color-primary)'
  }
  return colors[type] || 'var(--text-muted)'
}

const getAlertColor = (severity) => {
  // 使用 CSS 变量，跟随主题变化
  return severity === 'high' ? 'var(--color-danger)' : 'var(--color-warning)'
}

onMounted(() => {
  loadRecommendations()
})
</script>

<template>
  <div class="home-container">
    <!-- Header -->
    <div class="header">
      <div class="header-content">
        <h1>系统概览</h1>
        <p class="subtitle">智慧采购系统 · AI驱动的智能采购助手</p>
      </div>
    </div>

    <!-- 智能推荐横幅 -->
    <div v-if="smartRecommendations.length > 0" class="recommendations-banner">
      <div class="banner-header">
        <el-icon><Opportunity /></el-icon>
        <span>智能推荐</span>
      </div>
      <div class="recommendations-scroll">
        <div v-for="(rec, index) in smartRecommendations" :key="index" class="recommendation-chip" :class="rec.priority">
          <el-icon :color="getRecommendationColor(rec.type)">
            <component :is="getRecommendationIcon(rec.type)" />
          </el-icon>
          <span class="rec-category">{{ rec.category }}</span>
          <span class="rec-action">{{ rec.action }}</span>
        </div>
      </div>
    </div>

    <!-- 价格预警 -->
    <div v-if="priceAlerts.length > 0" class="alerts-section">
      <div v-for="(alert, index) in priceAlerts.slice(0, 2)" :key="index" class="alert-item" :class="alert.severity">
        <el-icon><Warning /></el-icon>
        <span>{{ alert.category }} - {{ alert.alert }}</span>
        <el-button size="small" text @click="router.push('/price')">查看详情</el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-card" v-for="(stat, key) in stats" :key="key">
          <div class="stat-icon" :class="key">
            <el-icon :size="36">
              <component :is="key === 'reviewedRequirements' ? 'Document' : key === 'priceRecords' ? 'TrendCharts' : 'DocumentCopy'" />
            </el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stat }}</div>
            <div class="stat-label">
              {{ key === 'reviewedRequirements' ? '已审查需求' : key === 'priceRecords' ? '价格库记录' : '已分析合同' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="main-grid">
      <!-- System Status -->
      <div class="card status-card">
        <div class="card-header">
          <h3>智能体状态</h3>
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="status-list">
          <div class="status-item" v-for="item in systemStatus" :key="item.name">
            <div class="status-info">
              <el-icon class="status-icon"><component :is="item.icon" /></el-icon>
              <span class="status-name">{{ item.name }}</span>
              <span class="status-badge" :class="item.status === '正常' ? 'success' : 'warning'">
                {{ item.status }}
              </span>
            </div>
            <div class="status-uptime">运行时间: {{ item.uptime }}</div>
          </div>
        </div>
      </div>

      <!-- Smart Recommendations -->
      <div class="card recommendations-card">
        <div class="card-header">
          <h3>采购建议</h3>
          <el-icon><Opportunity /></el-icon>
        </div>
        <div v-loading="recommendationsLoading" class="recommendations-list">
          <div v-if="smartRecommendations.length === 0 && !recommendationsLoading" class="empty-state">
            <el-icon :size="40"><Opportunity /></el-icon>
            <p>正在分析市场数据...</p>
          </div>
          <div v-for="(rec, index) in smartRecommendations" :key="index" class="recommendation-item">
            <div class="rec-icon" :style="{ background: getRecommendationColor(rec.type) + '20' }">
              <el-icon :color="getRecommendationColor(rec.type)" :size="20">
                <component :is="getRecommendationIcon(rec.type)" />
              </el-icon>
            </div>
            <div class="rec-content">
              <div class="rec-title">{{ rec.title }}</div>
              <div class="rec-meta">
                <el-tag size="small" :type="rec.priority === 'high' ? 'danger' : 'warning'">{{ rec.action }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activities -->
      <div class="card activity-card">
        <div class="card-header">
          <h3>最近活动</h3>
          <el-icon><Clock /></el-icon>
        </div>
        <div class="activity-list">
          <div class="activity-item" v-for="(activity, index) in recentActivities" :key="index">
            <div class="activity-icon" :style="{ backgroundColor: getTypeColor(activity.type) + '20' }">
              <el-icon :color="getTypeColor(activity.type)">
                <component :is="getTypeIcon(activity.type)" />
              </el-icon>
            </div>
            <div class="activity-info">
              <div class="activity-desc">{{ activity.desc }}</div>
              <div class="activity-meta">
                <span class="activity-time">{{ activity.time }}</span>
                <span class="activity-status">{{ activity.status }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="card actions-card">
        <div class="card-header">
          <h3>快速操作</h3>
          <el-icon><Lightning /></el-icon>
        </div>
        <div class="actions-grid">
          <router-link to="/chat" class="action-btn primary">
            <el-icon :size="28"><ChatDotRound /></el-icon>
            <span>AI对话</span>
            <small>智能问答</small>
          </router-link>
          <router-link to="/requirements" class="action-btn">
            <el-icon :size="28"><Document /></el-icon>
            <span>需求审查</span>
            <small>文档分析</small>
          </router-link>
          <router-link to="/price" class="action-btn">
            <el-icon :size="28"><TrendCharts /></el-icon>
            <span>价格参考</span>
            <small>趋势预测</small>
          </router-link>
          <router-link to="/contract" class="action-btn">
            <el-icon :size="28"><DocumentCopy /></el-icon>
            <span>合同分析</span>
            <small>风险识别</small>
          </router-link>
        </div>
      </div>
    </div>

    <!-- AI 快捷分析 -->
    <div class="card quick-analysis-card">
      <div class="card-header">
        <h3>AI快捷分析</h3>
        <el-icon><MagicStick /></el-icon>
      </div>
      <div class="quick-analysis-grid">
        <div class="analysis-item" @click="quickAnalyze('server')">
          <el-icon :size="24"><Monitor /></el-icon>
          <span>服务器选型</span>
        </div>
        <div class="analysis-item" @click="quickAnalyze('network')">
          <el-icon :size="24"><Connection /></el-icon>
          <span>网络设备</span>
        </div>
        <div class="analysis-item" @click="quickAnalyze('storage')">
          <el-icon :size="24"><Files /></el-icon>
          <span>存储设备</span>
        </div>
        <div class="analysis-item" @click="quickAnalyze('software')">
          <el-icon :size="24"><Grid /></el-icon>
          <span>软件采购</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container { animation: fadeIn 0.5s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

.header { background: linear-gradient(135deg, var(--color-primary-bg) 0%, var(--color-primary-border) 100%); border-radius: 16px; padding: 35px; margin-bottom: 25px; border: 1px solid var(--border-color); }
.header-content h1 { color: var(--text-primary); font-size: 32px; margin: 0 0 8px 0; font-weight: 600; }
.subtitle { color: var(--text-secondary); font-size: 15px; margin: 0; }

/* Recommendations Banner */
.recommendations-banner { background: linear-gradient(90deg, var(--color-primary-bg) 0%, var(--color-primary-border) 100%); border-radius: 12px; padding: 12px 20px; margin-bottom: 20px; display: flex; align-items: center; gap: 16px; border: 1px solid var(--color-primary-border); }
.banner-header { display: flex; align-items: center; gap: 8px; color: var(--color-primary); font-weight: 600; font-size: 14px; white-space: nowrap; }
.recommendations-scroll { display: flex; gap: 12px; overflow-x: auto; flex: 1; padding: 4px 0; }
.recommendation-chip { display: flex; align-items: center; gap: 8px; padding: 6px 14px; background: var(--bg-card-hover); border-radius: 20px; font-size: 13px; white-space: nowrap; }
.recommendation-chip.high { background: var(--color-primary-bg); border: 1px solid var(--color-primary-border); }
.rec-category { color: var(--text-primary); }
.rec-action { color: var(--text-secondary); }

/* Alerts */
.alerts-section { display: flex; gap: 12px; margin-bottom: 20px; }
.alert-item { display: flex; align-items: center; gap: 10px; padding: 10px 16px; background: var(--color-primary-bg); border-radius: 10px; font-size: 13px; color: var(--text-primary); flex: 1; }
.alert-item.medium { background: var(--color-primary-border); }
.alert-item .el-icon { color: var(--color-danger); }
.alert-item.medium .el-icon { color: var(--color-warning); }

/* Stats */
.stats-section { margin-bottom: 25px; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat-card { background: var(--bg-card); border-radius: 14px; padding: 20px; display: flex; align-items: center; gap: 16px; border: 1px solid var(--border-color); transition: all 0.3s; cursor: pointer; }
.stat-card:hover { transform: translateY(-4px); border-color: var(--color-primary-border); box-shadow: var(--shadow-glow); }
.stat-icon { width: 60px; height: 60px; border-radius: 14px; display: flex; align-items: center; justify-content: center; }
.stat-icon.reviewedRequirements { background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%); }
.stat-icon.priceRecords { background: linear-gradient(135deg, var(--color-success) 0%, color-mix(in srgb, var(--color-success) 70%, white) 100%); }
.stat-icon.analyzedContracts { background: linear-gradient(135deg, var(--color-warning) 0%, color-mix(in srgb, var(--color-warning) 70%, white) 100%); }
.stat-icon .el-icon { color: #ffffff; }
.stat-value { color: var(--text-primary); font-size: 36px; font-weight: 700; margin-bottom: 4px; }
.stat-label { color: var(--text-secondary); font-size: 13px; }

/* Main Grid */
.main-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.main-grid .actions-card { grid-column: span 2; }

/* Cards */
.card { background: var(--bg-card); border-radius: 16px; padding: 20px; border: 1px solid var(--border-color); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }
.card-header h3 { color: var(--text-primary); font-size: 16px; margin: 0; font-weight: 600; }
.card-header .el-icon { color: var(--color-primary); font-size: 22px; }

/* Status List */
.status-list { display: flex; flex-direction: column; gap: 10px; }
.status-item { background: var(--bg-card); padding: 12px; border-radius: 10px; }
.status-info { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.status-icon { color: var(--color-primary); }
.status-name { color: var(--text-primary); font-size: 14px; flex: 1; }
.status-badge { padding: 3px 10px; border-radius: 12px; font-size: 11px; }
.status-badge.success { background: var(--color-primary-bg); color: var(--color-success); }
.status-uptime { color: var(--text-muted); font-size: 12px; padding-left: 28px; }

/* Recommendations */
.recommendations-list { display: flex; flex-direction: column; gap: 10px; min-height: 150px; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 150px; color: var(--text-muted); }
.recommendation-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg-card); border-radius: 10px; transition: all 0.2s; }
.recommendation-item:hover { background: var(--bg-card-hover); }
.rec-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.rec-title { color: var(--text-primary); font-size: 13px; margin-bottom: 4px; }
.rec-meta { display: flex; gap: 8px; }

/* Activity List */
.activity-list { display: flex; flex-direction: column; gap: 10px; }
.activity-item { display: flex; align-items: center; gap: 12px; padding: 10px; border-radius: 10px; }
.activity-item:hover { background: var(--bg-card); }
.activity-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.activity-desc { color: var(--text-primary); font-size: 13px; margin-bottom: 4px; }
.activity-meta { display: flex; gap: 10px; }
.activity-time { color: var(--text-muted); font-size: 12px; }
.activity-status { color: var(--color-success); font-size: 12px; }

/* Actions Grid */
.actions-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.action-btn { background: linear-gradient(135deg, var(--color-primary-bg) 0%, var(--color-primary-border) 100%); border: 1px solid var(--color-primary-border); border-radius: 12px; padding: 20px 16px; display: flex; flex-direction: column; align-items: center; gap: 8px; text-decoration: none; transition: all 0.3s; position: relative; overflow: hidden; }
.action-btn .el-icon { color: var(--color-primary); }
.action-btn span { color: var(--text-primary); font-size: 14px; font-weight: 500; }
.action-btn small { color: var(--text-muted); font-size: 11px; }
.action-btn:hover { background: linear-gradient(135deg, var(--color-primary-border) 0%, var(--color-primary-bg) 100%); transform: translateY(-3px); box-shadow: var(--shadow-glow); }
.action-btn.primary { background: linear-gradient(135deg, var(--color-primary-bg) 0%, transparent 100%); border-color: var(--color-primary-border); }
.action-btn.primary .el-icon { color: var(--color-primary); }

/* Quick Analysis */
.quick-analysis-card { margin-top: 20px; }
.quick-analysis-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.analysis-item { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 16px; background: var(--bg-card); border-radius: 12px; cursor: pointer; transition: all 0.3s; }
.analysis-item .el-icon { color: var(--color-primary); }
.analysis-item span { color: var(--text-secondary); font-size: 13px; }
.analysis-item:hover { background: var(--color-primary-bg); transform: translateY(-2px); }

/* Responsive */
@media (max-width: 1200px) {
  .main-grid { grid-template-columns: 1fr; }
  .main-grid .actions-card { grid-column: span 1; }
  .actions-grid { grid-template-columns: repeat(2, 1fr); }
  .quick-analysis-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
  .alerts-section { flex-direction: column; }
  .recommendations-banner { flex-direction: column; align-items: flex-start; }
  .recommendations-scroll { flex-wrap: wrap; }
  .actions-grid { grid-template-columns: 1fr 1fr; }
}
</style>
