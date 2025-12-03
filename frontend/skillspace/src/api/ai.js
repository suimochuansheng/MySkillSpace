// api/ai.js
/**
 * AI模块API接口
 * 提供通义千问对话服务
 */

import http from './http';

/**
 * 发送问题到AI助手
 * @param {string} prompt - 用户问题
 * @returns {Promise} - 返回AI回答
 */
export const sendQuestion = async (prompt) => {
  try {
    const response = await http.post('/api/ai/qwen/', { prompt });
    return response;
  } catch (error) {
    console.error('AI对话请求失败:', error);
    throw error;
  }
};

/**
 * 批量发送问题（可选功能）
 * @param {Array<string>} prompts - 问题数组
 * @returns {Promise} - 返回回答数组
 */
export const sendBatchQuestions = async (prompts) => {
  try {
    const promises = prompts.map(prompt => sendQuestion(prompt));
    const results = await Promise.all(promises);
    return results;
  } catch (error) {
    console.error('批量AI对话请求失败:', error);
    throw error;
  }
};
