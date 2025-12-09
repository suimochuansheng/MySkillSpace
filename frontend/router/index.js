import DashboardPage from '@/views/DashboardPage.vue'

const routes = [
  {
    path: '/',
    component: DashboardPage,
    redirect: '/resume', // 默认跳哪里看你喜好
    children: [
      // --- 新增权限系统路由 ---
      {
        path: '/sys/user',
        name: 'UserManagement',
        component: () => import('@/views/sys/user/index.vue')
      },
      {
        path: '/sys/role',
        name: 'RoleManagement',
        component: () => import('@/views/sys/role/index.vue')
      },
      {
        path: '/sys/menu',
        name: 'MenuManagement',
        component: () => import('@/views/sys/menu/index.vue')
      },
      // --- 原有业务路由 ---
      {
        path: '/resume',
        name: 'Resume',
        component: () => import('@/views/Resume/index.vue') // 假设你的路径
      },
      // ... 其他路由
    ]
  }
]