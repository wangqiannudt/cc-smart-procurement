<script setup>
const props = defineProps({
  result: {
    type: Object,
    default: null
  }
})

const riskTagType = (score) => {
  if (score >= 60) return 'danger'
  if (score >= 30) return 'warning'
  return 'success'
}
</script>

<template>
  <el-card v-if="result" class="result-panel">
    <template #header>
      <div class="panel-header">
        <span>综合分析结果</span>
        <el-tag :type="riskTagType(result.risk_score)">
          风险分 {{ result.risk_score }}
        </el-tag>
      </div>
    </template>

    <el-descriptions :column="1" border>
      <el-descriptions-item label="综合建议">
        {{ result.summary?.overall_recommendation || '暂无' }}
      </el-descriptions-item>
      <el-descriptions-item label="优先级">
        {{ result.summary?.priority || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="分析维度">
        <el-space wrap>
          <el-tag
            v-for="(enabled, key) in (result.summary?.dimensions || {})"
            :key="key"
            size="small"
            :type="enabled ? 'success' : 'info'"
          >
            {{ key }}
          </el-tag>
        </el-space>
      </el-descriptions-item>
      <el-descriptions-item label="历史记录ID">
        #{{ result.history_id }}
      </el-descriptions-item>
    </el-descriptions>

    <div class="sub-sections">
      <el-collapse>
        <el-collapse-item title="需求审查结果" name="requirement">
          <pre>{{ JSON.stringify(result.requirement_result, null, 2) }}</pre>
        </el-collapse-item>
        <el-collapse-item title="价格分析结果" name="price">
          <pre>{{ JSON.stringify(result.price_result, null, 2) }}</pre>
        </el-collapse-item>
        <el-collapse-item title="合同分析结果" name="contract">
          <pre>{{ JSON.stringify(result.contract_result, null, 2) }}</pre>
        </el-collapse-item>
      </el-collapse>
    </div>
  </el-card>
</template>

<style scoped>
.result-panel {
  margin-bottom: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sub-sections {
  margin-top: 12px;
}

.result-panel :deep(.el-descriptions__body),
.result-panel :deep(.el-descriptions__table),
.result-panel :deep(.el-descriptions__table tr),
.result-panel :deep(.el-descriptions__table th),
.result-panel :deep(.el-descriptions__table td) {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-color) !important;
}

.result-panel :deep(.el-descriptions__label) {
  background: var(--bg-card-hover) !important;
  color: var(--text-primary) !important;
}

.result-panel :deep(.el-collapse) {
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.result-panel :deep(.el-collapse-item__header),
.result-panel :deep(.el-collapse-item__wrap),
.result-panel :deep(.el-collapse-item__content) {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-color) !important;
}

pre {
  margin: 0;
  padding: 8px 10px;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  background: var(--bg-input);
  border: 1px solid var(--border-color-light);
  border-radius: 8px;
  color: var(--text-primary);
}
</style>
