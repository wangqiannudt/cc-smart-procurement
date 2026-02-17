<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const uploadRef = ref()
const uploadLoading = ref(false)
const reviewResult = ref(null)
const dialogVisible = ref(false)
const currentIssue = ref(null)
const inputMode = ref('text') // 'text' or 'file'
const textContent = ref('')
const showInputPanel = ref(true) // 控制输入面板的展开/收起

// 品类相关
const categories = ref([])
const selectedCategory = ref(null)
const selectedSubtype = ref(null)
const categoryFields = ref([])
const loadingCategories = ref(false)

// 计算子类型选项
const subtypeOptions = computed(() => {
  if (!selectedCategory.value) return []
  const cat = categories.value.find(c => c.id === selectedCategory.value)
  return cat?.subtypes || []
})

// 监听品类变化，清空子类型选择
watch(selectedCategory, () => {
  selectedSubtype.value = null
})

const uploadConfig = reactive({
  accept: '.docx,.txt',
  limit: 1,
  autoUpload: false,
  showFileList: true
})

const fileList = ref([])

// 加载品类列表
const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const response = await axios.get('/api/categories')
    if (response.data.success) {
      categories.value = response.data.data
    }
  } catch (error) {
    console.error('加载品类失败:', error)
  } finally {
    loadingCategories.value = false
  }
}

onMounted(() => {
  loadCategories()
})

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const handleBeforeUpload = () => {
  return false
}

const handleChange = (uploadFile) => {
  fileList.value = [uploadFile]
  textContent.value = ''
}

const handleRemove = () => {
  fileList.value = []
  reviewResult.value = null
  showInputPanel.value = true
}

const handleModeChange = (mode) => {
  inputMode.value = mode
  fileList.value = []
  textContent.value = ''
}

const handleReview = async () => {
  if (inputMode.value === 'file') {
    if (fileList.value.length === 0) {
      ElMessage.warning('请先上传文件')
      return
    }
  } else {
    if (!textContent.value.trim()) {
      ElMessage.warning('请输入需求内容')
      return
    }
  }

  uploadLoading.value = true

  try {
    let response
    if (inputMode.value === 'file') {
      const formData = new FormData()
      formData.append('file', fileList.value[0].raw)
      if (selectedCategory.value) {
        formData.append('category_id', selectedCategory.value)
      }
      if (selectedSubtype.value) {
        formData.append('subtype_id', selectedSubtype.value)
      }
      response = await axios.post('/api/review-requirements', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    } else {
      response = await axios.post('/api/review-requirements/text', {
        content: textContent.value,
        category_id: selectedCategory.value || undefined,
        subtype_id: selectedSubtype.value || undefined
      })
    }

    if (response.data.success) {
      reviewResult.value = response.data.data
      showInputPanel.value = false // 收起输入面板
      ElMessage.success('审查完成')
    } else {
      ElMessage.error('审查失败: ' + response.data.error)
    }
  } catch (error) {
    ElMessage.error('审查失败: ' + error.message)
  } finally {
    uploadLoading.value = false
  }
}

const handleNewReview = () => {
  reviewResult.value = null
  fileList.value = []
  textContent.value = ''
  showInputPanel.value = true
}

const showIssueDetail = (issue) => {
  currentIssue.value = issue
  dialogVisible.value = true
}

const getLevelType = (level) => {
  const types = {
    error: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return types[level] || 'info'
}

const getLevelText = (level) => {
  const texts = {
    error: '错误',
    warning: '警告',
    info: '提示'
  }
  return texts[level] || level
}

const getScoreColor = (score) => {
  if (score >= 80) return '#67C23A'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}

const getScoreStatus = (score) => {
  if (score >= 80) return '优秀'
  if (score >= 60) return '合格'
  return '需改进'
}

const formatFieldValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') {
    if (value.comparator && value.value !== undefined) {
      const comp = value.comparator === 'gte' ? '≥' : value.comparator === 'lte' ? '≤' : ''
      return `${comp}${value.value}${value.unit ? ' ' + value.unit : ''}`
    }
    if (value.media && value.value) {
      return `${value.media} ${value.value}${value.unit ? value.unit : ''}`
    }
    return JSON.stringify(value)
  }
  return String(value)
}

// 按优先级分组问题
const groupedIssues = computed(() => {
  if (!reviewResult.value?.issues) return { errors: [], warnings: [], infos: [] }
  return {
    errors: reviewResult.value.issues.filter(i => i.level === 'error'),
    warnings: reviewResult.value.issues.filter(i => i.level === 'warning'),
    infos: reviewResult.value.issues.filter(i => i.level === 'info')
  }
})

