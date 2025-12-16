// src/router/index.js
/**
 * Vue Router 配置
 * 定义应用的所有路由规则和导航守卫
 */

import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterPermission } from './permission'

/**
 * 路由配置
 * 
 * meta字段说明:
 * - title: 页面标题
 * - icon: 菜单图标（Element Plus图标名称）
 * - requiresAuth: 是否需要登录（默认true）
 * - keepAlive: 是否缓存页面（默认false）
 */
const routes = [
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
  
  // 主应用页面（Dashboard）
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/DashboardPage.vue'),
    meta: { 
      requiresAuth: true,
      title: '工作台'
    }
  },
  
  // 权限管理系统路由
  {
    path: '/sys',
    redirect: '/sys/user',
    meta: { 
      requiresAuth: true,
      title: '系统管理'
    },
    children: [
      {
        path: 'user',
        name: 'UserManagement',
        component: () => import('@/views/sys/user/index.vue'),
        meta: { 
          title: '用户管理', 
          icon: 'User',
          requiresAuth: true,
          permission: 'system:user:list'
        }
      },
      {
        path: 'role',
        name: 'RoleManagement',
        component: () => import('@/views/sys/role/index.vue'),
        meta: { 
          title: '角色管理', 
          icon: 'UserFilled',
          requiresAuth: true,
          permission: 'system:role:list'
        }
      },
      {
        path: 'menu',
        name: 'MenuManagement',
        component: () => import('@/views/sys/menu/index.vue'),
        meta: { 
          title: '菜单管理', 
          icon: 'Menu',
          requiresAuth: true,
          permission: 'system:menu:list'
        }
      },
      {
        path: 'operationlog',
        name: 'OperationLogManagement',
        component: () => import('@/views/sys/operationlog/index.vue'),
        meta: { 
          title: '操作日志', 
          icon: 'DocumentCopy',
          requiresAuth: true,
          permission: 'monitor:operlog:list'
        }
      },
      {
        path: 'loginlog',
        name: 'LoginLogManagement',
        component: () => import('@/views/sys/loginlog/index.vue'),
        meta: { 
          title: '登录日志', 
          icon: 'Document',
          requiresAuth: true,
          permission: 'monitor:loginlog:list'
        }
      }
    ]
  },
  
  // 404页面（可选）
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/login/LoginPage.vue'), // 临时重定向到登录页
    meta: { 
      requiresAuth: false,
      title: '页面不存在'
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
  }
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
