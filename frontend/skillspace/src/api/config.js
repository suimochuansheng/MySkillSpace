// api/config.js
/**
 * API配置文件
 * 定义后端API的基础URL和通用配置
 */

// 后端API基础URL
// 开发环境使用localhost，生产环境需要修改为实际域名
export const API_BASE_URL = 'http://localhost:8000';

// API端点路径配置
export const API_ENDPOINTS = {
  // 认证相关接口
  AUTH: {
    LOGIN: '/api/auth/login/',           // 用户登录
    REGISTER: '/api/auth/register/',     // 用户注册
    LOGOUT: '/api/auth/logout/',         // 用户登出
    ME: '/api/auth/me/',                 // 获取当前用户信息
    PASSWORD_CHANGE: '/api/auth/password/change/',  // 修改密码
    CHECK_EMAIL: '/api/auth/check-email/', // 检查邮箱是否可用
  },
  // 简历相关接口（预留）
  RESUME: {
    LIST: '/api/resume/',
  },
  // 任务相关接口（预留）
  TASKS: {
    TRIGGER: '/api/tasks/trigger/',
  }
};

// HTTP请求超时时间（毫秒）
// ✅ 修复点5：AI推理需要较长时间，增加超时时间到2分钟
export const REQUEST_TIMEOUT = 120000;  // 120秒 = 2分钟（原为10秒）

// 请求头配置
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};
