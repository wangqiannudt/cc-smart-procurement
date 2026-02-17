<script setup>
import { ref, onMounted } from 'vue'
import { useChat } from '../composables'

const inputMessage = ref('')

// 使用 composable
const {
  messages,
  loading,
  messagesContainer,
  formatContent,
  initSession,
  sendMessage: sendChatMessage,
  clearChat
} = useChat()

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message) return
  inputMessage.value = ''
  await sendChatMessage(message)
}

// 快捷操作
const quickActions = [
  { label: '价格查询', message: '我想了解价格查询功能' },
  { label: '需求审查', message: '需求审查怎么做' },
  { label: '合同分析', message: '合同分析功能介绍' },
  { label: '服务器选型', message: '服务器选型建议' }
]

const sendQuickAction = (message) => {
  inputMessage.value = message
  sendMessage()
}

onMounted(() => {
  initSession()
})
</script>

<template>
  <div class="chat-container">
    <!-- Header -->
    <div class="chat-header">
      <div class="header-info">
        <h2>AI智能助手</h2>
        <p>采购问题咨询 · 需求分析 · 方案建议</p>
      </div>
      <el-button @click="clearChat" type="default" size="small">
        <el-icon><RefreshRight /></el-icon>
        新对话
      </el-button>
    </div>

    <!-- Messages Area -->
    <div class="messages-area" ref="messagesContainer">
      <div class="messages-wrapper">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message"
          :class="msg.role"
        >
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'user'" :size="24"><User /></el-icon>
            <el-icon v-else :size="24"><Service /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-sender">{{ msg.role === 'user' ? '我' : 'AI助手' }}</span>
              <span class="message-time">{{ msg.time }}</span>
            </div>
            <div class="message-text" v-html="formatContent(msg.content)"></div>

            <!-- Suggested Actions -->
            <div v-if="msg.actions && msg.actions.length > 0" class="suggested-actions">
              <el-button
                v-for="(action, actionIndex) in msg.actions"
                :key="actionIndex"
                size="small"
                type="primary"
                plain
                @click="sendQuickAction(action.label)"
              >
                {{ action.label }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- Loading Indicator -->
        <div v-if="loading" class="message assistant">
          <div class="message-avatar">
            <el-icon :size="24"><Service /></el-icon>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <el-button
        v-for="(action, index) in quickActions"
        :key="index"
        size="small"
        round
        @click="sendQuickAction(action.message)"
      >
        {{ action.label }}
      </el-button>
    </div>

    <!-- Input Area -->
    <div class="input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="2"
        placeholder="输入您的问题，按 Enter 发送..."
        @keydown.enter.exact.prevent="sendMessage"
        :disabled="loading"
      />
      <el-button
        type="primary"
        :loading="loading"
        @click="sendMessage"
        :disabled="!inputMessage.trim()"
      >
        <el-icon><Promotion /></el-icon>
        发送
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(64, 158, 255, 0.05);
  border-radius: 16px 16px 0 0;
}

.header-info h2 {
  color: #ffffff;
  font-size: 22px;
  margin: 0 0 5px 0;
  font-weight: 600;
}

.header-info p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  margin: 0;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.messages-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  color: white;
}

.message.assistant .message-avatar {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
  color: white;
}

.message-content {
  max-width: 70%;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 15px 18px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.message.user .message-content {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2) 0%, rgba(64, 158, 255, 0.1) 100%);
  border-color: rgba(64, 158, 255, 0.3);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-sender {
  color: #409EFF;
  font-size: 13px;
  font-weight: 600;
}

.message-time {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
}

.message-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  line-height: 1.6;
}

.message-text :deep(strong) {
  color: #409EFF;
  font-weight: 600;
}

.suggested-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 5px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #409EFF;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

/* Quick Actions */
.quick-actions {
  display: flex;
  gap: 10px;
  padding: 15px 25px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  overflow-x: auto;
  justify-content: center;
  flex-wrap: wrap;
}

.quick-actions .el-button {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.quick-actions .el-button:hover {
  background: rgba(64, 158, 255, 0.15);
  border-color: rgba(64, 158, 255, 0.4);
  color: #409EFF;
}

/* Input Area */
.input-area {
  display: flex;
  gap: 12px;
  padding: 20px 25px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0 0 16px 16px;
}

.input-area .el-textarea {
  flex: 1;
}

.input-area :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
  border-radius: 12px;
  resize: none;
}

.input-area :deep(.el-textarea__inner:focus) {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.input-area :deep(.el-textarea__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.input-area .el-button {
  align-self: flex-end;
  height: 54px;
  padding: 0 25px;
  border-radius: 12px;
}

/* Responsive */
@media (max-width: 768px) {
  .chat-container {
    height: calc(100vh - 120px);
    border-radius: 12px;
    margin: -16px;
  }

  .message-content {
    max-width: 85%;
  }

  .quick-actions {
    padding: 10px 15px;
  }

  .input-area {
    padding: 15px;
  }
}
</style>
