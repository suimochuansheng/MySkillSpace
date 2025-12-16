// api/monitor.js
/**
 * 系统监控相关API
 */
import http from './http';
import { API_ENDPOINTS } from './config';

/**
 * 获取系统状态
 *
 * @returns {Promise<Object>} 系统状态数据
 *
 * 响应示例:
 * {
 *   code: 200,
 *   data: {
 *     system: {...},
 *     cpu: {...},
 *     memory: {...},
 *     disk: {...},
 *     network: {...},
 *     database: {...}
 *   }
 * }
 */
export const getSystemStatus = async () => {
  return http.get(API_ENDPOINTS.MONITOR.SYSTEM_STATUS);
};

export default {
  getSystemStatus
};
