// src/router/index.js
/**
 * Vue Router 配置
 * 定义应用的所有路由规则和导航守卫
 *
 * 架构说明：
 * 1. 基础路由：登录、403、404等无需认证的页面
 * 2. 应用路由：所有需要认证的页面都在MainLayout下，实现统一布局和菜单
 */

import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterPermission } from './permission'

/**
 * 基础路由（无需权限控制）
 */
const basicRoutes = [
  // 根路径重定向
  {
    path: '/',
    redirect: '/dashboard'
  },

  // 登录页面
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginPage.vue'),
    meta: {
      requiresAuth: false,
      title: '用户登录'
    }
  },

  // 403权限拒绝页面
  {
    path: '/403',
    name: 'PermissionDenied',
    component: () => import('@/views/403.vue'),
    meta: {
      requiresAuth: false,
      title: '权限拒绝'
    }
  },

  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/login/LoginPage.vue'),
    meta: {
      requiresAuth: false,
      title: '页面不存在'
    }
  }
]

/**
 * 应用主路由（需要认证，使用MainLayout包装）
 */
const mainLayoutRoute = {
  path: '/',
  component: () => import('@/views/layout/MainLayout.vue'),
  meta: { requiresAuth: true },
  children: [
    // 工作台首页
    {
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/HomePage.vue'),
      meta: {
        title: '工作台',
        permission: 'dashboard:view'
      }
    },

    // AI简历诊断
    {
      path: 'resume',
      name: 'Resume',
      component: () => import('@/views/resume/ResumePage.vue'),
      meta: {
        title: 'AI简历诊断',
        permission: 'resume:view'
      }
    },

    // 任务中心
    {
      path: 'tasks',
      name: 'Tasks',
      component: () => import('@/views/tasks/TasksPage.vue'),
      meta: {
        title: '任务中心',
        permission: 'tasks:view'
      }
    },

    // 系统监控
    {
      path: 'monitor',
      name: 'Monitor',
      component: () => import('@/views/monitor/MonitorPage.vue'),
      meta: {
        title: '系统监控',
        permission: 'monitor:view'
      }
    },

    // AI助手
    {
      path: 'ai',
      name: 'Ai',
      component: () => import('@/views/ai/AiPage.vue'),
      meta: {
        title: 'AI助手',
        permission: 'ai:view'
      }
    },

    // 系统管理（重定向到用户管理）
    {
      path: 'sys',
      redirect: '/sys/user'
    },

    // 用户管理
    {
      path: 'sys/user',
      name: 'UserManagement',
      component: () => import('@/views/sys/user/index.vue'),
      meta: {
        title: '用户管理',
        icon: 'User',
        permission: 'system:user:list'
      }
    },

    // 角色管理
    {
      path: 'sys/role',
      name: 'RoleManagement',
      component: () => import('@/views/sys/role/index.vue'),
      meta: {
        title: '角色管理',
        icon: 'Avatar',
        permission: 'system:role:list'
      }
    },

    // 菜单管理
    {
      path: 'sys/menu',
      name: 'MenuManagement',
      component: () => import('@/views/sys/menu/index.vue'),
      meta: {
        title: '菜单管理',
        icon: 'Menu',
        permission: 'system:menu:list'
      }
    },

    // 操作日志
    {
      path: 'sys/operlog',
      name: 'OperationLogManagement',
      component: () => import('@/views/sys/operationlog/index.vue'),
      meta: {
        title: '操作日志',
        icon: 'DocumentCopy',
        permission: 'monitor:operlog:list'
      }
    },

    // 登录日志
    {
      path: 'sys/loginlog',
      name: 'LoginLogManagement',
      component: () => import('@/views/sys/loginlog/index.vue'),
      meta: {
        title: '登录日志',
        icon: 'Document',
        permission: 'monitor:loginlog:list'
      }
    },

    // 封禁IP管理
    {
      path: 'sys/banned-ip',
      name: 'BannedIPManagement',
      component: () => import('@/views/sys/banned-ip/index.vue'),
      meta: {
        title: '封禁IP管理',
        icon: 'Lock',
        permission: 'monitor:banned:list'
      }
    }
  ]
}

/**
 * 合并所有路由
 */
const routes = [
  ...basicRoutes,
  mainLayoutRoute
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(), // 使用HTML5 History模式
  routes,
  // 路由切换时滚动到顶部
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 设置路由权限守卫
setupRouterPermission(router)

/**
 * 全局前置守卫 - 旧的实现（已移动到permission.js）
 * 保留以下代码用于说明，实际逻辑已在permission.js中实现
 */
// router.beforeEach((to, from, next) => { ... })

/**
 * 全局后置钩子 - 旧的实现（已移动到permission.js）
 * router.afterEach((to, from) => { ... })
 */

/**
 * 路由错误处理 - 旧的实现（已移动到permission.js）
 * router.onError((error) => { ... })
 */

export default router
