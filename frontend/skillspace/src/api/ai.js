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
 * 流式发送问题到AI助手（SSE over fetch）
 * @param {string} prompt - 用户问题
 * @param {string} sessionId - 会话ID（可选）
 * @param {(evt: {type:string,text:string})=>void} onChunk - 片段回调
 * @param {AbortSignal} signal - 取消信号
 */
export const sendQuestionStream = async (prompt, sessionId = null, onChunk = () => {}, signal = undefined) => {
  const requestData = { prompt, stream: true };
  if (sessionId) {
    requestData.session_id = sessionId;
  }
  // console.log('[sendQuestionStream] 请求数据:', requestData);
  const response = await fetch('/api/ai/qwen/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
    signal,
    credentials: 'include'
  });
  console.log('[sendQuestionStream] 响应状态:', response.status, '类型:', response.headers.get('content-type'));
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    for (let i = 0; i < lines.length - 1; i++) {
      const line = lines[i].trim();
      if (line.startsWith('data:')) {
        const jsonStr = line.slice(5).trim();
        if (jsonStr) {
          try {
            const evt = JSON.parse(jsonStr);
            console.log('[sendQuestionStream] 事件:', evt);
            onChunk(evt);
          } catch (e) {
            console.warn('[sendQuestionStream] 解析错误:', e, '原始:', jsonStr);
          }
        }
      }
    }
    buffer = lines[lines.length - 1];
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
