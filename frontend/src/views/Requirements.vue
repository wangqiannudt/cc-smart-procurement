<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const uploadRef = ref()
const uploadLoading = ref(false)
const reviewResult = ref(null)
const dialogVisible = ref(false)
const currentIssue = ref(null)
const inputMode = ref('text') // 'text' or 'file'
const textContent = ref('')

const uploadConfig = reactive({
  accept: '.docx,.txt',
  limit: 1,
  autoUpload: false,
  showFileList: true
})

const fileList = ref([])

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
}

const handleModeChange = (mode) => {
  inputMode.value = mode
  fileList.value = []
  textContent.value = ''
  reviewResult.value = null
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
      response = await axios.post('/api/review-requirements', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    } else {
      // Direct text input - create a blob from text
      const blob = new Blob([textContent.value], { type: 'text/plain' })
      const formData = new FormData()
      formData.append('file', blob, 'requirement.txt')
      response = await axios.post('/api/review-requirements', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }

    if (response.data.success) {
      reviewResult.value = response.data.data
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
</script>

<template>
  <div class="requirements-container">
    <div class="page-header">
      <h1>需求规范审查</h1>
      <p>智能分析需求文档，识别潜在问题并提供改进建议</p>
    </div>

    <div class="content-grid">
      <!-- Upload Section -->
      <div class="card upload-card">
        <div class="card-header">
          <h3>上传需求文档</h3>
          <el-icon><Upload /></el-icon>
        </div>

        <!-- Mode Toggle -->
        <div class="mode-toggle">
          <el-radio-group v-model="inputMode" size="large">
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

        <!-- Text Input Mode -->
        <div class="input-area" v-if="inputMode === 'text'">
          <el-input
            v-model="textContent"
            type="textarea"
            :rows="15"
            placeholder="请输入或粘贴需求文档内容..."
            class="text-input"
          />
        </div>

        <!-- File Upload Mode -->
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
              <div class="el-upload__tip">
                支持 .docx 和 .txt 格式
              </div>
            </template>
          </el-upload>
        </div>

        <div class="upload-actions">
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

      <!-- Result Section -->
      <div class="card result-card" v-if="reviewResult">
        <div class="card-header">
          <h3>审查结果</h3>
          <el-icon><DataAnalysis /></el-icon>
        </div>

        <!-- Score -->
        <div class="score-section">
          <div class="score-content">
            <div class="score-circle" :style="{ borderColor: getScoreColor(reviewResult.completeness_score) }">
              <div class="score-value" :style="{ color: getScoreColor(reviewResult.completeness_score) }">
                {{ reviewResult.completeness_score }}
              </div>
              <div class="score-label">完整度评分</div>
            </div>
          </div>
          <div class="score-stats">
            <div class="stat-item error">
              <div class="stat-value">{{ reviewResult.error_count }}</div>
              <div class="stat-label">错误</div>
            </div>
            <div class="stat-item warning">
              <div class="stat-value">{{ reviewResult.warning_count }}</div>
              <div class="stat-label">警告</div>
            </div>
            <div class="stat-item info">
              <div class="stat-value">{{ reviewResult.info_count }}</div>
              <div class="stat-label">提示</div>
            </div>
          </div>
        </div>

        <!-- Suggestions -->
        <div class="section-title">
          <el-icon><ChatLineRound /></el-icon>
          <span>修改建议</span>
        </div>
        <div class="suggestions-list">
          <div
            class="suggestion-item"
            v-for="(suggestion, index) in reviewResult.suggestions"
            :key="index"
          >
            <el-icon class="suggestion-icon"><CircleCheck /></el-icon>
            <span>{{ suggestion }}</span>
          </div>
        </div>

        <!-- Issues List -->
        <div class="section-title">
          <el-icon><List /></el-icon>
          <span>问题清单</span>
        </div>
        <div class="issues-list">
          <div
            class="issue-item"
            v-for="(issue, index) in reviewResult.issues"
            :key="index"
            @click="showIssueDetail(issue)"
          >
            <div class="issue-tag" :class="issue.level">
              {{ getLevelText(issue.level) }}
            </div>
            <div class="issue-content">
              <div class="issue-message">{{ issue.message }}</div>
              <div class="issue-suggestion">{{ issue.suggestion }}</div>
            </div>
            <el-icon class="issue-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- Issue Detail Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="问题详情"
      width="600px"
      class="issue-dialog"
    >
      <div v-if="currentIssue" class="issue-detail">
        <div class="detail-row">
          <span class="label">问题类型:</span>
          <el-tag :type="getLevelType(currentIssue.level)">{{ getLevelText(currentIssue.level) }}</el-tag>
        </div>
        <div class="detail-row">
          <span class="label">问题描述:</span>
          <div class="value">{{ currentIssue.message }}</div>
        </div>
        <div class="detail-row">
          <span class="label">修改建议:</span>
          <div class="value suggestion">{{ currentIssue.suggestion }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.requirements-container {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: #ffffff;
  font-size: 32px;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.page-header p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 15px;
  margin: 0;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 25px;
}

.card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header h3 {
  color: #ffffff;
  font-size: 18px;
  margin: 0;
  font-weight: 600;
}

.card-header .el-icon {
  color: #409EFF;
  font-size: 24px;
}

/* Mode Toggle */
.mode-toggle {
  margin-bottom: 20px;
}

.mode-toggle :deep(.el-radio-group) {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 6px;
}

.mode-toggle :deep(.el-radio-button) {
  padding: 12px 24px;
  border: none !important;
  background: transparent !important;
  color: rgba(255, 255, 255, 0.6);
  border-radius: 12px !important;
  transition: all 0.3s ease;
}

.mode-toggle :deep(.el-radio-button:hover) {
  background: rgba(64, 158, 255, 0.15) !important;
  color: rgba(255, 255, 255, 0.9);
}

.mode-toggle :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%) !important;
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.4);
}

.mode-toggle :deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
  gap: 6px;
}

