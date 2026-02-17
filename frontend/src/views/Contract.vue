<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const uploadRef = ref()
const uploadLoading = ref(false)
const analysisResult = ref(null)
const dialogVisible = ref(false)
const currentRisk = ref(null)
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
  analysisResult.value = null
}

const handleModeChange = (mode) => {
  inputMode.value = mode
  fileList.value = []
  textContent.value = ''
  analysisResult.value = null
}

const handleAnalyze = async () => {
  if (inputMode.value === 'file') {
    if (fileList.value.length === 0) {
      ElMessage.warning('请先上传文件')
      return
    }
  } else {
    if (!textContent.value.trim()) {
      ElMessage.warning('请输入合同内容')
      return
    }
  }

  uploadLoading.value = true

  try {
    let response
    if (inputMode.value === 'file') {
      const formData = new FormData()
      formData.append('file', fileList.value[0].raw)
      response = await axios.post('/api/contract-analysis', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    } else {
      // Direct text input - create a blob from text
      const blob = new Blob([textContent.value], { type: 'text/plain' })
      const formData = new FormData()
      formData.append('file', blob, 'contract.txt')
      response = await axios.post('/api/contract-analysis', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }

    if (response.data.success) {
      analysisResult.value = response.data.data
      ElMessage.success('分析完成')
    } else {
      ElMessage.error('分析失败: ' + response.data.error)
    }
  } catch (error) {
    ElMessage.error('分析失败: ' + error.message)
  } finally {
    uploadLoading.value = false
  }
}

const showRiskDetail = (risk) => {
  currentRisk.value = risk
  dialogVisible.value = true
}

const getRiskType = (level) => {
  const types = {
    '高风险': 'danger',
    '中风险': 'warning',
    '需特别关注': 'info'
  }
  return types[level] || 'info'
}

const getRiskColor = (level) => {
  const colors = {
    '高风险': '#F56C6C',
    '中风险': '#E6A23C',
    '需特别关注': '#409EFF'
  }
  return colors[level] || '#909399'
}

const getOverallRiskColor = (level) => {
  const colors = {
    '高风险': '#F56C6C',
    '中风险': '#E6A23C',
    '低风险': '#67C23A',
    '风险可控': '#67C23A'
  }
  return colors[level] || '#409EFF'
}

const getOverallRiskType = (level) => {
  const types = {
    '高风险': 'danger',
    '中风险': 'warning',
    '低风险': 'success',
    '风险可控': 'success'
  }
  return types[level] || 'info'
}
</script>

<template>
  <div class="contract-container">
    <div class="page-header">
      <h1>合同要素识别与风险提示</h1>
      <p>智能分析合同文档，识别关键要素和潜在风险</p>
    </div>

    <div class="content-grid">
      <!-- Upload Section -->
      <div class="card upload-card">
        <div class="card-header">
          <h3>上传合同文档</h3>
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
            placeholder="请输入或粘贴合同文档内容..."
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
            @click="handleAnalyze"
            size="large"
          >
            <el-icon v-if="!uploadLoading"><MagicStick /></el-icon>
            {{ uploadLoading ? '分析中...' : '开始分析' }}
          </el-button>
        </div>
      </div>

      <!-- Result Section -->
      <div class="card result-card" v-if="analysisResult">
        <div class="card-header">
          <h3>分析结果</h3>
          <el-icon><DocumentChecked /></el-icon>
        </div>

        <!-- Overall Risk Assessment -->
        <div class="risk-assessment">
          <div class="risk-overview">
            <div class="risk-badge" :style="{ backgroundColor: getOverallRiskColor(analysisResult.risk_level) + '33', color: getOverallRiskColor(analysisResult.risk_level) }">
              {{ analysisResult.risk_level }}
            </div>
            <div class="risk-info">
              <div class="risk-title">整体风险评估</div>
              <div class="risk-desc">基于合同条款内容分析得出</div>
            </div>
          </div>
          <div class="risk-summary">
            <div class="summary-item" :class="'high'">
              <div class="summary-value">{{ analysisResult.risk_summary['高风险'] || 0 }}</div>
              <div class="summary-label">高风险</div>
            </div>
            <div class="summary-item" :class="'medium'">
              <div class="summary-value">{{ analysisResult.risk_summary['中风险'] || 0 }}</div>
              <div class="summary-label">中风险</div>
            </div>
            <div class="summary-item" :class="'low'">
              <div class="summary-value">{{ analysisResult.risk_summary['需特别关注'] || 0 }}</div>
              <div class="summary-label">需关注</div>
            </div>
          </div>
        </div>

        <!-- Contract Elements -->
        <div class="section-title">
          <el-icon><List /></el-icon>
          <span>合同要素</span>
          <span class="completeness">完整度: {{ analysisResult.completeness }}%</span>
        </div>
        <div class="elements-grid">
          <div
            v-for="(element, key) in analysisResult.elements"
            :key="key"
            class="element-card"
            :class="{ found: element.found }"
          >
            <div class="element-status">
              <el-icon v-if="element.found" color="#67C23A"><CircleCheck /></el-icon>
              <el-icon v-else color="#F56C6C"><CircleClose /></el-icon>
            </div>
            <div class="element-name">{{ key }}</div>
            <div class="element-keywords" v-if="element.found && element.keywords.length">
              <el-tag
                v-for="kw in element.keywords.slice(0, 2)"
                :key="kw"
                size="small"
                type="info"
              >
                {{ kw }}
              </el-tag>
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
            v-for="(suggestion, index) in analysisResult.suggestions"
            :key="index"
          >
            <el-icon class="suggestion-icon"><CircleCheck /></el-icon>
            <span>{{ suggestion }}</span>
          </div>
        </div>

        <!-- Risk List -->
        <div class="section-title" v-if="analysisResult.risks.length > 0">
          <el-icon><Warning /></el-icon>
          <span>风险条款</span>
        </div>
        <div class="risks-list" v-if="analysisResult.risks.length > 0">
          <div
            class="risk-item"
            v-for="(risk, index) in analysisResult.risks.slice(0, 10)"
            :key="index"
            @click="showRiskDetail(risk)"
          >
            <div class="risk-level-badge" :style="{ backgroundColor: getRiskColor(risk.level) + '33', color: getRiskColor(risk.level) }">
              {{ risk.level }}
            </div>
            <div class="risk-content">
              <div class="risk-keyword">关键词: {{ risk.keyword }}</div>
              <div class="risk-sentence">{{ risk.sentence }}</div>
            </div>
            <el-icon class="risk-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- Risk Detail Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="风险条款详情"
      width="600px"
      class="risk-dialog"
    >
      <div v-if="currentRisk" class="risk-detail">
        <div class="detail-row">
          <span class="label">风险等级:</span>
          <el-tag :type="getRiskType(currentRisk.level)">{{ currentRisk.level }}</el-tag>
        </div>
        <div class="detail-row">
          <span class="label">关键词:</span>
          <div class="value">{{ currentRisk.keyword }}</div>
        </div>
        <div class="detail-row">
          <span class="label">条款内容:</span>
          <div class="value quote">{{ currentRisk.sentence }}</div>
        </div>
        <div class="detail-row">
          <span class="label">修改建议:</span>
          <div class="value suggestion">{{ currentRisk.suggestion }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.contract-container {
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

/* Risk Assessment */
.risk-assessment {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
}

.risk-overview {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.risk-badge {
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 700;
  text-align: center;
  min-width: 120px;
}

.risk-info {
  flex: 1;
}

.risk-title {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 5px;
}

.risk-desc {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.risk-summary {
  display: flex;
  justify-content: space-around;
}

.summary-item {
  text-align: center;
}

.summary-item.high .summary-value {
  color: #F56C6C;
}

.summary-item.medium .summary-value {
  color: #E6A23C;
}

.summary-item.low .summary-value {
  color: #409EFF;
}

.summary-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 5px;
}

.summary-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
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

.completeness {
  margin-left: auto;
  color: #67C23A;
  font-size: 14px;
  font-weight: 500;
}

/* Elements Grid */
.elements-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.element-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 15px;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.element-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-3px);
}

.element-card.found {
  border-color: rgba(103, 194, 58, 0.3);
}

.element-status {
  margin-bottom: 8px;
}

.element-name {
  color: #ffffff;
  font-size: 13px;
  margin-bottom: 8px;
  font-weight: 500;
}

.element-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
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

/* Risks List */
.risks-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
}

.risk-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.risk-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(5px);
}

.risk-level-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
  text-align: center;
  min-width: 70px;
}

.risk-content {
  flex: 1;
}

.risk-keyword {
  color: #ffffff;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 5px;
}

.risk-sentence {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.risk-arrow {
  color: rgba(255, 255, 255, 0.3);
  font-size: 18px;
  flex-shrink: 0;
}

/* Risk Dialog */
.risk-detail {
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

.detail-row .value.quote {
  background: rgba(255, 255, 255, 0.05);
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid #409EFF;
  font-style: italic;
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