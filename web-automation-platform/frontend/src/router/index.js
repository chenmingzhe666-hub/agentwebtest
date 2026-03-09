import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/test-edge'
  },
  {
    path: '/test-edge',
    name: 'TestEdge',
    component: () => import('../views/TestEdgeView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
