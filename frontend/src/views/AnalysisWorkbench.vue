<script setup>
import { computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import InputPanel from '../components/analysis/InputPanel.vue'
import ResultPanel from '../components/analysis/ResultPanel.vue'
import EvidencePanel from '../components/analysis/EvidencePanel.vue'
import StateBlock from '../components/common/StateBlock.vue'
import { useAnalysisWorkflow, useDraftCache } from '../composables'

const initialPayload = {
  requirement_text: '',
  contract_text: '',
  product_keyword: '',
  budget: null,
  template_type: ''
}

const { state: formState, loadDraft, clearDraft } = useDraftCache(
  'analysis_workflow_draft',
  initialPayload
)
const {
  loading,
  error,
  result,
  history,
  total,
  runWorkflow,
  fetchHistory,
  reuseHistory,
  clearResult
} = useAnalysisWorkflow()

const hasResult = computed(() => !!result.value)

const submitAnalysis = async () => {
  try {
    await runWorkflow(formState.value)
    await fetchHistory()
    ElMessage.success('分析完成')
  } catch {}
}

const clearAllDraft = () => {
  clearDraft()
  clearResult()
  ElMessage.success('草稿已清空')
}

const handleReuse = async (row) => {
  try {
    await reuseHistory(row.id)
    ElMessage.success('已基于历史记录重新分析')
  } catch {}
}

onMounted(async () => {
  loadDraft()
  await fetchHistory()
})
</script>

<template>
  <div class="analysis-workbench">
    <div class="page-title">
      <h2>综合分析工作台</h2>
      <p>将需求、价格和合同分析整合为一个可追溯结论。</p>
    </div>

    <InputPanel
      v-model="formState"
      :loading="loading"
      @submit="submitAnalysis"
      @clear-draft="clearAllDraft"
    />

    <StateBlock
      v-if="loading"
      type="loading"
      title="分析中"
      description="系统正在组合多个智能体结果，请稍候。"
    />

    <StateBlock
      v-else-if="error"
      type="error"
      title="分析失败"
      :description="error"
    />

    <template v-else-if="hasResult">
      <ResultPanel :result="result" />
      <EvidencePanel :evidence="result.evidence" />
    </template>

    <StateBlock
      v-else
      type="empty"
      title="尚未执行分析"
      description="填写输入后点击“开始分析”。"
    />

    <el-card class="history-panel">
      <template #header>
        <div class="panel-header">
          <span>分析历史</span>
          <el-tag type="info">共 {{ total }} 条</el-tag>
        </div>
      </template>

      <el-table :data="history" size="small" empty-text="暂无历史记录">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="template_type" label="模板" width="120" />
        <el-table-column prop="risk_score" label="风险分" width="90" />
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button text type="primary" @click="handleReuse(row)">复用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.analysis-workbench {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-title h2 {
  margin: 0 0 8px;
  font-size: 22px;
  color: var(--text-primary);
}

.page-title p {
  margin: 0;
  color: var(--text-secondary);
}

.history-panel {
  margin-bottom: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
