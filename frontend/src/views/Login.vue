<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const { login } = useAuth()

const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  const result = await login(form.value.username, form.value.password)
  loading.value = false

  if (result.success) {
    ElMessage.success('登录成功')
    router.push('/')
  } else {
    ElMessage.error(result.error || '登录失败')
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">智慧采购系统</h1>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="footer">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-gradient);
}
.login-card {
  width: 400px;
  padding: 40px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
}
.title {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 30px;
  font-size: 24px;
}
.footer {
  text-align: center;
  color: var(--text-muted);
  margin-top: 20px;
}
.footer a {
  color: var(--color-primary);
}
</style>
