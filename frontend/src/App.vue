<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useResponsive, useAuth, useTheme } from './composables'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()

const { user, isLoggedIn, logout, isAdmin } = useAuth()
const { currentTheme, currentThemeId, availableThemes, setTheme } = useTheme()

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
const showThemePanel = ref(false)

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

// 主题切换
const handleThemeChange = (themeId) => {
  setTheme(themeId)
  showThemePanel.value = false
}
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
          <!-- 底部区域：主题切换 + 用户信息 -->
          <div class="sidebar-bottom">
            <!-- 主题切换 -->
            <div class="theme-switcher">
              <div class="theme-current" @click="showThemePanel = !showThemePanel">
                <span class="theme-icon">{{ currentTheme.preview.icon }}</span>
                <span class="theme-name">{{ currentTheme.name }}</span>
                <el-icon class="theme-arrow" :class="{ 'is-open': showThemePanel }">
                  <ArrowRight />
                </el-icon>
              </div>
              <!-- 主题选择面板 -->
              <transition name="theme-panel">
                <div v-if="showThemePanel" class="theme-panel">
                  <div
                    v-for="theme in availableThemes"
                    :key="theme.id"
                    class="theme-option"
                    :class="{ 'is-active': currentThemeId === theme.id }"
                    @click="handleThemeChange(theme.id)"
                  >
                    <div class="theme-preview" :style="{ background: theme.preview.bg }">
                      <div class="theme-dot" :style="{ background: theme.preview.color }"></div>
                    </div>
                    <div class="theme-info">
                      <span class="theme-icon">{{ theme.preview.icon }}</span>
                      <span class="theme-title">{{ theme.name }}</span>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
            <!-- 用户信息 -->
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
          <!-- 底部区域 -->
          <div class="sidebar-bottom">
            <!-- 主题切换 -->
            <div class="theme-switcher">
              <div class="theme-current" @click="showThemePanel = !showThemePanel">
                <span class="theme-icon">{{ currentTheme.preview.icon }}</span>
                <span class="theme-name">{{ currentTheme.name }}</span>
                <el-icon class="theme-arrow" :class="{ 'is-open': showThemePanel }">
                  <ArrowRight />
                </el-icon>
              </div>
              <transition name="theme-panel">
                <div v-if="showThemePanel" class="theme-panel">
                  <div
                    v-for="theme in availableThemes"
                    :key="theme.id"
                    class="theme-option"
                    :class="{ 'is-active': currentThemeId === theme.id }"
                    @click="handleThemeChange(theme.id)"
                  >
                    <div class="theme-preview" :style="{ background: theme.preview.bg }">
                      <div class="theme-dot" :style="{ background: theme.preview.color }"></div>
                    </div>
                    <div class="theme-info">
                      <span class="theme-icon">{{ theme.preview.icon }}</span>
                      <span class="theme-title">{{ theme.name }}</span>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
            <!-- 用户信息 -->
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
  background: var(--bg-gradient);
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
  background: var(--bg-gradient-vertical);
  display: flex;
  align-items: center;
  padding: 0 16px;
  z-index: 1000;
  box-shadow: var(--shadow-md);
}

.hamburger-btn {
  background: var(--color-primary-bg) !important;
  border: 1px solid var(--color-primary-border) !important;
  color: var(--color-primary) !important;
}

.hamburger-btn:hover {
  background: var(--color-primary-border) !important;
}

.mobile-title {
  color: var(--color-primary);
  font-size: 18px;
  margin-left: 16px;
  font-weight: 600;
}

.sidebar {
  height: 100vh;
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  box-shadow: 1px 0 8px rgba(0, 0, 0, 0.15);
  position: relative;
}

.mobile-sidebar {
  width: 280px;
}

.logo {
  padding: 30px 20px;
  text-align: center;
  border-bottom: 1px solid var(--border-color);
}

.logo h2 {
  color: var(--color-primary);
  font-size: 20px;
  margin: 0 0 5px 0;
  font-weight: 600;
  letter-spacing: 1px;
}

.logo p {
  color: var(--text-muted);
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
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.el-menu-item:hover {
  background: var(--color-primary-bg) !important;
  transform: translateX(4px);
}

.el-menu-item.is-active {
  background: linear-gradient(90deg, var(--color-primary-border) 0%, var(--color-primary-bg) 100%) !important;
  border-color: var(--color-primary-border);
  box-shadow: var(--shadow-glow);
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

/* 底部区域 */
.sidebar-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

/* 主题切换器 */
.theme-switcher {
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.theme-current {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
}

.theme-current:hover {
  background: var(--bg-card-hover);
}

.theme-current .theme-icon {
  font-size: 18px;
}

.theme-current .theme-name {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary);
}

.theme-current .theme-arrow {
  transition: transform 0.3s ease;
  color: var(--text-muted);
}

.theme-current .theme-arrow.is-open {
  transform: rotate(90deg);
}

/* 主题选择面板 */
.theme-panel {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.theme-option:hover {
  background: var(--bg-card-hover);
}

.theme-option.is-active {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.theme-preview {
  width: 32px;
  height: 24px;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.theme-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  right: 4px;
  bottom: 4px;
}

.theme-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.theme-info .theme-icon {
  font-size: 14px;
}

.theme-title {
  font-size: 12px;
  color: var(--text-primary);
}

/* 主题面板动画 */
.theme-panel-enter-active,
.theme-panel-leave-active {
  transition: all 0.25s ease;
}

.theme-panel-enter-from,
.theme-panel-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 用户信息区块 */
.user-info {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
}
.user-detail {
  flex: 1;
}
.username {
  color: var(--text-primary);
  font-size: 14px;
}
.role {
  color: var(--text-muted);
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
    background: var(--sidebar-bg);
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
