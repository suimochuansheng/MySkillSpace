// api/ai.js
/**
 * AI模块API接口
 * 提供通义千问对话服务
 */

import http from './http';

/**
 * 获取指定会话的历史记录
 * @param {string} sessionId - 会话ID
 * @returns {Promise} - 返回历史对话记录列表
 */
export const getHistory = async (sessionId) => {
  try {
    const response = await http.get(`/api/ai/qwen/?session_id=${sessionId}`);
    return response;
  } catch (error) {
    console.error('获取历史记录失败:', error);
    throw error;
  }
};

/**
 * 发送问题到AI助手
 * @param {string} prompt - 用户问题
 * @param {string} sessionId - 会话ID（可选）
 * @returns {Promise} - 返回AI回答和session_id
 */
export const sendQuestion = async (prompt, sessionId = null) => {
  try {
    const requestData = { prompt };
    if (sessionId) {
      requestData.session_id = sessionId;
    }
    const response = await http.post('/api/ai/qwen/', requestData);
    return response;
  } catch (error) {
    console.error('AI对话请求失败:', error);
    throw error;
  }
};

/**
 * 批量发送问题（可选功能）
 * @param {Array<string>} prompts - 问题数组
 * @param {string} sessionId - 会话ID（可选）
 * @returns {Promise} - 返回回答数组
 */
export const sendBatchQuestions = async (prompts, sessionId = null) => {
  try {
    const promises = prompts.map(prompt => sendQuestion(prompt, sessionId));
    const results = await Promise.all(promises);
    return results;
  } catch (error) {
    console.error('批量AI对话请求失败:', error);
    throw error;
  }
};