// 按组分类提取的字段
const groupedFields = computed(() => {
  if (!reviewResult.value?.extracted_fields) return {}
  return reviewResult.value.extracted_fields
})
</script>

<template>
  <div class="requirements-container">
    <div class="page-header">
      <h1>需求规范审查</h1>
      <p>智能分析需求文档，识别潜在问题并提供改进建议</p>
    </div>

    <!-- 输入面板 - 可折叠 -->
    <div class="input-panel" :class="{ 'collapsed': !showInputPanel && reviewResult }">
      <div class="panel-header" @click="showInputPanel = !showInputPanel">
        <div class="header-left">
          <el-icon class="toggle-icon" :class="{ 'rotated': !showInputPanel }"><ArrowDown /></el-icon>
          <span class="panel-title">
            {{ reviewResult ? '重新输入需求' : '输入需求文档' }}
          </span>
          <template v-if="reviewResult">
            <el-tag v-if="selectedCategory" type="primary" size="small" style="margin-left: 12px;">
              {{ categories.find(c => c.id === selectedCategory)?.name }}
            </el-tag>
            <el-tag v-if="selectedSubtype" type="success" size="small" style="margin-left: 4px;">
              {{ subtypeOptions.find(s => s.id === selectedSubtype)?.name }}
            </el-tag>
          </template>
        </div>
        <div class="header-right" v-if="reviewResult">
          <el-button type="primary" size="small" @click.stop="handleNewReview">
            <el-icon><Plus /></el-icon>
            新建审查
          </el-button>
        </div>
      </div>

      <div class="panel-content" v-show="showInputPanel || !reviewResult">
        <!-- 品类选择 -->
        <div class="category-row">
          <div class="category-label">选择品类</div>
          <div class="category-selectors">
            <el-select
              v-model="selectedCategory"
              placeholder="选择品类（可选）"
              clearable
              :loading="loadingCategories"
              class="category-select"
            >
              <el-option
                v-for="cat in categories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              >
                <span>{{ cat.name }}</span>
                <span class="option-desc">{{ cat.description }}</span>
              </el-option>
            </el-select>

            <el-select
              v-model="selectedSubtype"
              placeholder="选择子类型"
              clearable
              :disabled="!selectedCategory || subtypeOptions.length === 0"
              class="subtype-select"
            >
              <el-option
                v-for="sub in subtypeOptions"
                :key="sub.id"
                :label="sub.name"
                :value="sub.id"
              >
                <span>{{ sub.name }}</span>
                <span class="option-desc">{{ sub.description }}</span>
              </el-option>
            </el-select>
          </div>
        </div>

        <!-- 输入方式和内容 -->
        <div class="input-section">
          <div class="mode-tabs">
            <el-radio-group v-model="inputMode" size="default">
              <el-radio-button value="text">
                <el-icon><Document /></el-icon>
                直接粘贴
              </el-radio-button>
              <el-radio-button value="file">
                <el-icon><Upload /></el-icon>
                文件上传
              </el-radio-button>
            </el-radio-group>
          </div>

          <!-- 文本输入 -->
          <div class="input-area" v-if="inputMode === 'text'">
            <el-input
              v-model="textContent"
              type="textarea"
              :rows="6"
              placeholder="请输入或粘贴需求文档内容..."
              class="text-input"
            />
          </div>

          <!-- 文件上传 -->
          <div class="upload-area" v-else>
            <el-upload
              ref="uploadRef"
              v-model:file-list="fileList"
              :auto-upload="false"
              :limit="1"
              :on-exceed="handleExceed"
              :before-upload="handleBeforeUpload"
              :on-change="handleChange"
              :on-remove="handleRemove"
              accept=".docx,.txt"
              drag
              class="upload-drag"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">支持 .docx 和 .txt 格式</div>
              </template>
            </el-upload>
          </div>

          <!-- 提交按钮 -->
          <div class="submit-row">
            <el-button
              type="primary"
              :loading="uploadLoading"
              @click="handleReview"
              size="large"
            >
              <el-icon v-if="!uploadLoading"><MagicStick /></el-icon>
              {{ uploadLoading ? '审查中...' : '开始审查' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 审查结果 - 主内容区 -->
    <div class="result-main" v-if="reviewResult">
      <!-- 评分概览卡片 -->
      <div class="score-overview">
        <div class="score-left">
          <div class="score-circle" :style="{
            borderColor: getScoreColor(reviewResult.completeness_score),
            background: `conic-gradient(${getScoreColor(reviewResult.completeness_score)} ${reviewResult.completeness_score * 3.6}deg, rgba(255,255,255,0.1) 0deg)`
          }">
            <div class="score-inner">
              <div class="score-value" :style="{ color: getScoreColor(reviewResult.completeness_score) }">
                {{ Math.round(reviewResult.completeness_score) }}
              </div>
              <div class="score-label">完整度评分</div>
            </div>
          </div>
          <div class="score-info">
            <div class="score-status" :style="{ color: getScoreColor(reviewResult.completeness_score) }">
              {{ getScoreStatus(reviewResult.completeness_score) }}
            </div>
            <div class="category-tags" v-if="reviewResult.category_id">
              <el-tag type="primary" effect="dark">
                {{ categories.find(c => c.id === reviewResult.category_id)?.name || reviewResult.category_id }}
              </el-tag>
              <el-tag v-if="reviewResult.subtype_id" type="success" effect="dark">
                {{ subtypeOptions.find(s => s.id === reviewResult.subtype_id)?.name || reviewResult.subtype_id }}
              </el-tag>
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

      <!-- 主要内容区域 -->
      <div class="result-content">
        <!-- 左侧：提取的字段 -->
        <div class="result-section fields-section">
          <div class="section-header">
            <el-icon><List /></el-icon>
            <span>提取的字段</span>
            <el-tag size="small" type="info">{{ reviewResult.field_count }} 项</el-tag>
          </div>
          <div class="fields-grid">
            <div
              class="field-card"
              v-for="(field, fieldId) in groupedFields"
              :key="fieldId"
            >
              <div class="field-header">
                <span class="field-label">{{ field.label }}</span>
                <el-tag
                  size="small"
                  :type="field.confidence >= 0.8 ? 'success' : field.confidence >= 0.5 ? 'warning' : 'danger'"
                  effect="plain"
                >
                  {{ Math.round(field.confidence * 100) }}%
                </el-tag>
              </div>
              <div class="field-value">{{ formatFieldValue(field.value) }}</div>
            </div>
          </div>
        </div>

        <!-- 右侧：问题和建议 -->
        <div class="result-section issues-section">
          <!-- 修改建议 -->
          <div class="suggestions-box" v-if="reviewResult.suggestions?.length">
            <div class="box-header">
              <el-icon><ChatLineRound /></el-icon>
              <span>修改建议</span>
            </div>
            <div class="suggestions-list">
              <div class="suggestion-item" v-for="(suggestion, index) in reviewResult.suggestions" :key="index">
                <el-icon class="suggestion-icon"><CircleCheck /></el-icon>
                <span>{{ suggestion }}</span>
              </div>
            </div>
          </div>

          <!-- 问题清单 -->
          <div class="issues-box">
            <div class="box-header">
              <el-icon><Warning /></el-icon>
              <span>问题清单</span>
              <el-tag size="small" :type="reviewResult.error_count > 0 ? 'danger' : 'success'">
                {{ reviewResult.issue_count }} 项
              </el-tag>
            </div>

            <el-tabs class="issues-tabs">
              <el-tab-pane :label="`错误 (${groupedIssues.errors.length})`" name="errors">
                <div class="issues-list" v-if="groupedIssues.errors.length">
                  <div
                    class="issue-item error"
                    v-for="(issue, index) in groupedIssues.errors"
                    :key="index"
                    @click="showIssueDetail(issue)"
                  >
                    <div class="issue-icon"><el-icon><CircleClose /></el-icon></div>
                    <div class="issue-content">
                      <div class="issue-message">{{ issue.message }}</div>
                      <div class="issue-suggestion">{{ issue.suggestion }}</div>
                    </div>
                    <el-icon class="issue-arrow"><ArrowRight /></el-icon>
                  </div>
                </div>
                <el-empty v-else description="没有错误" :image-size="60" />
              </el-tab-pane>

              <el-tab-pane :label="`警告 (${groupedIssues.warnings.length})`" name="warnings">
                <div class="issues-list" v-if="groupedIssues.warnings.length">
                  <div
                    class="issue-item warning"
                    v-for="(issue, index) in groupedIssues.warnings"
                    :key="index"
                    @click="showIssueDetail(issue)"
                  >
                    <div class="issue-icon"><el-icon><Warning /></el-icon></div>
                    <div class="issue-content">
                      <div class="issue-message">{{ issue.message }}</div>
                      <div class="issue-suggestion">{{ issue.suggestion }}</div>
                    </div>
                    <el-icon class="issue-arrow"><ArrowRight /></el-icon>
                  </div>
                </div>
                <el-empty v-else description="没有警告" :image-size="60" />
              </el-tab-pane>

              <el-tab-pane :label="`提示 (${groupedIssues.infos.length})`" name="infos">
                <div class="issues-list" v-if="groupedIssues.infos.length">
                  <div
                    class="issue-item info"
                    v-for="(issue, index) in groupedIssues.infos"
                    :key="index"
                    @click="showIssueDetail(issue)"
                  >
                    <div class="issue-icon"><el-icon><InfoFilled /></el-icon></div>
                    <div class="issue-content">
                      <div class="issue-message">{{ issue.message }}</div>
                      <div class="issue-suggestion">{{ issue.suggestion }}</div>
                    </div>
                    <el-icon class="issue-arrow"><ArrowRight /></el-icon>
                  </div>
                </div>
                <el-empty v-else description="没有提示" :image-size="60" />
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- 风险摘要 -->
          <div class="risk-box" v-if="reviewResult.risk_summary?.total > 0">
            <div class="box-header">
              <el-icon><WarnTriangleFilled /></el-icon>
              <span>风险检测</span>
              <el-tag size="small" :type="reviewResult.risk_summary.P0_count > 0 ? 'danger' : 'warning'">
                {{ reviewResult.risk_summary.total }} 项风险
              </el-tag>
            </div>
            <div class="risk-summary">
              <div class="risk-item" v-if="reviewResult.risk_summary.P0_count">
                <span class="risk-level p0">P0 高风险</span>
                <span class="risk-count">{{ reviewResult.risk_summary.P0_count }} 项</span>
              </div>
              <div class="risk-item" v-if="reviewResult.risk_summary.P1_count">
                <span class="risk-level p1">P1 中风险</span>
                <span class="risk-count">{{ reviewResult.risk_summary.P1_count }} 项</span>
              </div>
              <div class="risk-item" v-if="reviewResult.risk_summary.P2_count">
                <span class="risk-level p2">P2 低风险</span>
                <span class="risk-count">{{ reviewResult.risk_summary.P2_count }} 项</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else-if="!showInputPanel">
      <el-icon class="empty-icon"><Document /></el-icon>
      <p>请输入或上传需求文档开始审查</p>
    </div>

    <!-- 问题详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="问题详情" width="500px" class="issue-dialog">
      <div v-if="currentIssue" class="issue-detail">
        <div class="detail-row">
          <span class="label">严重程度:</span>
          <el-tag :type="getLevelType(currentIssue.level)" size="small">
            {{ getLevelText(currentIssue.level) }}
          </el-tag>
        </div>
        <div class="detail-row">
          <span class="label">问题描述:</span>
          <div class="value">{{ currentIssue.message }}</div>
        </div>
        <div class="detail-row">
          <span class="label">修改建议:</span>
          <div class="value suggestion">{{ currentIssue.suggestion }}</div>
        </div>
        <div class="detail-row" v-if="currentIssue.keyword">
          <span class="label">关键词:</span>
          <el-tag type="warning" size="small">{{ currentIssue.keyword }}</el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.requirements-container {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  color: #ffffff;
  font-size: 28px;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.page-header p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0;
}

/* 输入面板 */
.input-panel {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.input-panel.collapsed {
  background: rgba(255, 255, 255, 0.03);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background 0.2s;
}

.panel-header:hover {
  background: rgba(255, 255, 255, 0.03);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-icon {
  color: rgba(255, 255, 255, 0.5);
  transition: transform 0.3s;
}

.toggle-icon.rotated {
  transform: rotate(-90deg);
}

.panel-title {
  color: #ffffff;
  font-size: 15px;
  font-weight: 500;
}

.panel-content {
  padding: 16px;
}

/* 品类选择 */
.category-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.category-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  white-space: nowrap;
}

.category-selectors {
  display: flex;
  gap: 12px;
  flex: 1;
}

.category-select, .subtype-select {
  flex: 1;
  max-width: 200px;
}

.option-desc {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-left: 8px;
}

/* 输入区域 */
.input-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mode-tabs :deep(.el-radio-group) {
  display: flex;
}

.mode-tabs :deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
}

.text-input :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ffffff;
  font-size: 14px;
  line-height: 1.6;
}

