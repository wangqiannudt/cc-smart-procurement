<script setup>
const props = defineProps({
  evidence: {
    type: Object,
    default: () => ({ rules: [], price_sources: [], contract_clauses: [] })
  }
})
</script>

<template>
  <el-card class="evidence-panel">
    <template #header>
      <span>证据链</span>
    </template>

    <el-tabs>
      <el-tab-pane label="规则证据">
        <el-table :data="evidence.rules || []" size="small" empty-text="暂无规则证据">
          <el-table-column prop="rule_id" label="规则ID" min-width="120" />
          <el-table-column prop="field" label="字段" min-width="120" />
          <el-table-column prop="priority" label="优先级" width="90" />
          <el-table-column prop="message" label="说明" min-width="220" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="价格来源">
        <el-table :data="evidence.price_sources || []" size="small" empty-text="暂无价格来源">
          <el-table-column prop="product" label="产品" min-width="180" />
          <el-table-column prop="source" label="来源" width="120" />
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="price" label="价格" width="120" />
          <el-table-column prop="note" label="备注" min-width="180" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="合同条款">
        <el-table :data="evidence.contract_clauses || []" size="small" empty-text="暂无合同证据">
          <el-table-column prop="clause_type" label="类型" width="120" />
          <el-table-column prop="keyword" label="关键词" width="120" />
          <el-table-column prop="excerpt" label="原文片段" min-width="280" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<style scoped>
.evidence-panel {
  margin-bottom: 16px;
}
</style>
