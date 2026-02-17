import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/Chat.vue')
  },
  {
    path: '/requirements',
    name: 'Requirements',
    component: () => import('../views/Requirements.vue')
  },
  {
    path: '/price',
    name: 'Price',
    component: () => import('../views/Price.vue')
  },
  {
    path: '/contract',
    name: 'Contract',
    component: () => import('../views/Contract.vue')
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('smart_procurement_token')
  const userStr = localStorage.getItem('smart_procurement_user')
  const user = userStr ? JSON.parse(userStr) : null

  // 公开页面直接放行
  if (to.meta.public) {
    return next()
  }

  // 需要登录的页面
  if (!token || !user) {
    return next('/login')
  }

  // 需要管理员权限
  if (to.meta.requiresAdmin && user.role !== 'admin') {
    return next('/')
  }

  next()
})

export default router
