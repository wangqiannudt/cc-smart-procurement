<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const uploadRef = ref()
const uploadLoading = ref(false)
const analysisResult = ref(null)
const dialogVisible = ref(false)
const currentRisk = ref(null)
const inputMode = ref('text') // 'text' or 'file'
const textContent = ref('')
const showInputPanel = ref(true) // 控制输入面板的展开/收起

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
  showInputPanel.value = true
}

const handleModeChange = (mode) => {
  inputMode.value = mode
  fileList.value = []
  textContent.value = ''
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
      showInputPanel.value = false // 收起输入面板
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

const handleNewAnalysis = () => {
  analysisResult.value = null
  fileList.value = []
  textContent.value = ''
  showInputPanel.value = true
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

// 按风险等级分组
const groupedRisks = computed(() => {
  if (!analysisResult.value?.risks) return { high: [], medium: [], low: [] }
  return {
    high: analysisResult.value.risks.filter(r => r.level === '高风险'),
    medium: analysisResult.value.risks.filter(r => r.level === '中风险'),
    low: analysisResult.value.risks.filter(r => r.level === '需特别关注')
  }
})

// 找到的要素
const foundElements = computed(() => {
  if (!analysisResult.value?.elements) return []
  return Object.entries(analysisResult.value.elements)
    .filter(([_, element]) => element.found)
    .map(([key, element]) => ({ name: key, ...element }))
})

// 缺失的要素
const missingElements = computed(() => {
  if (!analysisResult.value?.elements) return []
  return Object.entries(analysisResult.value?.elements)
    .filter(([_, element]) => !element.found)
    .map(([key, element]) => ({ name: key, ...element }))
})
</script>

<template>
  <div class="contract-container">
    <div class="page-header">
      <h1>合同要素识别与风险提示</h1>
      <p>智能分析合同文档，识别关键要素和潜在风险</p>
    </div>

    <!-- 输入面板 - 可折叠 -->
    <div class="input-panel" :class="{ 'collapsed': !showInputPanel && analysisResult }">
      <div class="panel-header" @click="showInputPanel = !showInputPanel">
        <div class="header-left">
          <el-icon class="toggle-icon" :class="{ 'rotated': !showInputPanel }"><ArrowDown /></el-icon>
          <span class="panel-title">
            {{ analysisResult ? '重新输入合同' : '输入合同文档' }}
          </span>
          <template v-if="analysisResult">
            <el-tag :type="getOverallRiskType(analysisResult.risk_level)" size="small" style="margin-left: 12px;">
              {{ analysisResult.risk_level }}
            </el-tag>
          </template>
        </div>
        <div class="header-right" v-if="analysisResult">
          <el-button type="primary" size="small" @click.stop="handleNewAnalysis">
            <el-icon><Plus /></el-icon>
            新建分析
          </el-button>
        </div>
      </div>

      <div class="panel-content" v-show="showInputPanel || !analysisResult">
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
              placeholder="请输入或粘贴合同文档内容..."
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
              @click="handleAnalyze"
              size="large"
            >
              <el-icon v-if="!uploadLoading"><MagicStick /></el-icon>
              {{ uploadLoading ? '分析中...' : '开始分析' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分析结果 - 主内容区 -->
    <div class="result-main" v-if="analysisResult">
      <!-- 风险概览卡片 -->
      <div class="risk-overview-card">
        <div class="risk-left">
          <div class="risk-badge-large" :style="{
            borderColor: getOverallRiskColor(analysisResult.risk_level),
            background: `conic-gradient(${getOverallRiskColor(analysisResult.risk_level)} ${(100 - analysisResult.completeness) * 3.6}deg, rgba(255,255,255,0.1) 0deg)`
          }">
            <div class="risk-badge-inner">
              <div class="risk-level-text" :style="{ color: getOverallRiskColor(analysisResult.risk_level) }">
                {{ analysisResult.risk_level }}
              </div>
              <div class="risk-level-label">风险评估</div>
            </div>
          </div>
          <div class="risk-info">
            <div class="completeness-value" :style="{ color: getOverallRiskColor(analysisResult.risk_level) }">
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
                <div class="stat-value">{{ foundElements.length }}</div>
                <div class="stat-label">已识别要素</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="result-content">
        <!-- 左侧：合同要素 -->
        <div class="result-section elements-section">
          <div class="section-header">
            <el-icon><List /></el-icon>
            <span>合同要素</span>
            <el-tag size="small" type="info">{{ foundElements.length }}/{{ foundElements.length + missingElements.length }}</el-tag>
          </div>
          <div class="elements-content">
            <!-- 已识别要素 -->
            <div class="element-group" v-if="foundElements.length">
              <div class="group-title">
                <el-icon color="#67C23A"><CircleCheck /></el-icon>
                <span>已识别要素</span>
              </div>
              <div class="elements-grid">
                <div
                  class="element-card found"
                  v-for="(element, index) in foundElements"
                  :key="index"
                >
                  <div class="element-name">{{ element.name }}</div>
                  <div class="element-keywords" v-if="element.keywords?.length">
                    <el-tag
                      v-for="kw in element.keywords.slice(0, 2)"
                      :key="kw"
                      size="small"
                      type="success"
                      effect="plain"
                    >
                      {{ kw }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
            <!-- 缺失要素 -->
            <div class="element-group" v-if="missingElements.length">
              <div class="group-title">
                <el-icon color="#F56C6C"><CircleClose /></el-icon>
                <span>缺失要素</span>
              </div>
              <div class="elements-grid">
                <div
                  class="element-card missing"
                  v-for="(element, index) in missingElements"
                  :key="index"
                >
                  <div class="element-name">{{ element.name }}</div>
                  <div class="element-status">未识别</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：风险和建议 -->
        <div class="result-section issues-section">
          <!-- 修改建议 -->
          <div class="suggestions-box" v-if="analysisResult.suggestions?.length">
            <div class="box-header">
              <el-icon><ChatLineRound /></el-icon>
              <span>修改建议</span>
            </div>
            <div class="suggestions-list">
              <div class="suggestion-item" v-for="(suggestion, index) in analysisResult.suggestions" :key="index">
                <el-icon class="suggestion-icon"><CircleCheck /></el-icon>
                <span>{{ suggestion }}</span>
              </div>
            </div>
          </div>

          <!-- 风险条款 -->
          <div class="risks-box">
            <div class="box-header">
              <el-icon><Warning /></el-icon>
              <span>风险条款</span>
              <el-tag size="small" :type="analysisResult.risks?.length > 0 ? 'danger' : 'success'">
                {{ analysisResult.risks?.length || 0 }} 项
              </el-tag>
            </div>

            <el-tabs class="risks-tabs">
              <el-tab-pane :label="`高风险 (${groupedRisks.high.length})`" name="high">
                <div class="risks-list" v-if="groupedRisks.high.length">
                  <div
                    class="risk-item high"
                    v-for="(risk, index) in groupedRisks.high.slice(0, 10)"
                    :key="index"
                    @click="showRiskDetail(risk)"
                  >
                    <div class="risk-icon"><el-icon><WarnTriangleFilled /></el-icon></div>
                    <div class="risk-content">
                      <div class="risk-keyword">关键词: {{ risk.keyword }}</div>
                      <div class="risk-sentence">{{ risk.sentence }}</div>
                    </div>
                    <el-icon class="risk-arrow"><ArrowRight /></el-icon>
                  </div>
                </div>
                <el-empty v-else description="没有高风险条款" :image-size="60" />
              </el-tab-pane>

              <el-tab-pane :label="`中风险 (${groupedRisks.medium.length})`" name="medium">
                <div class="risks-list" v-if="groupedRisks.medium.length">
                  <div
                    class="risk-item medium"
                    v-for="(risk, index) in groupedRisks.medium.slice(0, 10)"
                    :key="index"
                    @click="showRiskDetail(risk)"
                  >
                    <div class="risk-icon"><el-icon><Warning /></el-icon></div>
                    <div class="risk-content">
                      <div class="risk-keyword">关键词: {{ risk.keyword }}</div>
                      <div class="risk-sentence">{{ risk.sentence }}</div>
                    </div>
                    <el-icon class="risk-arrow"><ArrowRight /></el-icon>
                  </div>
                </div>
                <el-empty v-else description="没有中风险条款" :image-size="60" />
              </el-tab-pane>

              <el-tab-pane :label="`需关注 (${groupedRisks.low.length})`" name="low">
                <div class="risks-list" v-if="groupedRisks.low.length">
                  <div
                    class="risk-item low"
                    v-for="(risk, index) in groupedRisks.low.slice(0, 10)"
                    :key="index"
                    @click="showRiskDetail(risk)"
                  >
                    <div class="risk-icon"><el-icon><InfoFilled /></el-icon></div>
                    <div class="risk-content">
                      <div class="risk-keyword">关键词: {{ risk.keyword }}</div>
                      <div class="risk-sentence">{{ risk.sentence }}</div>
                    </div>
                    <el-icon class="risk-arrow"><ArrowRight /></el-icon>
                  </div>
                </div>
                <el-empty v-else description="没有需关注条款" :image-size="60" />
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else-if="!showInputPanel">
      <el-icon class="empty-icon"><Document /></el-icon>
      <p>请输入或上传合同文档开始分析</p>
    </div>

    <!-- 风险详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="风险条款详情" width="550px" class="risk-dialog">
      <div v-if="currentRisk" class="risk-detail">
        <div class="detail-row">
          <span class="label">风险等级:</span>
          <el-tag :type="getRiskType(currentRisk.level)" size="small">{{ currentRisk.level }}</el-tag>
        </div>
        <div class="detail-row">
          <span class="label">关键词:</span>
          <el-tag type="warning" size="small">{{ currentRisk.keyword }}</el-tag>
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

/* 风险概览卡片 */
.risk-overview-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
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
  color: rgba(255, 255, 255, 0.5);
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
  color: rgba(255, 255, 255, 0.5);
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

.stat-item.high .stat-icon { background: rgba(245, 108, 108, 0.15); color: #F56C6C; }
.stat-item.medium .stat-icon { background: rgba(230, 162, 60, 0.15); color: #E6A23C; }
.stat-item.low .stat-icon { background: rgba(64, 158, 255, 0.15); color: #409EFF; }
.stat-item.elements .stat-icon { background: rgba(103, 194, 58, 0.15); color: #67C23A; }

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

/* 合同要素区域 */
.elements-section {
  max-height: 600px;
  display: flex;
  flex-direction: column;
}

.elements-content {
  padding: 12px;
  overflow-y: auto;
  flex: 1;
}

.element-group {
  margin-bottom: 16px;
}

.element-group:last-child {
  margin-bottom: 0;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  font-weight: 500;
}

.elements-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.element-card {
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border-left: 3px solid;
  transition: all 0.2s;
}

.element-card.found {
  border-color: #67C23A;
}

.element-card.missing {
  border-color: #F56C6C;
  opacity: 0.6;
}

.element-card:hover {
  background: rgba(255, 255, 255, 0.06);
}

.element-name {
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
}

.element-status {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
}

.element-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
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

.suggestions-box, .risks-box {
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

/* 风险标签页 */
.risks-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 12px;
  background: rgba(255, 255, 255, 0.02);
}

.risks-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.risks-tabs :deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

.risks-tabs :deep(.el-tabs__item.is-active) {
  color: #409EFF;
}

.risks-list {
  padding: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.risk-item {
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

.risk-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.risk-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.risk-item.high .risk-icon { background: rgba(245, 108, 108, 0.15); color: #F56C6C; }
.risk-item.medium .risk-icon { background: rgba(230, 162, 60, 0.15); color: #E6A23C; }
.risk-item.low .risk-icon { background: rgba(64, 158, 255, 0.15); color: #409EFF; }

.risk-content {
  flex: 1;
  min-width: 0;
}

.risk-keyword {
  color: #ffffff;
  font-size: 12px;
  margin-bottom: 2px;
}

.risk-sentence {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.risk-arrow {
  color: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
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

/* 风险详情弹窗 */
.risk-detail {
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
  .risk-overview-card {
    flex-direction: column;
    gap: 20px;
  }

  .risk-right {
    max-width: 100%;
    width: 100%;
  }

  .elements-grid {
    grid-template-columns: 1fr;
  }
}
</style>
