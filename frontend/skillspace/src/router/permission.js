/**
 * 路由权限守卫
 * 负责在路由导航时进行权限检查
 */

import { usePermissionStore } from '@/stores/usePermissionStore'

/**
 * 初始化路由权限检查
 * 应在 main.js 中的 router.beforeEach 中调用
 */
export const setupRouterPermission = async (router) => {
  router.beforeEach(async (to, from, next) => {
    const permissionStore = usePermissionStore()

    // 设置页面标题
    if (to.meta.title) {
      document.title = `${to.meta.title} - SkillSpace`
    } else {
      document.title = 'SkillSpace - 技能空间'
    }

    // 获取本地存储的用户信息
    const userInfo = localStorage.getItem('user')

    // 检查路由是否需要认证（默认需要）
    const requiresAuth = to.meta.requiresAuth !== false

    if (requiresAuth) {
      // 需要认证但未登录，重定向到登录页
      if (!userInfo) {
        console.warn('[路由守卫] 未登录，重定向到登录页')
        next({
          path: '/login',
          query: { redirect: to.fullPath } // 保存目标路径，登录后跳转
        })
        return
      }

      // 权限未初始化，需要初始化
      if (!permissionStore.initialized) {
        try {
          console.log('[路由守卫] 初始化权限信息...')
          await permissionStore.initPermissions()
        } catch (error) {
          console.error('[路由守卫] 权限初始化失败:', error)
          // 权限初始化失败，登出用户
          localStorage.removeItem('user')
          localStorage.removeItem('token')
          next({
            path: '/login',
            query: { redirect: to.fullPath }
          })
          return
        }
      }

      // 检查路由级别的权限
      const requiredPermission = to.meta.permission
      if (requiredPermission) {
        const hasPermission = permissionStore.hasPermission(requiredPermission)
        if (!hasPermission) {
          console.warn(`[路由守卫] 无权访问 ${to.path}，需要权限: ${requiredPermission}`)
          next('/403')
          return
        }
      }
    }

    // 已登录用户访问登录页，重定向到首页
    if (to.path === '/login' && userInfo) {
      console.log('[路由守卫] 已登录，重定向到首页')
      next('/dashboard')
      return
    }

    // 允许访问
    next()
  })

  router.afterEach((to, from) => {
    // 页面切换完成后的处理
    console.log(`[路由] 从 ${from.path} 导航到 ${to.path}`)
  })

  // 路由错误处理
  router.onError((error) => {
    console.error('[路由错误]', error)
  })
}

export default setupRouterPermission
