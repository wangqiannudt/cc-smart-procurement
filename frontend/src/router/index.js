import { createRouter, createWebHistory } from 'vue-router'

const routes = [
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
