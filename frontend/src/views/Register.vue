<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const { register } = useAuth()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'handler'
})
const loading = ref(false)

const roles = [
  { label: '承办人', value: 'handler', desc: '提交采购需求' },
  { label: '经办人', value: 'processor', desc: '处理采购流程' }
]

const handleRegister = async () => {
  if (!form.value.username || !form.value.email || !form.value.password) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (form.value.password !== form.value.confirmPassword) {
    ElMessage.warning('两次密码输入不一致')
    return
  }
  loading.value = true
  const result = await register(
    form.value.username,
    form.value.email,
    form.value.password,
    form.value.role
  )
  loading.value = false

  if (result.success) {
    ElMessage.success('注册成功，请等待管理员审核')
    router.push('/login')
  } else {
    ElMessage.error(result.error || '注册失败')
  }
}
</script>

<template>
  <div class="register-container">
    <div class="register-card">
      <h1 class="title">用户注册</h1>
      <el-form :model="form" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="form.role">
            <el-radio
              v-for="r in roles"
              :key="r.value"
              :value="r.value"
            >
              {{ r.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRegister"
            style="width: 100%"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="footer">
        已有账号？
        <router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
}
.register-card {
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}
.title {
  text-align: center;
  color: #fff;
  margin-bottom: 30px;
  font-size: 24px;
}
.footer {
  text-align: center;
  color: #909399;
  margin-top: 20px;
}
.footer a {
  color: #409eff;
}
</style>
