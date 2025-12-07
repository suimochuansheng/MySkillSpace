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
          
          <!-- 打字速度控制 -->
          <el-popover placement="bottom" :width="250" trigger="click">
            <template #reference>
              <el-button size="small" text>
                <el-icon><Setting /></el-icon>
                设置
              </el-button>
            </template>
            <div class="speed-control">
              <div class="speed-label">打字速度：{{ typingSpeedLabel }}</div>
              <el-slider 
                v-model="typingSpeed" 
                :min="10" 
                :max="100" 
                :step="10"
                :marks="{ 10: '快', 50: '中', 100: '慢' }"
              />
            </div>
          </el-popover>
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
                <el-collapse v-if="message.thinking || message.thinkingFull" class="thinking-collapse">
                  <el-collapse-item name="thinking">
                    <template #title>
                      <div class="thinking-header">
                        <span>AI 思考过程</span>
                        <el-tag v-if="message.isTyping && message.thinking && !message.content" size="small" type="info">正在思考...</el-tag>
                      </div>
                    </template>
                    <div class="thinking-content" v-html="formatMarkdown(message.thinking)"></div>
                  </el-collapse-item>
                </el-collapse>
                
                <!-- AI最终回答 -->
                <div class="message-text-wrapper">
                  <div class="message-text" v-html="formatMarkdown(message.content)"></div>
                  <!-- 打字中的光标效果 -->
                  <span v-if="message.isTyping" class="typing-cursor">|</span>
                </div>
                
                <div class="message-actions">
                  <span class="message-time">{{ message.time }}</span>
                  
                  <!-- 跳过打字动画按钮 -->
                  <el-button 
                    v-if="message.isTyping"
                    size="small" 
                    text
                    type="primary"
                    @click="skipAllTyping(index, message)"
                  >
                    <el-icon><DArrowRight /></el-icon>
                    跳过动画
                  </el-button>
                  
                  <el-button 
                    v-else
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

          <!-- 加载中动画 -->
          <div v-if="isLoading" class="message-item ai">
            <div class="ai-message">
              <el-avatar :size="40" class="message-avatar" style="background-color: #409EFF;">
                <el-icon><ChatDotRound /></el-icon>
              </el-avatar>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
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
import { ref, nextTick, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  ChatDotRound, 
  ChatLineRound, 
  User, 
  CopyDocument, 
  Delete, 
  Promotion,
  DArrowRight,
  Setting
} from '@element-plus/icons-vue';
import { aiAPI } from '@/api';
import { v4 as uuidv4 } from 'uuid';

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

// 打字机效果相关
const typingSpeed = ref(30); // 打字速度（毫秒/字符）
const isTyping = ref(false); // 是否正在打字
let typingTimer = null; // 打字计时器

// 打字速度标签
const typingSpeedLabel = computed(() => {
  if (typingSpeed.value <= 20) return '极快';
  if (typingSpeed.value <= 40) return '快';
  if (typingSpeed.value <= 60) return '中等';
  if (typingSpeed.value <= 80) return '较慢';
  return '慢';  
});

// 快速提问选项
const quickQuestions = ref([
  '介绍一下Python编程语言',
  '什么是机器学习？',
  '如何学习前端开发？',
  '解释一下Vue.js框架'
]);

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

// 解析模型输出，提取思考过程和最终答案
const parseModelOutput = (output) => {
  if (!output) return { thought: '', answer: '' };
  
  // 匹配“思考：”到“答案：”之间的内容
  const thoughtMatch = output.match(/思考：([\s\S]*?)\n+答案：/);
  // 匹配“答案：”之后的所有内容
  const answerMatch = output.match(/答案：([\s\S]*)/);
  
  return {
    thought: thoughtMatch ? thoughtMatch[1].trim() : '',
    answer: answerMatch ? answerMatch[1].trim() : output
  };
};

