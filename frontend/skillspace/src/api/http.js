// api/http.js
/**
 * HTTP客户端封装
 * 提供统一的API请求方法，处理请求/响应拦截、错误处理等
 */

import { API_BASE_URL, REQUEST_TIMEOUT, DEFAULT_HEADERS } from './config';

/**
 * 封装的HTTP请求类
 * 使用原生fetch API，支持自动携带Cookie（Session认证）
 */
class HttpClient {
  /**
   * 构造函数
   * 初始化基础URL和默认配置
   */
  constructor() {
    this.baseURL = API_BASE_URL;
    this.timeout = REQUEST_TIMEOUT;
  }

 /**
   * 【新增】从Cookie中提取Django的CSRF令牌
   * @returns {string} csrftoken值（cookie固定键名csrftoken；空字符串表示未找到）
   */
  getCsrfToken() {
    const cookieArr = document.cookie.split('; ');
    for (const cookie of cookieArr) {
      const [key, value] = cookie.split('=');
      if (key === 'csrftoken') {
        return value;
      }
    }
    return '';
  }

  /**
   * 发送HTTP请求的核心方法
   * 
   * @param {string} url - 请求路径（相对路径）
   * @param {object} options - fetch API选项
   * @returns {Promise} 返回响应数据或抛出错误
   */
  async request(url, options = {}) {
    // 构建完整URL
    const fullUrl = `${this.baseURL}${url}`;

    // 合并默认配置
    const config = {
      ...options,
      headers: {
        ...DEFAULT_HEADERS,
        ...options.headers,
      },
      // 重要：credentials: 'include' 确保跨域请求携带Cookie
      // Django Session认证依赖Cookie中的sessionid
      credentials: 'include',
    };
    
    // 【核心修改】给非GET请求添加CSRF令牌头（Django要求）
    const nonGetMethods = ['POST', 'PUT', 'DELETE', 'PATCH'];
    if (nonGetMethods.includes(config.method?.toUpperCase())) {
      config.headers['X-CSRFToken'] = this.getCsrfToken();
    }
    // 创建超时控制
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    config.signal = controller.signal;

    try {
      // 发送请求
      const response = await fetch(fullUrl, config);
      
      // 清除超时定时器
      clearTimeout(timeoutId);

      // 解析响应体
      const data = await response.json().catch(() => ({}));

      // 检查HTTP状态码
      if (!response.ok) {
        // HTTP错误（4xx, 5xx）
        throw {
          status: response.status,
          message: data.detail || data.message || '请求失败',
          errors: data,
        };
      }

      // 请求成功，返回数据
      return data;

    } catch (error) {
      // 清除超时定时器
      clearTimeout(timeoutId);

      // 处理不同类型的错误
      if (error.name === 'AbortError') {
        // 请求超时
        throw { 
          status: 408, 
          message: '请求超时，请检查网络连接' 
        };
      } else if (error.status) {
        // HTTP错误（已在上面处理）
        throw error;
      } else {
        // 网络错误或其他异常
        throw { 
          status: 0, 
          message: '网络连接失败，请检查后端服务是否启动' 
        };
      }
    }
  }

  /**
   * GET请求
   * 
   * @param {string} url - 请求路径
   * @param {object} params - URL查询参数
   * @returns {Promise} 响应数据
   */
  async get(url, params = {}) {
    // 构建查询字符串
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;

    return this.request(fullUrl, {
      method: 'GET',
    });
  }

  /**
   * POST请求
   * 
   * @param {string} url - 请求路径
   * @param {object} data - 请求体数据
   * @returns {Promise} 响应数据
   */
  async post(url, data = {}) {
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  /**
   * PUT请求
   * 
   * @param {string} url - 请求路径
   * @param {object} data - 请求体数据
   * @returns {Promise} 响应数据
   */
  async put(url, data = {}) {
    return this.request(url, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * DELETE请求
   * 
   * @param {string} url - 请求路径
   * @returns {Promise} 响应数据
   */
  async delete(url) {
    return this.request(url, {
      method: 'DELETE',
    });
  }
}

// 导出单例实例
export default new HttpClient();
