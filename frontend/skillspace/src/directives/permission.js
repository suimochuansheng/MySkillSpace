/**
 * 权限控制指令 - v-permission
 * 用于控制页面元素（如按钮）的显隐和禁用状态
 * 
 * 使用方式:
 * 1. 单个权限: v-permission="'system:user:delete'"
 * 2. 任意权限(OR): v-permission="['system:user:delete', 'system:user:edit']"
 * 3. 结合v-show: <el-button v-permission="'system:user:delete'">删除</el-button>
 */

import { usePermissionStore } from '@/stores/usePermissionStore'

export const vPermission = {
  mounted(el, binding) {
    const { value } = binding
    const permissionStore = usePermissionStore()
    const userPermissions = permissionStore.permissions

    if (value && value instanceof Array && value.length > 0) {
      // 数组模式: 只要有一个权限就显示（OR逻辑）
      const hasPermission = value.some(perm => userPermissions.includes(perm))
      if (!hasPermission) {
        el.style.display = 'none'
      }
    } else if (typeof value === 'string') {
      // 字符串模式: 需要完全匹配
      if (!userPermissions.includes(value)) {
        el.style.display = 'none'
      }
    }
  }
}

/**
 * 权限禁用指令 - v-perm-disable
 * 用于基于权限禁用元素（如按钮）
 * 
 * 使用方式:
 * <el-button v-perm-disable="'system:user:edit'">编辑</el-button>
 */
export const vPermDisable = {
  mounted(el, binding) {
    const { value } = binding
    const permissionStore = usePermissionStore()
    const userPermissions = permissionStore.permissions

    if (typeof value === 'string') {
      if (!userPermissions.includes(value)) {
        // 禁用元素
        const target = el.tagName === 'BUTTON' ? el : el.querySelector('button')
        if (target) {
          target.setAttribute('disabled', 'disabled')
          target.style.cursor = 'not-allowed'
          target.style.opacity = '0.6'
        }
      }
    }
  }
}

/**
 * 权限检查函数 - 在JS代码中使用
 * @param {string|array} permission - 权限标识或权限数组
 * @returns {boolean} 是否有权限
 * 
 * 使用方式:
 * import { hasPermission } from '@/directives/permission'
 * if (hasPermission('system:user:delete')) {
 *   // 执行删除操作
 * }
 */
export const hasPermission = (permission) => {
  const permissionStore = usePermissionStore()
  const userPermissions = permissionStore.permissions

  if (!permission) return true

  if (typeof permission === 'string') {
    return userPermissions.includes(permission)
  }

  if (Array.isArray(permission)) {
    return permission.some(perm => userPermissions.includes(perm))
  }

  return false
}

export default {
  vPermission,
  vPermDisable,
  hasPermission
}
