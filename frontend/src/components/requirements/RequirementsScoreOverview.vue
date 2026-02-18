<script setup>
defineProps({
  reviewResult: {
    type: Object,
    required: true
  },
  categoryName: {
    type: String,
    default: ''
  },
  subtypeName: {
    type: String,
    default: ''
  },
  scoreColor: {
    type: String,
    required: true
  },
  scoreStatus: {
    type: String,
    required: true
  }
})
</script>

<template>
  <div class="score-overview">
    <div class="score-left">
      <div class="score-circle" :style="{
        borderColor: scoreColor,
        background: `conic-gradient(${scoreColor} ${reviewResult.completeness_score * 3.6}deg, rgba(255,255,255,0.1) 0deg)`
      }">
        <div class="score-inner">
          <div class="score-value" :style="{ color: scoreColor }">
            {{ Math.round(reviewResult.completeness_score) }}
          </div>
          <div class="score-label">完整度评分</div>
        </div>
      </div>
      <div class="score-info">
        <div class="score-status" :style="{ color: scoreColor }">
          {{ scoreStatus }}
        </div>
        <div class="category-tags" v-if="categoryName || subtypeName">
          <el-tag v-if="categoryName" type="primary" effect="dark">{{ categoryName }}</el-tag>
          <el-tag v-if="subtypeName" type="success" effect="dark">{{ subtypeName }}</el-tag>
        </div>
      </div>
    </div>
    <div class="score-right">
      <div class="stat-grid">
        <div class="stat-item error">
          <div class="stat-icon"><el-icon><CircleClose /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ reviewResult.error_count }}</div>
            <div class="stat-label">错误</div>
          </div>
        </div>
        <div class="stat-item warning">
          <div class="stat-icon"><el-icon><Warning /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ reviewResult.warning_count }}</div>
            <div class="stat-label">警告</div>
          </div>
        </div>
        <div class="stat-item info">
          <div class="stat-icon"><el-icon><InfoFilled /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ reviewResult.info_count }}</div>
            <div class="stat-label">提示</div>
          </div>
        </div>
        <div class="stat-item fields">
          <div class="stat-icon"><el-icon><Document /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ reviewResult.field_count }}</div>
            <div class="stat-label">提取字段</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.score-overview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.score-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.score-inner {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(15, 15, 26, 0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  color: var(--text-muted);
  font-size: 11px;
  margin-top: 4px;
}

.score-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.score-status {
  font-size: 20px;
  font-weight: 600;
}

.category-tags {
  display: flex;
  gap: 8px;
}

.score-right {
  flex: 1;
  max-width: 400px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: var(--bg-card);
  border-radius: 8px;
}

.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.stat-item.error .stat-icon { background: rgba(245, 108, 108, 0.15); color: #f56c6c; }
.stat-item.warning .stat-icon { background: rgba(230, 162, 60, 0.15); color: #e6a23c; }
.stat-item.info .stat-icon { background: rgba(64, 158, 255, 0.15); color: #409eff; }
.stat-item.fields .stat-icon { background: rgba(103, 194, 58, 0.15); color: #67c23a; }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

@media (max-width: 1200px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .score-overview {
    flex-direction: column;
    gap: 20px;
  }

  .score-right {
    max-width: 100%;
    width: 100%;
  }
}
</style>
