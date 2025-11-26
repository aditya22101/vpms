import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/RegisterView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/admin',
      name: 'AdminDashboard',
      component: () => import('../views/AdminDashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/parking-lots',
      name: 'AdminParkingLots',
      component: () => import('../views/AdminParkingLots.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/users',
      name: 'AdminUsers',
      component: () => import('../views/AdminUsers.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/user',
      name: 'UserDashboard',
      component: () => import('../views/UserDashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: false }
    },
    {
      path: '/user/book-parking',
      name: 'BookParking',
      component: () => import('../views/BookParkingView.vue'),
      meta: { requiresAuth: true, requiresAdmin: false }
    },
    {
      path: '/user/my-bookings',
      name: 'MyBookings',
      component: () => import('../views/MyBookingsView.vue'),
      meta: { requiresAuth: true, requiresAdmin: false }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login'
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth
  const requiresAdmin = to.meta.requiresAdmin

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (requiresAuth && requiresAdmin && !authStore.isAdmin) {
    next('/user')
  } else if (!requiresAuth && authStore.isAuthenticated) {
    if (authStore.isAdmin) {
      next('/admin')
    } else {
      next('/user')
    }
  } else {
    next()
  }
})

export default router

