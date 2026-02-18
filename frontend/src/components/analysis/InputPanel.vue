<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'clear-draft'])

const templates = [
  { value: 'server', label: '服务器采购' },
  { value: 'workstation', label: '工作站采购' },
  { value: 'instrument', label: '仪器仪表采购' },
  { value: 'custom', label: '自定义场景' }
]

const form = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const applyTemplate = (template) => {
  if (template === 'server') {
    form.value = {
      ...form.value,
      template_type: 'server',
      requirement_text: '采购服务器用于数据库集群，要求高可用、支持虚拟化。',
      product_keyword: '服务器',
      budget: 200000
    }
    return
  }
  if (template === 'workstation') {
    form.value = {
      ...form.value,
      template_type: 'workstation',
      requirement_text: '采购图形工作站用于3D建模与渲染，要求稳定性高。',
      product_keyword: '工作站',
      budget: 120000
    }
    return
  }
  if (template === 'instrument') {
    form.value = {
      ...form.value,
      template_type: 'instrument',
      requirement_text: '采购测试测量仪器用于实验室环境，需附带校准服务。',
      product_keyword: '仪器仪表',
      budget: 300000
    }
    return
  }
  form.value = {
    ...form.value,
    template_type: 'custom'
  }
}
</script>

<template>
  <el-card class="input-panel">
    <template #header>
      <div class="panel-header">
        <span>综合分析输入</span>
        <el-space>
          <el-button size="small" @click="emit('clear-draft')">清空草稿</el-button>
          <el-button type="primary" size="small" :loading="loading" @click="emit('submit')">
            开始分析
          </el-button>
        </el-space>
      </div>
    </template>

    <el-form label-position="top">
      <el-form-item label="场景模板">
        <el-select
          v-model="form.template_type"
          placeholder="请选择模板"
          @change="applyTemplate"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="item in templates"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="需求文本">
        <el-input
          v-model="form.requirement_text"
          type="textarea"
          :rows="4"
          placeholder="输入采购需求文本"
          class="analysis-textarea"
        />
      </el-form-item>

      <el-form-item label="合同文本（可选）">
        <el-input
          v-model="form.contract_text"
          type="textarea"
          :rows="4"
          placeholder="输入合同条款文本以进行风险分析"
          class="analysis-textarea"
        />
      </el-form-item>

      <div class="row">
        <el-form-item label="产品关键词" class="col">
          <el-input v-model="form.product_keyword" placeholder="如：服务器、工作站" />
        </el-form-item>
        <el-form-item label="预算（元）" class="col">
          <el-input-number
            v-model="form.budget"
            :min="0"
            :step="1000"
            controls-position="right"
            style="width: 100%"
            class="budget-input"
          />
        </el-form-item>
      </div>
    </el-form>
  </el-card>
</template>

<style scoped>
.input-panel {
  margin-bottom: 16px;
}

.input-panel :deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color-light);
}

.input-panel :deep(.el-form-item__label) {
  color: var(--text-secondary);
}

.analysis-textarea :deep(.el-textarea__inner) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  line-height: 1.6;
}

.analysis-textarea :deep(.el-textarea__inner::placeholder) {
  color: var(--text-muted);
}

.analysis-textarea :deep(.el-textarea__inner:focus) {
  border-color: var(--color-primary);
}

.budget-input :deep(.el-input-number__increase),
.budget-input :deep(.el-input-number__decrease) {
  background: var(--bg-card);
  color: var(--text-secondary);
}

.budget-input :deep(.el-input-number__increase:hover),
.budget-input :deep(.el-input-number__decrease:hover) {
  background: var(--bg-card-hover);
  color: var(--color-primary);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.col {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .row {
    grid-template-columns: 1fr;
  }
}
</style>
