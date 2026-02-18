<script setup>
const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  categories: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const updateField = (key, value) => {
  emit('update:modelValue', {
    ...props.modelValue,
    [key]: value
  })
}
</script>

<template>
  <div class="card search-card">
    <div class="card-header">
      <h3>搜索筛选</h3>
      <el-icon><Search /></el-icon>
    </div>
    <el-form :model="modelValue" inline class="search-form">
      <el-form-item label="商品分类">
        <el-select
          :model-value="modelValue.category"
          placeholder="请选择分类"
          clearable
          style="width: 180px"
          @update:model-value="(v) => updateField('category', v)"
        >
          <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
        </el-select>
      </el-form-item>
      <el-form-item label="关键词">
        <el-input
          :model-value="modelValue.keyword"
          placeholder="产品名称或规格"
          clearable
          style="width: 200px"
          @update:model-value="(v) => updateField('keyword', v)"
        />
      </el-form-item>
      <el-form-item label="价格范围">
        <el-input-number
          :model-value="modelValue.minPrice"
          :min="0"
          :step="10000"
          controls-position="right"
          style="width: 130px"
          @update:model-value="(v) => updateField('minPrice', v)"
        />
        <span class="price-separator">-</span>
        <el-input-number
          :model-value="modelValue.maxPrice"
          :min="0"
          :step="10000"
          controls-position="right"
          style="width: 130px"
          @update:model-value="(v) => updateField('maxPrice', v)"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="emit('search')">
          <el-icon><Search /></el-icon> 查询
        </el-button>
        <el-button @click="emit('reset')">
          <el-icon><RefreshRight /></el-icon> 重置
        </el-button>
      </el-form-item>
    </el-form>
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

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.search-form :deep(.el-form-item__label) {
  color: var(--text-secondary);
}

.price-separator {
  color: var(--text-muted);
  margin: 0 8px;
}
</style>
