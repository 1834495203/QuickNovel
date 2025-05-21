import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Main.vue') // 改为独立的 Home.vue
  },
  {
    path: '/characters',
    name: 'characters',
    component: () => import('../views/ListCharacters.vue'),
  },
  {
    path: '/character/create',
    name: 'CharacterCreate',
    component: () => import('../views/CharacterCreate.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 这里可以添加登录验证等逻辑
  next()
})

export default router