.mode-toggle :deep(.el-icon) {
  font-size: 16px;
}

/* Text Input Area */
.input-area {
  margin-bottom: 20px;
}

.text-input :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #ffffff;
  font-size: 14px;
  line-height: 1.6;
  padding: 15px;
  resize: vertical;
}

.text-input :deep(.el-textarea__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.text-input :deep(.el-textarea__inner:focus) {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* Upload Card */
.upload-drag {
  border: 2px dashed rgba(64, 158, 255, 0.3);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.02);
}

.upload-drag :deep(.el-upload-dragger) {
  padding: 40px 20px;
  background: transparent;
  border: none;
}

.upload-drag :deep(.el-icon--upload) {
  font-size: 48px;
  color: #409EFF;
}

.upload-drag :deep(.el-upload__text) {
  color: rgba(255, 255, 255, 0.7);
}

.upload-drag :deep(.el-upload__text em) {
  color: #409EFF;
  font-style: normal;
}

.upload-drag :deep(.el-upload__tip) {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.upload-actions .el-button {
  padding: 14px 50px;
  font-size: 16px;
  border-radius: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 50%, #409EFF 100%) !important;
  border: none !important;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.upload-actions .el-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.upload-actions .el-button:hover::before {
  left: 100%;
}

.upload-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(64, 158, 255, 0.5);
}

.upload-actions .el-button:active {
  transform: translateY(0);
}

.upload-actions .el-button .el-icon {
  font-size: 18px;
}

/* Score Section */
.score-section {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 25px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  margin-bottom: 25px;
}

.score-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  border: 6px solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.5s ease;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin-top: 5px;
}

.score-stats {
  flex: 1;
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-item.error .stat-value {
  color: #F56C6C;
}

.stat-item.warning .stat-value {
  color: #E6A23C;
}

.stat-item.info .stat-value {
  color: #409EFF;
}

.stat-item .stat-value {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-item .stat-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

/* Section Title */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  margin: 25px 0 15px 0;
}

.section-title .el-icon {
  color: #409EFF;
  font-size: 20px;
}

/* Suggestions List */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background: rgba(103, 194, 58, 0.1);
  border-radius: 10px;
  border-left: 3px solid #67C23A;
  transition: all 0.3s ease;
}

.suggestion-item:hover {
  background: rgba(103, 194, 58, 0.15);
  transform: translateX(5px);
}

.suggestion-icon {
  color: #67C23A;
  font-size: 18px;
  flex-shrink: 0;
}

.suggestion-item span {
  color: #ffffff;
  font-size: 14px;
}

/* Issues List */
.issues-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
}

.issue-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.issue-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(5px);
}

.issue-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
  width: 50px;
  text-align: center;
}

.issue-tag.error {
  background: rgba(245, 108, 108, 0.2);
  color: #F56C6C;
}

.issue-tag.warning {
  background: rgba(230, 162, 60, 0.2);
  color: #E6A23C;
}

.issue-tag.info {
  background: rgba(64, 158, 255, 0.2);
  color: #409EFF;
}

.issue-content {
  flex: 1;
}

.issue-message {
  color: #ffffff;
  font-size: 14px;
  margin-bottom: 5px;
}

.issue-suggestion {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

.issue-arrow {
  color: rgba(255, 255, 255, 0.3);
  font-size: 18px;
  flex-shrink: 0;
}

/* Issue Dialog */
.issue-detail {
  padding: 10px;
}

.detail-row {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.detail-row .label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  font-weight: 500;
  min-width: 80px;
}

.detail-row .value {
  flex: 1;
  color: #ffffff;
  font-size: 14px;
  line-height: 1.6;
}

.detail-row .value.suggestion {
  color: #67C23A;
}

:deep(.el-dialog) {
  background: rgba(26, 26, 46, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

:deep(.el-dialog__header) {
  color: #ffffff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-dialog__title) {
  color: #ffffff;
}

:deep(.el-dialog__body) {
  color: #ffffff;
}

:deep(.el-dialog__close) {
  color: rgba(255, 255, 255, 0.6);
}

:deep(.el-dialog__close:hover) {
  color: #ffffff;
}
</style>