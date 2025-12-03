// api/index.js
/**
 * API入口文件
 * 统一导出所有API模块
 */

// 导出认证API
export * as authAPI from './auth';

// 导出AI模块API
export * as aiAPI from './ai';

// 导出HTTP客户端（用于自定义请求）
export { default as http } from './http';

// 导出配置（用于访问API端点等）
export * from './config';
