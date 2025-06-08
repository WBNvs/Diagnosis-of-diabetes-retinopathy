import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/dashboard/doctor',
    component: () => import('../views/doctor/DoctorDashboard.vue'),
    meta: { requiresAuth: true, role: 'doctor' },
    children: [
      {
        path: '',
        name: 'DoctorDashboard',
        component: () => import('../views/doctor/DashboardView.vue')
      },
      {
        path: 'diagnosis/new',
        name: 'NewDiagnosis',
        component: () => import('../views/doctor/diagnosis/NewDiagnosis.vue')
      },
      {
        path: 'diagnosis/history',
        name: 'DiagnosisHistory',
        component: () => import('../views/doctor/diagnosis/DiagnosisHistory.vue')
      },
      {
        path: 'reports/pending',
        name: 'PendingReports',
        component: () => import('../views/doctor/reports/PendingReports.vue')
      },
      {
        path: 'reports/list',
        name: 'ReportsList',
        component: () => import('../views/doctor/reports/ReportsList.vue')
      },
      {
        path: 'reports/:id',
        name: 'ReportDetail',
        component: () => import('../views/doctor/reports/ReportDetail.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/doctor/settings/SettingsView.vue')
      }
    ]
  },
  {
    path: '/dashboard/patient',
    name: 'PatientDashboard',
    component: () => import('../views/patient/PatientDashboard.vue'),
    meta: { requiresAuth: true, role: 'patient' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  
  console.log('路由守卫检查:', {
    to: to.path,
    from: from.path,
    token,
    role,
    requiresAuth: to.meta.requiresAuth,
    requiredRole: to.meta.role
  })
  
  if (to.meta.requiresAuth && !token) {
    console.log('需要认证但未登录，重定向到登录页')
    next('/login')
  } else if (to.meta.role && to.meta.role !== role) {
    console.log('角色不匹配，重定向到对应仪表盘')
    // 如果用户角色与路由要求的角色不匹配，重定向到对应角色的仪表盘
    if (role === 'doctor') {
      next('/dashboard/doctor')
    } else {
      next('/dashboard/patient')
    }
  } else {
    console.log('路由检查通过，允许访问')
    next()
  }
})

export default router 