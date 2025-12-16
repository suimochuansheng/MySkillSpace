<template>
  <div class="ai-module">
    <el-card class="ai-header-card" shadow="never">
      <div class="ai-header">
        <div class="ai-title">
          <el-icon :size="24" color="#409EFF"><ChatDotRound /></el-icon>
          <h2>AI智能助手</h2>
        </div>
        <div class="ai-subtitle">
          <el-tag type="info" size="small">基于通义千问-7B</el-tag>
          <span class="powered-by">智能问答服务</span>
        </div>
      </div>
    </el-card>

    <!-- 对话历史记录 -->
    <el-card class="chat-history-card" shadow="never">
      <div class="chat-container" ref="chatContainerRef">
        <!-- 欢迎信息 -->
        <div v-if="chatHistory.length === 0" class="welcome-message">
          <el-empty description="暂无对话记录">
            <template #image>
              <el-icon :size="100" color="#409EFF"><ChatLineRound /></el-icon>
            </template>
            <p class="welcome-text">👋 您好！我是AI智能助手，有什么可以帮您的吗？</p>
            <div class="quick-questions">
              <p class="quick-title">💡 快速提问：</p>
              <el-button 
                v-for="(question, index) in quickQuestions" 
                :key="index"
                size="small"
                plain
                @click="handleQuickQuestion(question)"
              >
                {{ question }}
              </el-button>
            </div>
          </el-empty>
        </div>

        <!-- 对话消息列表 -->
        <div v-else class="message-list">
          <div 
            v-for="(message, index) in chatHistory" 
            :key="index"
            :class="['message-item', message.role]"
          >
            <!-- 用户消息 -->
            <div v-if="message.role === 'user'" class="user-message">
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ message.time }}</div>
              </div>
              <el-avatar :size="40" class="message-avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
            </div>

            <!-- AI消息 -->
            <div v-else class="ai-message">
              <el-avatar :size="40" class="message-avatar" style="background-color: #409EFF;">
                <el-icon><ChatDotRound /></el-icon>
              </el-avatar>
              <div class="message-content">
                <!-- AI思考过程（折叠展示） -->
                <el-collapse v-if="message.thinking" class="thinking-collapse">
                  <el-collapse-item name="thinking">
                    <template #title>
                      <div class="thinking-header">
                        <el-icon><Loading /></el-icon>
                        <span>AI 思考过程</span>
                        <el-tag v-if="message.isTyping && !message.content" size="small" type="info">正在思考...</el-tag>
                      </div>
                    </template>
                    <div class="thinking-content" v-html="formatMarkdown(message.thinking)"></div>
                  </el-collapse-item>
                </el-collapse>

                <!-- AI最终回答 -->
                <div v-if="message.content" class="message-text-wrapper">
                  <div class="message-text" v-html="formatMarkdown(message.content)"></div>
                  <span v-if="message.isTyping" class="typing-cursor">|</span>
                </div>

                <!-- 加载中提示（还没有内容时） -->
                <div v-if="message.isTyping && !message.thinking && !message.content" class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                
                <div class="message-actions">
                  <span class="message-time">{{ message.time }}</span>
                  <el-button 
                    v-if="!message.isTyping"
                    size="small" 
                    text 
                    @click="copyToClipboard(message.content)"
                  >
                    <el-icon><CopyDocument /></el-icon>
                    复制
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 输入区域 -->
    <el-card class="input-card" shadow="never">
      <div class="input-container">
        <el-input
          v-model="userInput"
          type="textarea"
          :rows="3"
          placeholder="请输入您的问题...（支持2000字以内）"
          :maxlength="2000"
          show-word-limit
          @keydown.ctrl.enter="handleSend"
          :disabled="isLoading"
        />
        <div class="input-actions">
          <el-button 
            @click="handleClear" 
            :disabled="chatHistory.length === 0"
            size="default"
          >
            <el-icon><Delete /></el-icon>
            清空对话
          </el-button>
          <div class="right-buttons">
            <el-button 
              v-if="isLoading"
              type="danger"
              @click="handleStop"
              size="default"
            >
              停止
            </el-button>
            <el-button 
              type="primary" 
              @click="handleSend"
              :loading="isLoading"
              :disabled="!userInput.trim()"
              size="default"
            >
              <el-icon v-if="!isLoading"><Promotion /></el-icon>
              {{ isLoading ? '正在思考...' : '发送 (Ctrl+Enter)' }}
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { aiAPI } from '@/api';
import {
  ChatDotRound,
  ChatLineRound,
  CopyDocument,
  Delete,
  Loading,
  Promotion,
  User
} from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { createHighlighter } from 'shiki';
import { v4 as uuidv4 } from 'uuid';
import { nextTick, onMounted, ref } from 'vue';

