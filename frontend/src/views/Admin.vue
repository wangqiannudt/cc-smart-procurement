<script setup>
import { ref, onMounted } from 'vue'
import { request } from '../api'
import { ElMessage } from 'element-plus'

// 用户管理
const users = ref([])
const userLoading = ref(false)
const userFilter = ref({ role: '', is_active: '' })

// 统计数据
const overview = ref({})
const processorWorkload = ref([])
const categorySummary = ref([])

// Tab控制
const activeTab = ref('users')

const fetchUsers = async () => {
  userLoading.value = true
  try {
    const params = {}
    if (userFilter.value.role) params.role = userFilter.value.role
    if (userFilter.value.is_active !== '') params.is_active = userFilter.value.is_active
    const res = await request.get('/users', params)
    userLoading.value = false
    if (res.success) {
      users.value = res.data
    }
  } catch (e) {
    userLoading.value = false
  }
}

const fetchOverview = async () => {
  try {
    const res = await request.get('/statistics/overview')
    if (res.success) {
      overview.value = res.data
    }
  } catch (e) {}
}

const fetchStatistics = async () => {
  try {
    const [workload, category] = await Promise.all([
      request.get('/statistics/processor-workload'),
      request.get('/statistics/category-summary')
    ])
    if (workload.success) processorWorkload.value = workload.data
    if (category.success) categorySummary.value = category.data
  } catch (e) {}
}

const activateUser = async (userId) => {
  try {
    const res = await request.put(`/users/${userId}/activate`)
    if (res.success) {
      ElMessage.success('用户已激活')
      fetchUsers()
    } else {
      ElMessage.error(res.error || '操作失败')
    }
  } catch (e) {}
}

const deactivateUser = async (userId) => {
  try {
    const res = await request.put(`/users/${userId}/deactivate`)
    if (res.success) {
      ElMessage.success('用户已停用')
      fetchUsers()
    } else {
      ElMessage.error(res.error || '操作失败')
    }
  } catch (e) {}
}

const updateUserRole = async (userId, role) => {
  try {
    const res = await request.put(`/users/${userId}/role?role=${role}`)
    if (res.success) {
      ElMessage.success('角色已更新')
      fetchUsers()
    } else {
      ElMessage.error(res.error || '操作失败')
    }
  } catch (e) {}
}

const roleLabels = { handler: '承办人', processor: '经办人', admin: '管理员' }
const statusType = (isActive) => isActive ? 'success' : 'warning'
const statusLabel = (isActive) => isActive ? '已激活' : '待审核'

onMounted(() => {
  fetchUsers()
  fetchOverview()
  fetchStatistics()
})
</script>

<template>
  <div class="admin-page">
    <h2 class="page-title">管理后台</h2>

    <!-- 概览卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-value">{{ overview.total_users || 0 }}</div>
          <div class="stat-label">总用户数</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-value">{{ overview.active_users || 0 }}</div>
          <div class="stat-label">已激活用户</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-value">{{ overview.total_requirements || 0 }}</div>
          <div class="stat-label">总需求数</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-value pending">{{ overview.pending || 0 }}</div>
          <div class="stat-label">待处理</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-value processing">{{ overview.processing || 0 }}</div>
          <div class="stat-label">处理中</div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover">
          <div class="stat-value completed">{{ overview.completed || 0 }}</div>
          <div class="stat-label">已完成</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Tab切换 -->
    <el-tabs v-model="activeTab" class="content-tabs">
      <el-tab-pane label="用户管理" name="users">
        <!-- 筛选 -->
        <div class="filter-bar">
          <el-select v-model="userFilter.role" placeholder="角色" clearable @change="fetchUsers">
            <el-option label="承办人" value="handler" />
            <el-option label="经办人" value="processor" />
            <el-option label="管理员" value="admin" />
          </el-select>
          <el-select v-model="userFilter.is_active" placeholder="状态" clearable @change="fetchUsers">
            <el-option label="已激活" :value="true" />
            <el-option label="待审核" :value="false" />
          </el-select>
        </div>

        <!-- 用户列表 -->
        <el-table :data="users" v-loading="userLoading" stripe>
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="role" label="角色">
            <template #default="{ row }">
              <el-tag>{{ roleLabels[row.role] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="statusType(row.is_active)">
                {{ statusLabel(row.is_active) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280">
            <template #default="{ row }">
              <el-button
                v-if="!row.is_active"
                type="success"
                size="small"
                @click="activateUser(row.id)"
              >
                激活
              </el-button>
              <el-button
                v-else
                type="warning"
                size="small"
                @click="deactivateUser(row.id)"
              >
                停用
              </el-button>
              <el-select
                :model-value="row.role"
                size="small"
                @change="(val) => updateUserRole(row.id, val)"
                style="width: 100px; margin-left: 8px"
              >
                <el-option label="承办人" value="handler" />
                <el-option label="经办人" value="processor" />
                <el-option label="管理员" value="admin" />
              </el-select>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="经办人工作量" name="workload">
        <el-table :data="processorWorkload" stripe>
          <el-table-column prop="username" label="经办人" />
          <el-table-column prop="total_processed" label="处理需求数" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="采购分类统计" name="category">
        <el-table :data="categorySummary" stripe>
          <el-table-column prop="category" label="品类" />
          <el-table-column prop="count" label="数量" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.admin-page {
  padding: 20px;
}
.page-title {
  color: #fff;
  margin-bottom: 20px;
}
.overview-cards {
  margin-bottom: 20px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
}
.stat-value.pending { color: #e6a23c; }
.stat-value.processing { color: #409eff; }
.stat-value.completed { color: #67c23a; }
.stat-label {
  text-align: center;
  color: #909399;
  margin-top: 8px;
}
.content-tabs {
  margin-top: 20px;
}
.filter-bar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}
</style>
