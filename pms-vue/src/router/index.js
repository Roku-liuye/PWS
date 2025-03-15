import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { title: '登录' }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue'),
      meta: { title: '注册' }
    },
    {
      path: '/',
      component: Layout,
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/dashboard.vue'),
          meta: { title: '首页', icon: 'dashboard' }
        },
        {
          path: 'asset',
          name: 'Asset',
          component: () => import('../views/asset.vue'),
          meta: { title: '资产管理', icon: 'asset' }
        },
        {
          path: 'repair',
          name: 'Repair',
          component: () => import('../views/repair.vue'),
          meta: { title: '报修管理', icon: 'repair' }
        },
        {
          path: 'finance',
          name: 'Finance',
          component: () => import('../views/finance.vue'),
          meta: { title: '费用管理', icon: 'finance' }
        },
        {
          path: 'classroom',
          name: 'Classroom',
          component: () => import('../views/classroom.vue'),
          meta: { title: '租借课室', icon: 'classroom' }
        },
        {
          path: 'user',
          name: 'User',
          component: () => import('../views/user.vue'),
          meta: { title: '用户管理', icon: 'user' }
        },
        {
          path: 'notice',
          name: 'Notice',
          component: () => import('../views/notice.vue'),
          meta: { title: '公告管理', icon: 'notice' }
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('../views/Profile.vue'),
          meta: { title: '个人信息' }
        },
        {
          path: 'change-password',
          name: 'ChangePassword',
          component: () => import('../views/ChangePassword.vue'),
          meta: { title: '修改密码' }
        }
      ]
    }
  ]
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 获取token
  const token = localStorage.getItem('token')
  
  // 如果访问的是登录或注册页面，直接放行
  if (to.path === '/login' || to.path === '/register') {
    if (token) {
      next('/')
    } else {
      next()
    }
  } else {
    // 如果没有token，重定向到登录页面
    if (!token) {
      next('/login')
    } else {
      next()
    }
  }
})

export default router