.text-input :deep(.el-textarea__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.text-input :deep(.el-textarea__inner:focus) {
  border-color: #409EFF;
}

.upload-drag {
  border: 2px dashed rgba(64, 158, 255, 0.3);
  border-radius: 8px;
}

.upload-drag :deep(.el-upload-dragger) {
  padding: 30px 20px;
  background: transparent;
  border: none;
}

.upload-drag :deep(.el-icon--upload) {
  font-size: 36px;
  color: #409EFF;
}

.upload-drag :deep(.el-upload__text) {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.upload-drag :deep(.el-upload__text em) {
  color: #409EFF;
}

.upload-drag :deep(.el-upload__tip) {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
}

.submit-row {
  display: flex;
  justify-content: flex-end;
}

.submit-row .el-button {
  padding: 10px 32px;
  font-size: 15px;
  border-radius: 8px;
}

/* 结果主区域 */
.result-main {
  animation: slideIn 0.4s ease;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 评分概览 */
.score-overview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
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
  color: rgba(255, 255, 255, 0.5);
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
  background: rgba(255, 255, 255, 0.03);
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

.stat-item.error .stat-icon { background: rgba(245, 108, 108, 0.15); color: #F56C6C; }
.stat-item.warning .stat-icon { background: rgba(230, 162, 60, 0.15); color: #E6A23C; }
.stat-item.info .stat-icon { background: rgba(64, 158, 255, 0.15); color: #409EFF; }
.stat-item.fields .stat-icon { background: rgba(103, 194, 58, 0.15); color: #67C23A; }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* 结果内容区 */
.result-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.result-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-size: 15px;
  font-weight: 500;
}

.section-header .el-icon {
  color: #409EFF;
}

/* 字段网格 */
.fields-section {
  max-height: 600px;
  display: flex;
  flex-direction: column;
}

.fields-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 12px;
  overflow-y: auto;
  flex: 1;
}

.field-card {
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border-left: 3px solid #409EFF;
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.field-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-weight: 500;
}

.field-value {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  word-break: break-all;
  line-height: 1.4;
}

/* 问题区域 */
.issues-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  max-height: 600px;
  overflow-y: auto;
}

.suggestions-box, .issues-box, .risk-box {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  overflow: hidden;
}

.box-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.02);
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
}

.box-header .el-icon {
  color: #409EFF;
}

.suggestions-list {
  padding: 8px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px;
  background: rgba(103, 194, 58, 0.08);
  border-radius: 6px;
  margin-bottom: 6px;
}

.suggestion-icon {
  color: #67C23A;
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}

.suggestion-item span {
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  line-height: 1.5;
}

/* 问题标签页 */
.issues-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 12px;
  background: rgba(255, 255, 255, 0.02);
}

.issues-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.issues-tabs :deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

.issues-tabs :deep(.el-tabs__item.is-active) {
  color: #409EFF;
}

.issues-list {
  padding: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.issue-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  margin-bottom: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.issue-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.issue-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.issue-item.error .issue-icon { background: rgba(245, 108, 108, 0.15); color: #F56C6C; }
.issue-item.warning .issue-icon { background: rgba(230, 162, 60, 0.15); color: #E6A23C; }
.issue-item.info .issue-icon { background: rgba(64, 158, 255, 0.15); color: #409EFF; }

.issue-content {
  flex: 1;
  min-width: 0;
}

.issue-message {
  color: #ffffff;
  font-size: 13px;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.issue-suggestion {
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.issue-arrow {
  color: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

/* 风险摘要 */
.risk-summary {
  padding: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.risk-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
}

.risk-level {
  font-size: 12px;
  font-weight: 500;
}

.risk-level.p0 { color: #F56C6C; }
.risk-level.p1 { color: #E6A23C; }
.risk-level.p2 { color: #409EFF; }

.risk-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.4);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

/* 问题详情弹窗 */
.issue-detail {
  padding: 8px;
}

.detail-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: flex-start;
}

.detail-row .label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  min-width: 70px;
}

.detail-row .value {
  flex: 1;
  color: #ffffff;
  font-size: 13px;
  line-height: 1.6;
}

.detail-row .value.suggestion {
  color: #67C23A;
}

:deep(.el-dialog) {
  background: rgba(26, 26, 46, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

:deep(.el-dialog__header) {
  color: #ffffff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding: 16px 20px;
  margin: 0;
}

:deep(.el-dialog__title) {
  color: #ffffff;
  font-weight: 500;
}

:deep(.el-dialog__body) {
  color: #ffffff;
  padding: 20px;
}

:deep(.el-dialog__close) {
  color: rgba(255, 255, 255, 0.5);
}

:deep(.el-dialog__close:hover) {
  color: #ffffff;
}

:deep(.el-empty__description) {
  color: rgba(255, 255, 255, 0.4);
}

/* 响应式 */
@media (max-width: 1200px) {
  .result-content {
    grid-template-columns: 1fr;
  }

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

  .fields-grid {
    grid-template-columns: 1fr;
  }
}
</style>