// 会话ID（使用localStorage持久化）
const sessionId = ref('');

// 对话历史记录
const chatHistory = ref([]);

// 用户输入
const userInput = ref('');

// 加载状态
const isLoading = ref(false);

// 流式请求控制器（用于中断请求）
const abortController = ref(null);

// 聊天容器引用
const chatContainerRef = ref(null);

// Shiki 高亮器实例
const highlighter = ref(null);

// 快速提问选项
const quickQuestions = ref([
  '介绍一下Python编程语言',
  '什么是机器学习？',
  '如何学习前端开发？',
  '解释一下Vue.js框架'
]);

// 初始化Shiki高亮器（Shiki v3.x API）
const initShiki = async () => {
  try {
    highlighter.value = await createHighlighter({
      themes: ['nord'],
      langs: ['javascript', 'python', 'html', 'css', 'json', 'bash', 'typescript', 'vue']
    });
    console.log('Shiki 高亮器初始化成功');
  } catch (error) {
    console.error('Shiki 高亮器初始化失败:', error);
  }
};

// 初始化或获取sessionId
const initSessionId = () => {
  const storedSessionId = localStorage.getItem('ai_session_id');
  if (storedSessionId) {
    sessionId.value = storedSessionId;
  } else {
    // 生成新的UUID（需要安装uuid包：npm install uuid）
    const newSessionId = uuidv4();
    sessionId.value = newSessionId;
    localStorage.setItem('ai_session_id', newSessionId);
  }
};

// 加载历史对话记录
const loadHistory = async () => {
  if (!sessionId.value) return;
  
  try {
    const response = await aiAPI.getHistory(sessionId.value);
    if (response.code === 200 && response.data) {
      // 转换后端数据格式为前端显示格式
      chatHistory.value = response.data.map(record => ({
        role: record.role,
        content: record.content,
        time: formatBackendTime(record.created_at)
      }));
      
      // 滚动到底部
      scrollToBottom();
    }
  } catch (error) {
    console.error('加载历史记录失败:', error);
    // 不显示错误提示，静默失败
  }
};

// 格式化后端时间戳
const formatBackendTime = (timestamp) => {
  const date = new Date(timestamp);
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
};

// 格式化时间
const formatTime = () => {
  const now = new Date();
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
};

