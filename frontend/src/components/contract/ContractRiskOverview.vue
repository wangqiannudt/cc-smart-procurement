<script setup>
defineProps({
  analysisResult: {
    type: Object,
    required: true
  },
  foundElementsCount: {
    type: Number,
    default: 0
  },
  riskColor: {
    type: String,
    required: true
  }
})
</script>

<template>
  <div class="risk-overview-card">
    <div class="risk-left">
      <div class="risk-badge-large" :style="{
        borderColor: riskColor,
        background: `conic-gradient(${riskColor} ${(100 - analysisResult.completeness) * 3.6}deg, rgba(255,255,255,0.1) 0deg)`
      }">
        <div class="risk-badge-inner">
          <div class="risk-level-text" :style="{ color: riskColor }">
            {{ analysisResult.risk_level }}
          </div>
          <div class="risk-level-label">风险评估</div>
        </div>
      </div>
      <div class="risk-info">
        <div class="completeness-value" :style="{ color: riskColor }">
          {{ analysisResult.completeness }}%
        </div>
        <div class="completeness-label">合同完整度</div>
      </div>
    </div>
    <div class="risk-right">
      <div class="stat-grid">
        <div class="stat-item high">
          <div class="stat-icon"><el-icon><WarnTriangleFilled /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ analysisResult.risk_summary['高风险'] || 0 }}</div>
            <div class="stat-label">高风险</div>
          </div>
        </div>
        <div class="stat-item medium">
          <div class="stat-icon"><el-icon><Warning /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ analysisResult.risk_summary['中风险'] || 0 }}</div>
            <div class="stat-label">中风险</div>
          </div>
        </div>
        <div class="stat-item low">
          <div class="stat-icon"><el-icon><InfoFilled /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ analysisResult.risk_summary['需特别关注'] || 0 }}</div>
            <div class="stat-label">需关注</div>
          </div>
        </div>
        <div class="stat-item elements">
          <div class="stat-icon"><el-icon><Document /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ foundElementsCount }}</div>
            <div class="stat-label">已识别要素</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.risk-overview-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.risk-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.risk-badge-large {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid;
}

.risk-badge-inner {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(15, 15, 26, 0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.risk-level-text {
  font-size: 14px;
  font-weight: 700;
}

.risk-level-label {
  color: var(--text-muted);
  font-size: 10px;
  margin-top: 2px;
}

.risk-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.completeness-value {
  font-size: 28px;
  font-weight: 700;
}

.completeness-label {
  color: var(--text-muted);
  font-size: 13px;
}

.risk-right {
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

.stat-item.high .stat-icon { background: rgba(245, 108, 108, 0.15); color: #f56c6c; }
.stat-item.medium .stat-icon { background: rgba(230, 162, 60, 0.15); color: #e6a23c; }
.stat-item.low .stat-icon { background: rgba(64, 158, 255, 0.15); color: #409eff; }
.stat-item.elements .stat-icon { background: rgba(103, 194, 58, 0.15); color: #67c23a; }

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
  .risk-overview-card {
    flex-direction: column;
    gap: 20px;
  }

  .risk-right {
    max-width: 100%;
    width: 100%;
  }
}
</style>