// 兼容旧格式：解析AI回答，提取思考过程和最终回答（兼容<think>标签格式）
const parseAiResponse = (text) => {
  if (!text) return { thinking: '', answer: '' };
  
  // 优先尝试新格式：“思考：”和“答案：”
  const parsed = parseModelOutput(text);
  if (parsed.thought || parsed.answer !== text) {
    return { thinking: parsed.thought, answer: parsed.answer };
  }
  
  // 回退到旧格式：<think>标签
  const thinkRegex = /<think>([\s\S]*?)<\/think>/i;
  const match = text.match(thinkRegex);
  
  if (match) {
    // 提取思考过程
    const thinking = match[1].trim();
    // 提取最终回答（去除think标签后的内容）
    const answer = text.replace(thinkRegex, '').trim();
    return { thinking, answer };
  }
  
  // 如果没有think标签，全部作为回答
  return { thinking: '', answer: text };
};

// 打字机效果：逐字显示内容
const typeWriter = async (fullText, messageIndex, field = 'content') => {
  return new Promise((resolve) => {
    let currentIndex = 0;
    isTyping.value = true;
    
    const type = () => {
      if (currentIndex <= fullText.length) {
        // 更新消息内容
        chatHistory.value[messageIndex][field] = fullText.substring(0, currentIndex);
        currentIndex++;
        
        // 滚动到底部（打字时持续滚动）
        scrollToBottom();
        
        // 继续打字
        typingTimer = setTimeout(type, typingSpeed.value);
      } else {
        // 打字完成
        isTyping.value = false;
        clearTimeout(typingTimer);
        resolve();
      }
    };
    
    type();
  });
};

// 停止打字机效果（用户可以跳过动画）
const skipTyping = (messageIndex, fullContent, field = 'content') => {
  if (typingTimer) {
    clearTimeout(typingTimer);
    typingTimer = null;
  }
  isTyping.value = false;
  chatHistory.value[messageIndex][field] = fullContent;
  scrollToBottom();
};

// 跳过所有打字动画（同时显示思考和回答）
const skipAllTyping = (messageIndex, message) => {
  if (typingTimer) {
    clearTimeout(typingTimer);
    typingTimer = null;
  }
  isTyping.value = false;
  
  // 直接显示完整内容
  if (message.thinkingFull) {
    chatHistory.value[messageIndex].thinking = message.thinkingFull;
  }
  if (message.answerFull) {
    chatHistory.value[messageIndex].content = message.answerFull;
  }
  chatHistory.value[messageIndex].isTyping = false;
  scrollToBottom();
};

// 简单的Markdown格式化（将换行转换为<br>）
const formatMarkdown = (text) => {
  if (!text) return '';
  
  // 清理特殊字符
  text = text.replace(/<\|[^|]+\|>/g, '');
  
  // 移除异常的图片标签
  text = text.replace(/!\[.*?\]\(.*?\)/g, '');
  text = text.replace(/<img[^>]*>/gi, '');
  
  // 正常的Markdown格式化
  return text
    .replace(/\n/g, '<br>')
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
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
    await aiAPI.sendQuestionStream(
      question,
      sessionId.value,
      (evt) => {
        if (!evt || !evt.type) return;
        if (evt.type === 'thinking') {
          chatHistory.value[messageIndex].thinking += (evt.token || '');
        } else if (evt.type === 'answer') {
          chatHistory.value[messageIndex].content += (evt.token || '');
        } else if (evt.type === 'error') {
          const errText = (evt.text ?? evt.msg ?? '未知错误');
          chatHistory.value[messageIndex].content = `抱歉，出现错误：${errText}`;
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

// 组件挂载时的初始化
// 主动停止当前请求（中断流式渲染）
const handleStop = () => {
  try {
    if (abortController.value) {
      abortController.value.abort();
    }
    isTyping.value = false;
    isLoading.value = false;
    ElMessage.info('已停止当前请求');
  } catch {}
};
// 组件挂载时的初始化
onMounted(() => {
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

/* 速度控制样式 */
.speed-control {
  padding: 12px 0;
}

.speed-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  font-weight: 500;
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
