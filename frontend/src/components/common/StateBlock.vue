<script setup>
defineProps({
  type: {
    type: String,
    default: 'empty'
  },
  title: {
    type: String,
    default: '暂无数据'
  },
  description: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div class="state-block" :class="`state-${type}`">
    <el-empty
      v-if="type === 'empty'"
      :description="description || title"
    />
    <div v-else-if="type === 'loading'" class="state-inline">
      <el-icon class="is-loading"><RefreshRight /></el-icon>
      <span>{{ description || '加载中...' }}</span>
    </div>
    <div v-else-if="type === 'error'" class="state-inline error">
      <el-icon><CircleClose /></el-icon>
      <span>{{ description || title || '请求失败' }}</span>
    </div>
    <div v-else-if="type === 'unauthorized'" class="state-inline warning">
      <el-icon><Warning /></el-icon>
      <span>{{ description || title || '无权限访问' }}</span>
    </div>
    <div v-else class="state-inline">
      <span>{{ description || title }}</span>
    </div>
  </div>
</template>

<style scoped>
.state-block {
  width: 100%;
  padding: 20px;
  border: 1px dashed var(--border-color);
  border-radius: 12px;
  background: var(--bg-card);
}

.state-inline {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-secondary);
}

.state-inline.error {
  color: var(--color-danger);
}

.state-inline.warning {
  color: var(--color-warning);
}
</style>
