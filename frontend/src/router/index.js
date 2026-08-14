// /var/www/ttennis/frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/TimeLapse.vue'),
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/views/Auth.vue'),
    meta: { requiresAuth: false, guestOnly: true, layout: 'auth' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/UserProfile.vue'),
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/my-bookings',
    name: 'MyBookings',
    component: () => import('@/views/MyBookings.vue'),
    meta: { requiresAuth: true, layout: 'main' }
  },
  {
    path: '/panel',
    name: 'AdminPanel',
    component: () => import('@/views/Admin.vue'),
    meta: { requiresAuth: true, bookingManagerOnly: true, layout: 'main' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/TimeLapse.vue'),
    meta: { layout: 'main' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const accessAuthenticated = store.getters['auth/isAuthenticated']
  const hasRefreshToken =
    !!localStorage.getItem('jwt-refresh-token')

  const isAuthenticated =
    accessAuthenticated || hasRefreshToken
  // 🔥 Исправлено: проверка по isAdmin из store, а не username
  const canManageBookings = store.getters['auth/canManageBookings']
  
  if (to.meta.guestOnly && isAuthenticated) {
    return next('/')
  }
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/auth')
  }
  
  if (to.meta.bookingManagerOnly && !canManageBookings) {
    return next('/')
  }
  
  next()
})

export default router
