/**
 * HTTP响应拦截器
 * 统一处理API响应中的权限相关错误
 */

import { ElMessage } from 'element-plus'
import router from '@/router'

/**
 * 处理API响应错误
 * @param {object} error - 错误对象
 * @param {number} error.status - HTTP状态码
 * @param {string} error.message - 错误消息
 * @param {object} error.errors - 详细错误信息
 */
export const handleResponseError = (error) => {
  const { status, message, errors } = error

  switch (status) {
    case 401:
      // 未认证 - 用户需要登录
      ElMessage.error('会话已过期，请重新登录')
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      router.push('/login')
      break

    case 403:
      // 禁止访问 - 权限不足
      ElMessage.error('您没有权限访问此资源')
      router.push('/403')
      break

    case 404:
      // 资源不存在
      ElMessage.error('请求的资源不存在')
      break

    case 500:
      // 服务器错误
      ElMessage.error('服务器内部错误，请稍后重试')
      break

    case 400:
      // 请求错误
      ElMessage.error(message || '请求参数错误')
      break

    case 408:
      // 请求超时
      ElMessage.error('请求超时，请检查网络连接')
      break

    case 0:
      // 网络错误
      ElMessage.error('网络连接失败，请检查后端服务是否启动')
      break

    default:
      ElMessage.error(message || '请求失败，请稍后重试')
  }

  // 返回错误供调用方处理
  return Promise.reject(error)
}

/**
 * 包装fetch请求，添加错误拦截
 * @param {string} url - 请求URL
 * @param {object} config - 请求配置
 * @returns {Promise}
 */
export const fetchWithInterceptor = async (url, config = {}) => {
  try {
    const response = await fetch(url, config)
    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      const error = {
        status: response.status,
        message: data.detail || data.message || '请求失败',
        errors: data,
      }
      return handleResponseError(error)
    }

    return data
  } catch (error) {
    if (error.name === 'AbortError') {
      return handleResponseError({ status: 408, message: '请求超时' })
    } else {
      return handleResponseError({ status: 0, message: '网络连接失败' })
    }
  }
}

export default {
  handleResponseError,
  fetchWithInterceptor
}
