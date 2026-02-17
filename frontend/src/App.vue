<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useResponsive, useAuth } from './composables'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()

const { user, isLoggedIn, logout, isAdmin } = useAuth()

const baseMenuItems = [
  { path: '/', icon: 'DataAnalysis', title: '系统概览' },
  { path: '/chat', icon: 'ChatDotRound', title: 'AI对话' },
  { path: '/requirements', icon: 'Document', title: '需求审查' },
  { path: '/price', icon: 'TrendCharts', title: '价格参考' },
  { path: '/contract', icon: 'DocumentCopy', title: '合同分析' }
]

const menuItems = computed(() => {
  const items = [...baseMenuItems]
  if (isAdmin.value) {
    items.push({ path: '/admin', icon: 'Setting', title: '管理后台' })
  }
  return items
})

const activeMenu = computed(() => route.path)

// 使用 composable
const { isMobile } = useResponsive(768)
const drawerVisible = ref(false)

// 切换抽屉
const toggleDrawer = () => {
  drawerVisible.value = !drawerVisible.value
}

// 关闭抽屉
const closeDrawer = () => {
  drawerVisible.value = false
}

const handleSelect = (key) => {
  router.push(key)
  // 移动端导航后关闭抽屉
  if (isMobile.value) {
    closeDrawer()
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    logout()
    router.push('/login')
  } catch {}
}

const roleLabel = computed(() => {
  const labels = { handler: '承办人', processor: '经办人', admin: '管理员' }
  return labels[user.value?.role] || ''
})
</script>

<template>
  <div class="app-container">
    <!-- 移动端顶部导航栏 -->
    <div v-if="isMobile" class="mobile-header">
      <el-button
        class="hamburger-btn"
        @click="toggleDrawer"
        circle
      >
        <el-icon :size="24">
          <component :is="drawerVisible ? 'Close' : 'Menu'" />
        </el-icon>
      </el-button>
      <h1 class="mobile-title">智慧采购系统</h1>
    </div>

    <el-container>
      <!-- 桌面端固定侧边栏 -->
      <el-aside v-if="!isMobile" width="240px">
        <div class="sidebar">
          <div class="logo">
            <h2>智慧采购系统</h2>
            <p>Smart Procurement</p>
          </div>
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical"
            @select="handleSelect"
            text-color="#ffffff"
            active-text-color="#409EFF"
            background-color="#1a1a2e"
          >
            <el-menu-item
              v-for="item in menuItems"
              :key="item.path"
              :index="item.path"
            >
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>
          </el-menu>
          <!-- 用户信息区块 -->
          <div class="user-info" v-if="isLoggedIn">
            <div class="user-avatar">
              <el-avatar :size="40">{{ user?.username?.charAt(0)?.toUpperCase() }}</el-avatar>
            </div>
            <div class="user-detail">
              <div class="username">{{ user?.username }}</div>
              <div class="role">{{ roleLabel }}</div>
            </div>
            <el-button type="danger" text @click="handleLogout">
              退出
            </el-button>
          </div>
        </div>
      </el-aside>

      <!-- 移动端抽屉式侧边栏 -->
      <el-drawer
        v-model="drawerVisible"
        direction="ltr"
        :with-header="false"
        size="280px"
        class="mobile-drawer"
      >
        <div class="sidebar mobile-sidebar">
          <div class="logo">
            <h2>智慧采购系统</h2>
            <p>Smart Procurement</p>
          </div>
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical"
            @select="handleSelect"
            text-color="#ffffff"
            active-text-color="#409EFF"
            background-color="#1a1a2e"
          >
            <el-menu-item
              v-for="item in menuItems"
              :key="item.path"
              :index="item.path"
            >
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>
          </el-menu>
          <!-- 用户信息区块 -->
          <div class="user-info" v-if="isLoggedIn">
            <div class="user-avatar">
              <el-avatar :size="40">{{ user?.username?.charAt(0)?.toUpperCase() }}</el-avatar>
            </div>
            <div class="user-detail">
              <div class="username">{{ user?.username }}</div>
              <div class="role">{{ roleLabel }}</div>
            </div>
            <el-button type="danger" text @click="handleLogout">
              退出
            </el-button>
          </div>
        </div>
      </el-drawer>

      <el-main :class="{ 'mobile-main': isMobile }">
        <div class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade-slide" mode="out-in">
              <keep-alive :include="['Home', 'Price']">
                <component :is="Component" />
              </keep-alive>
            </transition>
          </router-view>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
}

.el-container {
  height: 100vh;
}

/* 移动端顶部导航栏 */
.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
  display: flex;
  align-items: center;
  padding: 0 16px;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.hamburger-btn {
  background: rgba(64, 158, 255, 0.15) !important;
  border: 1px solid rgba(64, 158, 255, 0.3) !important;
  color: #409EFF !important;
}

.hamburger-btn:hover {
  background: rgba(64, 158, 255, 0.25) !important;
}

.mobile-title {
  color: #409EFF;
  font-size: 18px;
  margin-left: 16px;
  font-weight: 600;
}

.sidebar {
  height: 100vh;
  background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
  position: relative;
}

.mobile-sidebar {
  width: 280px;
}

.logo {
  padding: 30px 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  color: #409EFF;
  font-size: 20px;
  margin: 0 0 5px 0;
  font-weight: 600;
  letter-spacing: 1px;
}

.logo p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  margin: 0;
}

.el-menu-vertical {
  border: none;
  flex: 1;
  padding-top: 10px;
}

.el-menu-item {
  margin: 6px 18px;
  border-radius: 10px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.el-menu-item:hover {
  background: rgba(64, 158, 255, 0.12) !important;
  transform: translateX(4px);
}

.el-menu-item.is-active {
  background: linear-gradient(90deg, rgba(64, 158, 255, 0.35) 0%, rgba(64, 158, 255, 0.15) 100%) !important;
  border-color: rgba(64, 158, 255, 0.3);
  box-shadow: 0 0 15px rgba(64, 158, 255, 0.2);
}

.el-icon {
  margin-right: 10px;
  font-size: 18px;
}

.el-main {
  padding: 0;
  overflow-y: auto;
}

.mobile-main {
  padding-top: 60px !important;
}

.main-content {
  padding: 30px;
  min-height: 100vh;
}

/* 用户信息区块 */
.user-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
.user-detail {
  flex: 1;
}
.username {
  color: #fff;
  font-size: 14px;
}
.role {
  color: #909399;
  font-size: 12px;
}

/* 路由过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease-out;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(16px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-16px);
}

:deep(.el-scrollbar__wrap) {
  overflow-x: hidden;
}

/* 移动端抽屉样式 */
:deep(.mobile-drawer) {
  .el-drawer__body {
    padding: 0;
    background: #1a1a2e;
  }
}

/* 响应式媒体查询 */
@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }

  .logo {
    padding: 20px 16px;
  }

  .logo h2 {
    font-size: 18px;
  }

  .el-menu-item {
    margin: 4px 12px;
  }
}

@media (max-width: 480px) {
  .mobile-title {
    font-size: 16px;
  }

  .main-content {
    padding: 12px;
  }
}
</style>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

#app {
  height: 100vh;
}
</style>
