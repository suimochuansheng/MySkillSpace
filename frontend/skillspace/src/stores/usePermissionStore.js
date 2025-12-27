/**
 * 权限状态管理 Store (Pinia)
 * 负责管理用户权限、菜单、角色等信息
 * 解决权限数据的跨组件共享问题
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getRouters, getCurrentUser } from '@/api/auth'

export const usePermissionStore = defineStore('permission', () => {
  // ==========================================
  // 状态定义
  // ==========================================

  // 用户菜单（树形结构）
  const menuList = ref([])

  // 用户权限标识数组，如 ["system:user:list", "system:user:delete"]
  const permissions = ref([])

  // 用户基本信息（从 localStorage 恢复）
  const user = ref((() => {
    try {
      const savedUser = localStorage.getItem('user')
      return savedUser ? JSON.parse(savedUser) : null
    } catch (error) {
      console.error('[Permission Store] 恢复用户信息失败:', error)
      return null
    }
  })())

  // 用户角色
  const roles = ref([])

  // 加载状态
  const loading = ref(false)

  // 权限初始化标志（防止重复初始化）
  const initialized = ref(false)

  // ==========================================
  // 计算属性
  // ==========================================
  
  // 是否为超级管理员
  const isSuperAdmin = computed(() => user.value?.is_superuser || false)
  
  // 菜单是否已加载
  const isMenuLoaded = computed(() => menuList.value.length > 0)

  // ==========================================
  // 方法定义
  // ==========================================
  
  /**
   * 初始化权限信息
   * 从后端获取菜单、权限、用户信息
   */
  const initPermissions = async () => {
    if (initialized.value) {
      console.log('[Permission Store] 权限已初始化，跳过重复初始化')
      return
    }

    loading.value = true
    try {
      // 并行请求：获取菜单和当前用户信息
      const [routersRes, userRes] = await Promise.all([
        getRouters(),
        getCurrentUser()
      ])

      // 处理菜单数据
      if (routersRes?.menuList) {
        menuList.value = routersRes.menuList
      }

      // 处理权限数据
      if (routersRes?.authorities && Array.isArray(routersRes.authorities)) {
        permissions.value = routersRes.authorities
      }

      // 处理用户信息
      if (userRes) {
        user.value = userRes
        // 保存到 localStorage
        localStorage.setItem('user', JSON.stringify(userRes))
        if (userRes.role_ids) {
          roles.value = userRes.role_ids
        }
      }

      initialized.value = true
      console.log('[Permission Store] 权限初始化成功', {
        menus: menuList.value.length,
        permissions: permissions.value.length,
        roles: roles.value
      })
    } catch (error) {
      console.error('[Permission Store] 权限初始化失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 检查用户是否有指定权限
   * @param {string|array} permission - 权限标识
   * @returns {boolean}
   */
  const hasPermission = (permission) => {
    // 超级管理员拥有所有权限
    if (isSuperAdmin.value) {
      return true
    }

    if (!permission) return true

    if (typeof permission === 'string') {
      return permissions.value.includes(permission)
    }

    if (Array.isArray(permission)) {
      // 数组模式：只要有一个权限就返回true（OR逻辑）
      return permission.some(perm => permissions.value.includes(perm))
    }

    return false
  }

  /**
   * 检查用户是否拥有指定角色
   * @param {string|array} role - 角色ID或角色数组
   * @returns {boolean}
   */
  const hasRole = (role) => {
    if (isSuperAdmin.value) {
      return true
    }

    if (!role) return true

    if (typeof role === 'number' || typeof role === 'string') {
      return roles.value.includes(Number(role))
    }

    if (Array.isArray(role)) {
      return role.some(r => roles.value.includes(Number(r)))
    }

    return false
  }

  /**
   * 重置权限信息
   * 用于用户登出时清空权限数据
   */
  const resetPermissions = () => {
    menuList.value = []
    permissions.value = []
    roles.value = []
    user.value = null
    initialized.value = false
    console.log('[Permission Store] 权限已重置')
  }

  /**
   * 刷新权限信息
   * 用于权限变更后重新获取最新数据
   */
  const refreshPermissions = async () => {
    resetPermissions()
    await initPermissions()
  }

  /**
   * 设置菜单列表
   * 用于手动更新菜单（某些场景下使用）
   */
  const setMenuList = (menus) => {
    menuList.value = menus
  }

  /**
   * 设置权限列表
   */
  const setPermissions = (perms) => {
    permissions.value = perms
  }

  /**
   * 设置用户信息
   */
  const setUser = (userData) => {
    user.value = userData
    // 同步保存到 localStorage
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }

  return {
    // 状态
    menuList,
    permissions,
    user,
    roles,
    loading,
    initialized,
    
    // 计算属性
    isSuperAdmin,
    isMenuLoaded,
    
    // 方法
    initPermissions,
    hasPermission,
    hasRole,
    resetPermissions,
    refreshPermissions,
    setMenuList,
    setPermissions,
    setUser
  }
})
