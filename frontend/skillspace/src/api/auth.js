// api/auth.js
/**
 * 认证相关API服务
 * 封装所有用户认证相关的接口调用
 */

import http from './http';
import { API_ENDPOINTS } from './config';

/**
 * 用户登录
 * 
 * @param {string} account - 用户账户（邮箱或用户名）
 * @param {string} password - 用户密码
 * @returns {Promise<Object>} 返回用户信息和消息
 * 
 * 成功响应示例:
 * {
 *   user: {
 *     id: 1,
 *     email: "user@example.com",
 *     username: "用户名",
 *     last_login: "2025-11-30T12:00:00Z"
 *   },
 *   message: "登录成功！🎉"
 * }
 * 
 * 失败响应示例:
 * {
 *   detail: "账户或密码错误，请重试"
 * }
 */
export const login = async (account, password) => {
  return http.post(API_ENDPOINTS.AUTH.LOGIN, {
    account,
    password,
  });
};

/**
 * 用户注册
 * 
 * @param {Object} userData - 用户注册信息
 * @param {string} userData.email - 邮箱
 * @param {string} userData.password - 密码
 * @param {string} userData.password_confirm - 确认密码
 * @param {string} [userData.username] - 用户名（可选）
 * @returns {Promise<Object>} 返回用户信息和消息
 * 
 * 成功响应示例:
 * {
 *   user: {
 *     id: 1,
 *     email: "user@example.com",
 *     username: "用户名",
 *     date_joined: "2025-11-30T12:00:00Z"
 *   },
 *   message: "注册成功，欢迎加入 Skillspace！"
 * }
 */
export const register = async (userData) => {
  return http.post(API_ENDPOINTS.AUTH.REGISTER, userData);
};

/**
 * 用户登出
 * 
 * @returns {Promise<Object>} 返回登出消息
 * 
 * 成功响应示例:
 * {
 *   message: "登出成功，期待您的再次访问！"
 * }
 */
export const logout = async () => {
  return http.post(API_ENDPOINTS.AUTH.LOGOUT);
};

/**
 * 获取当前登录用户信息
 * 
 * @returns {Promise<Object>} 返回用户详细信息
 * 
 * 成功响应示例:
 * {
 *   id: 1,
 *   email: "user@example.com",
 *   username: "用户名",
 *   date_joined: "2025-11-30T12:00:00Z",
 *   last_login: "2025-11-30T13:30:00Z"
 * }
 */
export const getCurrentUser = async () => {
  return http.get(API_ENDPOINTS.AUTH.ME);
};

/**
 * 修改密码
 * 
 * @param {Object} passwordData - 密码数据
 * @param {string} passwordData.old_password - 旧密码
 * @param {string} passwordData.new_password - 新密码
 * @param {string} passwordData.new_password_confirm - 确认新密码
 * @returns {Promise<Object>} 返回修改结果消息
 * 
 * 成功响应示例:
 * {
 *   message: "密码修改成功，请使用新密码重新登录"
 * }
 */
export const changePassword = async (passwordData) => {
  return http.post(API_ENDPOINTS.AUTH.PASSWORD_CHANGE, passwordData);
};

/**
 * 检查邮箱是否可用（实时验证）
 * 
 * @param {string} email - 待检查的邮箱
 * @returns {Promise<Object>} 返回邮箱可用性
 * 
 * 响应示例:
 * {
 *   available: true,  // true=可用，false=已被注册
 *   message: "该邮箱可以使用"
 * }
 */
export const checkEmail = async (email) => {
  return http.post(API_ENDPOINTS.AUTH.CHECK_EMAIL, { email });
};

// 导出所有认证API为默认对象（可选的导出方式）
export default {
  login,
  register,
  logout,
  getCurrentUser,
  changePassword,
  checkEmail,
};
