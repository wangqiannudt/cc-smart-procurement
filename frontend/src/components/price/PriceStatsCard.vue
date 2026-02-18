<script setup>
const props = defineProps({
  priceRange: {
    type: Object,
    default: () => ({ min: 0, max: 0, avg: 0 })
  },
  formatPrice: {
    type: Function,
    required: true
  }
})
</script>

<template>
  <div class="card stats-card">
    <div class="card-header">
      <h3>价格统计</h3>
      <el-icon><DataBoard /></el-icon>
    </div>
    <div class="stats-grid">
      <div class="stat-box">
        <div class="stat-label">最低价</div>
        <div class="stat-value min">{{ formatPrice(priceRange.min) }}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">最高价</div>
        <div class="stat-value max">{{ formatPrice(priceRange.max) }}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">平均价</div>
        <div class="stat-value avg">{{ formatPrice(priceRange.avg) }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.card-header h3 {
  color: var(--text-primary);
  font-size: 16px;
  margin: 0;
  font-weight: 600;
}

.card-header .el-icon {
  color: #409eff;
  font-size: 22px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-box {
  text-align: center;
  padding: 20px;
  background: var(--bg-card);
  border-radius: 12px;
  transition: all 0.3s;
}

.stat-box:hover {
  background: var(--bg-card-hover);
  transform: translateY(-2px);
}

.stat-label {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
}

.stat-value.min {
  color: #67c23a;
}

.stat-value.max {
  color: #f56c6c;
}

.stat-value.avg {
  color: #409eff;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