// Markdown格式化（完整支持Markdown语法 + Shiki代码高亮）
// ⚠️ 关键：此函数只负责渲染，不处理业务逻辑
const formatMarkdown = (text) => {
  if (!text) return '';

  // === 步骤0：清理特殊字符和XML标记 ===
  text = text.replace(/<\|[^|]+\|>/g, '');
  text = text.replace(/!\[.*?\]\(.*?\)/g, '');
  text = text.replace(/<img[^>]*>/gi, '');
  text = text.replace(/<\/?thinking>/gi, '');
  text = text.replace(/<\/?answer>/gi, '');

  // === 步骤1：提取代码块（占位符保护）===
  const codeBlocks = [];
  text = text.replace(/```([\w]*)?\n([\s\S]*?)```/g, (match, lang, code) => {
    const language = lang?.toLowerCase() || 'javascript';
    const trimmedCode = code.trim();

    let codeHtml = '';

    if (highlighter.value) {
      try {
        const highlighted = highlighter.value.codeToHtml(trimmedCode, {
          lang: language,
          theme: 'nord'
        });

        codeHtml = `
          <div class="code-block-wrapper">
            <div class="code-block-header">
              <span class="code-language">${language}</span>
              <button class="code-copy-btn" onclick="copyCode(this)" data-code="${escapeHtml(trimmedCode)}">
                📋 复制
              </button>
            </div>
            ${highlighted}
          </div>
        `;
      } catch (error) {
        console.warn(`Shiki 高亮失败 (${language}):`, error);
        codeHtml = `
          <div class="code-block-wrapper">
            <div class="code-block-header">
              <span class="code-language">${language}</span>
              <button class="code-copy-btn" onclick="copyCode(this)" data-code="${escapeHtml(trimmedCode)}">
                📋 复制
              </button>
            </div>
            <pre><code>${escapeHtml(trimmedCode)}</code></pre>
          </div>
        `;
      }
    } else {
      codeHtml = `
        <div class="code-block-wrapper">
          <div class="code-block-header">
            <span class="code-language">${language}</span>
            <button class="code-copy-btn" onclick="copyCode(this)" data-code="${escapeHtml(trimmedCode)}">
              📋 复制
            </button>
          </div>
          <pre><code>${escapeHtml(trimmedCode)}</code></pre>
        </div>
      `;
    }

    const placeholder = `<<<CODE_BLOCK_${codeBlocks.length}>>>`;
    codeBlocks.push(codeHtml);
    return placeholder;
  });

  // === 步骤2：提取内联代码（占位符保护）===
  const inlineCodes = [];
  text = text.replace(/`([^`]+)`/g, (match, code) => {
    const placeholder = `<<<INLINE_CODE_${inlineCodes.length}>>>`;
    inlineCodes.push(`<code class="inline-code">${code}</code>`);
    return placeholder;
  });

  // === 步骤3：处理Markdown语法 ===

  // 3.1 标题
  text = text.replace(/^######\s+(.+)$/gm, '<h6 class="markdown-h6">$1</h6>');
  text = text.replace(/^#####\s+(.+)$/gm, '<h5 class="markdown-h5">$1</h5>');
  text = text.replace(/^####\s+(.+)$/gm, '<h4 class="markdown-h4">$1</h4>');
  text = text.replace(/^###\s+(.+)$/gm, '<h3 class="markdown-h3">$1</h3>');
  text = text.replace(/^##\s+(.+)$/gm, '<h2 class="markdown-h2">$1</h2>');
  text = text.replace(/^#\s+(.+)$/gm, '<h1 class="markdown-h1">$1</h1>');

  // 3.2 水平分隔线
  text = text.replace(/^---$/gm, '<hr class="markdown-hr">');
  text = text.replace(/^\*\*\*$/gm, '<hr class="markdown-hr">');

  // 3.3 粗体
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong class="markdown-bold">$1</strong>');
  text = text.replace(/__(.+?)__/g, '<strong class="markdown-bold">$1</strong>');

  // 3.4 斜体
  text = text.replace(/\*(.+?)\*/g, '<em class="markdown-italic">$1</em>');
  text = text.replace(/\b_(.+?)_\b/g, '<em class="markdown-italic">$1</em>');

  // 3.5 链接
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a class="markdown-link" href="$2" target="_blank">$1</a>');

  // 3.6 列表处理
  const lines = text.split('\n');
  let inList = false;
  let listType = null;
  const processedLines = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const unorderedMatch = line.match(/^[-*]\s+(.+)$/);
    const orderedMatch = line.match(/^(\d+)\.\s+(.+)$/);

    if (unorderedMatch) {
      if (!inList || listType !== 'ul') {
        if (inList) processedLines.push(`</${listType}>`);
        processedLines.push('<ul class="markdown-list">');
        inList = true;
        listType = 'ul';
      }
      processedLines.push(`<li class="markdown-list-item">${unorderedMatch[1]}</li>`);
    } else if (orderedMatch) {
      if (!inList || listType !== 'ol') {
        if (inList) processedLines.push(`</${listType}>`);
        processedLines.push('<ol class="markdown-list">');
        inList = true;
        listType = 'ol';
      }
      processedLines.push(`<li class="markdown-list-item">${orderedMatch[2]}</li>`);
    } else {
      if (inList) {
        processedLines.push(`</${listType}>`);
        inList = false;
        listType = null;
      }
      processedLines.push(line);
    }
  }

  if (inList) {
    processedLines.push(`</${listType}>`);
  }

  text = processedLines.join('\n');

  // 3.7 引用块
  text = text.replace(/^>\s+(.+)$/gm, '<blockquote class="markdown-blockquote">$1</blockquote>');

  // === 步骤4：处理段落 ===
  const paragraphs = text.split(/\n\n+/).filter(p => p.trim());
  text = paragraphs.map(para => {
    para = para.trim();

    // 跳过特殊元素
    if (
      para.includes('<<<CODE_BLOCK_') ||
      para.includes('<<<INLINE_CODE_') ||
      para.startsWith('<h') ||
      para.startsWith('<ul') ||
      para.startsWith('<ol') ||
      para.startsWith('<blockquote') ||
      para.startsWith('<hr')
    ) {
      return para;
    }

    // 普通段落
    para = para.replace(/\n/g, '<br>');
    return `<p class="text-paragraph">${para}</p>`;
  }).join('');

  // === 步骤5：恢复内联代码（先恢复，避免被代码块影响）===
  inlineCodes.forEach((codeHtml, index) => {
    const placeholder = `<<<INLINE_CODE_${index}>>>`;
    text = text.replace(new RegExp(placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), codeHtml);
  });

  // === 步骤6：恢复代码块 ===
  codeBlocks.forEach((codeHtml, index) => {
    const placeholder = `<<<CODE_BLOCK_${index}>>>`;
    text = text.replace(new RegExp(placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), codeHtml);
  });

  return text;
};

// HTML转义工具函数
const escapeHtml = (text) => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};

// 全局复制代码函数（供 HTML onclick 调用）
window.copyCode = (button) => {
  const code = button.getAttribute('data-code');
  if (code) {
    navigator.clipboard.writeText(code).then(() => {
      const originalText = button.textContent;
      button.textContent = '✅ 已复制';
      button.style.color = '#67c23a';
      
      setTimeout(() => {
        button.textContent = originalText;
        button.style.color = '';
      }, 2000);
    }).catch((err) => {
      console.error('复制失败:', err);
      ElMessage.error('复制失败，请手动复制');
    });
  }
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainerRef.value) {
      chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight;
    }
  });
};

// 处理快速提问
const handleQuickQuestion = (question) => {
  userInput.value = question;
  handleSend();
};

// 发送消息
const handleSend = async () => {
  const question = userInput.value.trim();
  
  // 校验输入
  if (!question) {
    ElMessage.warning('请输入问题内容');
    return;
  }

  if (question.length > 2000) {
    ElMessage.warning('问题内容过长，请控制在2000字以内');
    return;
  }

  // 添加用户消息到历史
  chatHistory.value.push({
    role: 'user',
    content: question,
    time: formatTime()
  });

  // 清空输入框
  userInput.value = '';

  // 滚动到底部
  scrollToBottom();

  // 设置加载状态
  isLoading.value = true;
  abortController.value = new AbortController();
  
  ElMessage.info({
    message: '🤖 AI正在思考中，首次请求可能需要等待约30秒...',
    duration: 5000,
    showClose: true
  });

  // 先添加一个AI消息占位符（用于流式逐字渲染）
  const messageIndex = chatHistory.value.length;
  chatHistory.value.push({
    role: 'assistant',
    content: '',
    thinking: '',
    time: formatTime(),
    isTyping: true
  });

  try {
    // 流式请求：逐段读取并更新UI
    let thinkingBuffer = '';  // 缓存思考过程
    let answerBuffer = '';    // 缓存答案内容
    let isInAnswerPhase = false;  // 标记是否已进入答案阶段

    // 🛑 核心修复：更强大的正则，匹配各种情况
    // 匹配行首或换行后的 "答案"、"回答" 等，后面允许跟冒号或空格
    const SEPARATOR_REGEX = /(?:^|\n|[\r\n])(?:答案|Answer|回答|综上|### 答案|<answer>)[:：]?\s*/i;

    await aiAPI.sendQuestionStream(
      question,
      sessionId.value,
      (evt) => {
        if (!evt || !evt.type) return;

        if (evt.type === 'thinking') {
          // 只在未进入答案阶段时累积思考内容
          if (!isInAnswerPhase) {
            const token = evt.token || '';
            thinkingBuffer += token;

            // 🎯 实时检测是否出现了分割符（使用 split 方式）
            const match = thinkingBuffer.match(SEPARATOR_REGEX);

            if (match) {
              console.warn('⚠️ 检测到思考内容中包含答案标记，强制切换到答案阶段');
              isInAnswerPhase = true;

              // ✅ 使用 split 方式分割（更简单、更鲁棒）
              const parts = thinkingBuffer.split(SEPARATOR_REGEX);

              if (parts.length > 1) {
                // parts[0] 是分割符前的内容 → 思考
                const realThinking = parts[0].trim();

                // parts.slice(1).join('') 是分割符后的所有内容 → 答案
                const remainingAnswer = parts.slice(1).join('').trim();

                // 清理思考内容的标记
                let displayThinking = realThinking;
                if (displayThinking.startsWith('思考：')) {
                  displayThinking = displayThinking.substring(3).trim();
                }
                chatHistory.value[messageIndex].thinking = displayThinking;

                // 开始累积答案
                answerBuffer = remainingAnswer;
                if (answerBuffer) {
                  chatHistory.value[messageIndex].content = answerBuffer;
                }
              }
              return;
            }

            // 清理思考内容的标记
            let displayThinking = thinkingBuffer;
            if (displayThinking.startsWith('思考：')) {
              displayThinking = displayThinking.substring(3).trim();
            }
            // 移除末尾可能出现的"答案："标记
            displayThinking = displayThinking.replace(/\n*答案：\s*$/, '').trim();

            chatHistory.value[messageIndex].thinking = displayThinking;
          }

        } else if (evt.type === 'answer') {
          // 进入答案阶段
          isInAnswerPhase = true;

          // 累积答案内容
          answerBuffer += (evt.token || '');

          // 清理答案内容的标记
          let displayAnswer = answerBuffer;
          if (displayAnswer.startsWith('答案：')) {
            displayAnswer = displayAnswer.substring(3).trim();
          }
          // 确保不包含"思考："标记
          displayAnswer = displayAnswer.replace(/^思考：[\s\S]*?答案：/, '').trim();

          chatHistory.value[messageIndex].content = displayAnswer;

        } else if (evt.type === 'error') {
          const errText = (evt.text ?? evt.msg ?? '未知错误');
          chatHistory.value[messageIndex].content = `❌ 抱歉，出现错误：${errText}`;
          chatHistory.value[messageIndex].isTyping = false;
        } else if (evt.type === 'finish') {
          // 结束标记
          chatHistory.value[messageIndex].isTyping = false;
        }
        scrollToBottom();
      },
      abortController.value.signal
    );
  } catch (error) {
    console.error('AI对话失败:', error);
    // 取消或异常时提示
    const msg = error.name === 'AbortError' ? '请求已停止' : `抱歉，处理您的问题时出现错误：${error.message || '未知错误'}`;
    if (chatHistory.value[messageIndex]) {
      chatHistory.value[messageIndex].content = msg;
      chatHistory.value[messageIndex].isTyping = false;
    } else {
      chatHistory.value.push({
        role: 'assistant',
        content: msg,
        time: formatTime()
      });
    }
    ElMessage.error(msg);
  } finally {
    // 结束状态处理
    isLoading.value = false;
    if (chatHistory.value[messageIndex]) {
      chatHistory.value[messageIndex].isTyping = false;
    }
    abortController.value = null;
  }
};

// 清空对话
const handleClear = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有对话记录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    chatHistory.value = [];
    // 生成新的session_id
    const newSessionId = uuidv4();
    sessionId.value = newSessionId;
    localStorage.setItem('ai_session_id', newSessionId);
    ElMessage.success('对话记录已清空，已创建新会话');
  } catch {
    // 用户取消
  }
};

// 复制到剪贴板
const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('内容已复制到剪贴板');
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制');
  });
};

// 主动停止当前请求（中断流式渲染）
const handleStop = () => {
  try {
    if (abortController.value) {
      abortController.value.abort();
    }
    isLoading.value = false;
    ElMessage.info('已停止当前请求');
  } catch {}
};

// 组件挂载时的初始化
onMounted(async () => {
  // 初始化Shiki高亮器
  await initShiki();
  
  // 初始化session_id
  initSessionId();
  
  // 加载历史对话记录
  loadHistory();
});
</script>

<style scoped>
.ai-module {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
  gap: 16px;
}

/* Header样式 */
.ai-header-card {
  flex-shrink: 0;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.ai-subtitle {
  display: flex;
  align-items: center;
  gap: 8px;
}

.powered-by {
  font-size: 12px;
  color: #909399;
}

/* 聊天历史区域 */
.chat-history-card {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chat-history-card :deep(.el-card__body) {
  height: 100%;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 欢迎消息 */
.welcome-message {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-text {
  font-size: 16px;
  color: #606266;
  margin: 20px 0;
}

.quick-questions {
  margin-top: 20px;
}

.quick-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 12px;
}

.quick-questions .el-button {
  margin: 5px;
}

/* 消息列表 */
.message-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-item {
  display: flex;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 用户消息 - ✅ 修复点16：增强自适应布局 */
.user-message {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  align-items: flex-start;
  width: 100%;
}

.user-message .message-avatar {
  flex-shrink: 0;
  /* 头像固定尺寸，不随容器变化 */
}

.user-message .message-content {
  flex: 0 1 auto;
  /* 自适应宽度：不放大，可缩小，基于内容 */
  max-width: min(70%, 600px);
  /* 响应式最大宽度：取70%和600px中较小值 */
  min-width: 100px;
  /* 最小宽度，避免过窄 */
}

.user-message .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 16px;
  border-radius: 12px 12px 0 12px;
  word-wrap: break-word;
  word-break: break-word;
  /* 确保长单词换行 */
  line-height: 1.6;
  width: 100%;
  box-sizing: border-box;
}

/* AI消息 - ✅ 修复点16：增强自适应布局 */
.ai-message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  width: 100%;
}

.ai-message .message-avatar {
  flex-shrink: 0;
  /* 头像固定尺寸，不随容器变化 */
}

.ai-message .message-content {
  flex: 0 1 auto;
  /* 自适应宽度：不放大，可缩小，基于内容 */
  max-width: min(70%, 600px);
  /* 响应式最大宽度：取70%噄600px中较小值 */
  min-width: 100px;
  /* 最小宽度，避免过窄 */
}

/* AI消息文本容器 */
.message-text-wrapper {
  display: inline-flex;
  align-items: flex-end;
  background: #f4f4f5;
  color: #303133;
  padding: 12px 16px;
  border-radius: 12px 12px 12px 0;
  word-wrap: break-word;
  word-break: break-word;
  line-height: 1.6;
  width: 100%;
  box-sizing: border-box;
}

.ai-message .message-text {
  flex: 1;
  display: inline;
}

.ai-message .message-text :deep(pre) {
  background: #282c34;
  color: #abb2bf;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}

.ai-message .message-text :deep(code) {
  background: #e9ecef;
  color: #e83e8c;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

/* --- 代码块容器 --- */
.ai-message .message-text :deep(.code-block-wrapper) {
  margin: 12px 0;
  border-radius: 8px; /* 圆角稍微小一点更精致 */
  overflow: hidden;   /* 裁剪溢出 */
  background-color: #282c34; /* 统一背景色，与 Shiki 主题一致 */
  border: 1px solid rgba(255, 255, 255, 0.1); /* 微弱边框提升质感 */
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* --- 代码块头部 (语言 + 复制按钮) --- */
.ai-message .message-text :deep(.code-block-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  background-color: #21252b; /* 比代码背景稍深，形成头部区分 */
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  user-select: none; /* 防止复制时选中头部文字 */
}

/* 语言标签 */
.ai-message .message-text :deep(.code-language) {
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  color: #abb2bf;
  text-transform: lowercase; /* 编程语言通常小写显示更好看 */
}

/* 复制按钮 */
.ai-message .message-text :deep(.code-copy-btn) {
  display: flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: none;
  color: #888;
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.ai-message .message-text :deep(.code-copy-btn:hover) {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

/* --- Shiki 生成的 PRE 标签核心修正 --- */
.ai-message .message-text :deep(.code-block-wrapper pre.shiki),
.ai-message .message-text :deep(.code-block-wrapper pre) {
  margin: 0 !important;      /* 去除默认外边距 */
  padding: 16px !important;  /* 统一内边距 */
  background-color: transparent !important; /* 🚫 关键：背景透明，由 wrapper 控制 */
  overflow-x: auto;          /* 横向滚动 */
  font-family: 'Fira Code', Consolas, monospace;
  font-size: 14px;
  line-height: 1.5;
  tab-size: 4;
}

/* 代码块响应式字体 */
@media (max-width: 768px) {
  .ai-message .message-text :deep(.code-block-wrapper pre) {
    padding: 14px 16px;
    font-size: 13px;
    line-height: 1.6;
  }
}

@media (max-width: 480px) {
  .ai-message .message-text :deep(.code-block-wrapper pre) {
    padding: 12px;
    font-size: 12px;
  }
  
  .ai-message .message-text :deep(.code-block-header) {
    padding: 8px 12px;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .ai-message .message-text :deep(.code-copy-btn) {
    padding: 5px 10px;
    font-size: 11px;
  }
}

.ai-message .message-text :deep(.code-block-wrapper code) {
  background: transparent !important;
  color: inherit !important;
  padding: 0 !important;
  font-family: 'Fira Code', 'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-variant-ligatures: common-ligatures;
  /* 启用连字 */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 内联代码样式 */
.ai-message .message-text :deep(.inline-code) {
  background: #e9ecef;
  color: #e83e8c;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

/* ============================================
   修复：增强普通文本段落的文档感
   ============================================ */

/* 1. 统一所有段落的排版样式 */
.ai-message .message-text :deep(p),
.ai-message .message-text :deep(.text-paragraph) {
  font-size: 15px;          /* 稍微增大字号，提升阅读体验 */
  line-height: 1.75;        /* 增加行高，让文字不拥挤 */
  color: #2c3e50;           /* 使用更柔和的深灰色，不要纯黑 */
  margin: 12px 0;           /* 上下保持间距 */
  letter-spacing: 0.02em;   /* 微小的字间距，增加精致感 */
  text-align: justify;      /* 两端对齐，让大段文字边缘整齐 */
}

.ai-message .message-text :deep(.text-paragraph:first-child) {
  margin-top: 0;
}

.ai-message .message-text :deep(.text-paragraph:last-child) {
  margin-bottom: 0;
}

/* 2. 重点修复：列表后的段落间距 */
/* 当段落紧跟在列表（ul/ol）后面时，增加顶部间距，区分层级 */
.ai-message .message-text :deep(ul + .text-paragraph),
.ai-message .message-text :deep(ol + .text-paragraph),
.ai-message .message-text :deep(ul + p),
.ai-message .message-text :deep(ol + p) {
  margin-top: 20px;
  padding-top: 12px;
  border-top: 1px dashed #ebeef5; /* 加一条淡淡的虚线分割总结部分 */
  color: #606266; /* 总结性文字颜色稍微淡一点，形成区分 */
}

/* 3. 增强 Markdown 中的加粗显示 */
/* 确保段落里的加粗文字颜色更深，对比更明显 */
.ai-message .message-text :deep(strong),
.ai-message .message-text :deep(b),
.ai-message .message-text :deep(.markdown-bold) {
  color: #000;
  font-weight: 600;
  margin: 0 2px; /* 加粗文字左右留一点点空隙 */
}

/* 4. 优化列表样式，使其与下方段落过渡自然 */
.ai-message .message-text :deep(ul),
.ai-message .message-text :deep(ol) {
  margin: 16px 0;
  padding-left: 24px;
  color: #303133;
}

.ai-message .message-text :deep(li) {
  margin-bottom: 8px; /* 列表项之间增加空隙 */
  line-height: 1.6;
}

/* 思考内容段落样式 */
.thinking-content :deep(.text-paragraph) {
  font-size: 14px;
  line-height: 1.7;
  color: #606266;
  margin: 8px 0;
  letter-spacing: 0.01em;
}

/* ============================================
   Markdown格式样式
   ============================================ */

/* 标题样式 */
.ai-message .message-text :deep(.markdown-h1) {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 24px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #dcdfe6;
  line-height: 1.4;
}

.ai-message .message-text :deep(.markdown-h2) {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 20px 0 14px 0;
  padding-bottom: 6px;
  border-bottom: 1px solid #e4e7ed;
  line-height: 1.4;
}

.ai-message .message-text :deep(.markdown-h3) {
  font-size: 20px;
  font-weight: 600;
  color: #409EFF;
  margin: 18px 0 12px 0;
  line-height: 1.4;
}

.ai-message .message-text :deep(.markdown-h4) {
  font-size: 18px;
  font-weight: 600;
  color: #606266;
  margin: 16px 0 10px 0;
  line-height: 1.4;
}

.ai-message .message-text :deep(.markdown-h5) {
  font-size: 16px;
  font-weight: 600;
  color: #606266;
  margin: 14px 0 8px 0;
  line-height: 1.4;
}

.ai-message .message-text :deep(.markdown-h6) {
  font-size: 14px;
  font-weight: 600;
  color: #909399;
  margin: 12px 0 6px 0;
  line-height: 1.4;
}

/* 思考内容中的标题样式（稍微小一点） */
.thinking-content :deep(.markdown-h3) {
  font-size: 18px;
  color: #606266;
  margin: 14px 0 10px 0;
}

/* 粗体样式 - 已在"增强普通文本段落的文档感"部分统一定义 */
/* 保留思考内容中的粗体样式 */
.thinking-content :deep(.markdown-bold),
.thinking-content :deep(strong),
.thinking-content :deep(b) {
  font-weight: 600;
  color: #303133;
  margin: 0 2px;
}

/* 斜体样式 */
.ai-message .message-text :deep(.markdown-italic) {
  font-style: italic;
  color: #606266;
}

/* 列表样式 */
.ai-message .message-text :deep(.markdown-list) {
  margin: 16px 0;
  padding-left: 24px;
  line-height: 1.6;
  color: #303133;
}

.ai-message .message-text :deep(.markdown-list-item) {
  margin-bottom: 8px;
  color: #303133;
  font-size: 15px;
  line-height: 1.6;
}

.thinking-content :deep(.markdown-list) {
  margin: 10px 0;
  padding-left: 20px;
  line-height: 1.6;
}

.thinking-content :deep(.markdown-list-item) {
  margin-bottom: 6px;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

/* 有序列表样式 */
.ai-message .message-text :deep(.markdown-list ol),
.ai-message .message-text :deep(ol) {
  list-style-type: decimal;
}

/* 无序列表样式 */
.ai-message .message-text :deep(.markdown-list ul),
.ai-message .message-text :deep(ul) {
  list-style-type: disc;
}

/* 链接样式 */
.ai-message .message-text :deep(.markdown-link) {
  color: #409EFF;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.3s ease;
}

.ai-message .message-text :deep(.markdown-link:hover) {
  color: #66b1ff;
  border-bottom-color: #66b1ff;
}

/* 引用块样式 */
.ai-message .message-text :deep(.markdown-blockquote) {
  margin: 16px 0;
  padding: 12px 16px;
  background: #f4f4f5;
  border-left: 4px solid #409EFF;
  color: #606266;
  font-style: italic;
  line-height: 1.7;
}

.thinking-content :deep(.markdown-blockquote) {
  margin: 12px 0;
  padding: 10px 14px;
  background: #fafafa;
  border-left: 3px solid #909399;
  color: #909399;
  font-size: 13px;
}

/* 水平分隔线样式 */
.ai-message .message-text :deep(.markdown-hr) {
  margin: 20px 0;
  border: none;
  border-top: 2px solid #e4e7ed;
}

/* 滚动条美化 (Webkit) */
.ai-message .message-text :deep(.code-block-wrapper pre::-webkit-scrollbar) {
  height: 8px; /* 横向滚动条高度 */
}

.ai-message .message-text :deep(.code-block-wrapper pre::-webkit-scrollbar-thumb) {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.ai-message .message-text :deep(.code-block-wrapper pre::-webkit-scrollbar-track) {
  background-color: transparent;
}

/* --- 修复内联代码样式 --- */
/* 防止普通文本中的 `code` 也变成大黑块 */
.ai-message .message-text :deep(:not(pre) > code),
.ai-message .message-text :deep(.inline-code) {
  background-color: rgba(175, 184, 193, 0.2);
  color: #e83e8c;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: 'Fira Code', Consolas, monospace;
  font-size: 85%;
}

.thinking-content :deep(:not(pre) > code),
.thinking-content :deep(.inline-code) {
  background-color: rgba(175, 184, 193, 0.15);
  color: #d63384;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Fira Code', Consolas, monospace;
  font-size: 85%;
}

/* 思考过程折叠区域样式 */
.thinking-collapse {
  margin-bottom: 12px;
}

.thinking-collapse :deep(.el-collapse-item__header) {
  background-color: #f5f7fa;
  color: #606266;
  font-size: 13px;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.thinking-collapse :deep(.el-collapse-item__wrap) {
  background-color: #fafafa;
  border: 1px solid #e4e7ed;
  border-top: none;
  border-radius: 0 0 8px 8px;
}

.thinking-content {
  padding: 12px;
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
  background-color: #fafafa;
}

.thinking-content :deep(br) {
  display: block;
  content: "";
  margin: 4px 0;
}

/* 思考过程标题区域 */
.thinking-header {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

/* 打字机光标效果 */
.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background-color: #409EFF;
  margin-left: 2px;
  animation: blink 1s infinite;
  vertical-align: text-bottom;
  flex-shrink: 0;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* 消息时间和操作 */
.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
  display: inline-block;
}

.message-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
}

.message-avatar {
  flex-shrink: 0;
  /* 全局头像设置：固定尺寸，不参与弹性伸缩 */
  width: 40px;
  height: 40px;
}

/* 加载动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #f4f4f5;
  border-radius: 12px 12px 12px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #909399;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

/* 输入区域 */
.input-card {
  flex-shrink: 0;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.right-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 滚动条美化 */
.chat-container::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

/* 响应式设计 - ✅ 修复点16：多断点适配 */
/* 大屏幕 (>1200px) */
@media (min-width: 1200px) {
  .user-message .message-content,
  .ai-message .message-content {
    max-width: min(65%, 700px);
    /* 大屏可以更宽 */
  }
}

/* 中等屏幕 (768px-1200px) */
@media (min-width: 769px) and (max-width: 1199px) {
  .user-message .message-content,
  .ai-message .message-content {
    max-width: min(75%, 500px);
  }
}

/* 小屏幕 (481px-768px) */
@media (max-width: 768px) {
  .ai-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .user-message .message-content,
  .ai-message .message-content {
    max-width: min(85%, 400px);
    /* 小屏更宽，但限制绝对宽度 */
  }

  .input-actions {
    flex-direction: column;
    gap: 8px;
  }

  .input-actions .el-button {
    width: 100%;
  }
}

/* 超小屏幕 (≤480px) */
@media (max-width: 480px) {
  .user-message .message-content,
  .ai-message .message-content {
    max-width: 90%;
    /* 超小屏占据更多空间 */
    min-width: 80px;
  }

  .user-message .message-text,
  .ai-message .message-text {
    padding: 10px 12px;
    /* 减小内边距以节省空间 */
    font-size: 14px;
  }

  .message-avatar {
    width: 36px;
    height: 36px;
    /* 缩小头像 */
  }

  .user-message,
  .ai-message {
    gap: 8px;
    /* 减小间距 */
  }
}
</style>
