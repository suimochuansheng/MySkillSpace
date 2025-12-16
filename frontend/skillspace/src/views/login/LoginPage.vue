<!-- src/components/LoginPage.vue -->
<template>
  <div class="login-container">
    <!-- 动态渐变背景层 -->
    <div class="gradient-bg">
      <div class="gradient-layer gradient-layer-1"></div>
      <div class="gradient-layer gradient-layer-2"></div>
      <div class="gradient-layer gradient-layer-3"></div>
    </div>
    
    <!-- 背景粒子动画（超炫！） -->
    <div class="particles" ref="particlesContainer"></div>

    <div class="login-card">
      <div class="glow-effect"></div>

      <h1 class="title">我的技能空间</h1>
      <p class="subtitle">我的技能展示</p>

      <!-- 账户输入框（支持邮箱或用户名） -->
      <div class="input-group">
        <input
          v-model="account"
          type="text"
          placeholder="邮箱地址或用户名"
          class="input-field"
          @focus="inputFocus('account')"
          @blur="inputBlur('account')"
        />
        <div class="underline" :class="{ active: accountFocused }"></div>
      </div>

      <!-- 密码输入框（带密码可见切换） -->
      <div class="input-group">
        <input
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="密码"
          class="input-field"
          @focus="inputFocus('password')"
          @blur="inputBlur('password')"
        />
        <div class="underline" :class="{ active: passwordFocused }"></div>
        <span class="toggle-password" @click="showPassword = !showPassword">
          {{ showPassword ? "🙈" : "👁️" }}
        </span>
      </div>

      <!-- 登录按钮（带渐变悬停效果） -->
      <button
        class="login-btn"
        :class="{ 'btn-active': isFormValid }"
        @click="handleLogin"
        :disabled="!isFormValid"
      >
        <span v-if="!isLoggingIn">登录</span>
        <span v-else>处理中...</span>
      </button>

      <div class="divider">
        <span>或继续使用</span>
      </div>

      <!-- 社交登录按钮（超现代设计） -->
      <div class="social-login">
        <button class="social-btn google">
          <svg viewBox="0 0 24 24" class="social-icon">
            <path
              d="M12.545,10.688V7.915h-2.128c-0.728,0-1.132,0.495-1.132,1.265v1.072h-0.906c0,0-0.588,0.01-0.775,0.01-0.83,0-0.994,0.412-0.994,1.072v1.43h-0.894v2.128h0.894v2.057c0,0.66,0.164,1.072,0.994,1.072h1.735v2.128h2.128v-2.128h1.287c0.83,0,0.994-0.412,0.994-1.072v-1.555h1.189v-2.057h-1.189v-1.072c0-0.66-0.164-1.072-0.994-1.072h-1.287v-1.43z"
            />
          </svg>
          Google
        </button>

        <button class="social-btn github">
          <svg viewBox="0 0 24 24" class="social-icon">
            <path
              d="M12,2A10,10 0 0,0 2,12C2,16.4182 4.87,20.1818 8.835,21.5C9.25,21.58 9.67,21.61 10.09,21.61C10.74,21.61 11.37,21.5 12,21.5C12.63,21.5 13.26,21.61 13.91,21.61C14.33,21.61 14.75,21.58 15.165,21.5C19.13,20.1818 22,16.4182 22,12A10,10 0 0,0 12,2Z"
            />
          </svg>
          GitHub
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { login } from "@/api/auth"; // 导入登录API
import { ElMessage } from 'element-plus'; // 导入Element Plus的顶部居中提示
import { computed, onMounted, ref } from "vue";
import { useRouter } from 'vue-router'; // 导入路由
import { usePermissionStore } from '@/stores/usePermissionStore'; // 导入权限store

// 创建路由实例
const router = useRouter();
const permissionStore = usePermissionStore();

// 表单数据
const account = ref("");  // 支持邮箱或用户名
const password = ref("");
const showPassword = ref(false);
const accountFocused = ref(false);
const passwordFocused = ref(false);
const isLoggingIn = ref(false);
const particlesContainer = ref(null);

// 错误消息状态
const errorMessage = ref("");

// 表单验证（支持邮箱或用户名）
const isFormValid = computed(() => {
  return account.value && password.value;
});

// 粒子动画初始化
onMounted(() => {
  if (!particlesContainer.value) return;
  
  // 创建50个粒子
  for (let i = 0; i < 50; i++) {
    createParticle();
  }
});

// 创建单个粒子
const createParticle = () => {
  const particle = document.createElement('div');
  particle.className = 'particle';
  
  // 随机位置
  const startX = Math.random() * 100;
  const startY = Math.random() * 100;
  particle.style.left = `${startX}%`;
  particle.style.top = `${startY}%`;
  
  // 随机大小 (2-6px)
  const size = Math.random() * 4 + 2;
  particle.style.width = `${size}px`;
  particle.style.height = `${size}px`;
  
  // 随机动画延迟和持续时间
  const duration = Math.random() * 20 + 15; // 15-35秒
  const delay = Math.random() * 5; // 0-5秒延迟
  particle.style.animationDuration = `${duration}s`;
  particle.style.animationDelay = `${delay}s`;
  
  particlesContainer.value.appendChild(particle);
};

// 输入框焦点处理
const inputFocus = (field) => {
  if (field === "account") accountFocused.value = true;
  if (field === "password") passwordFocused.value = true;
  // 清除错误消息
  errorMessage.value = "";
};

const inputBlur = (field) => {
  if (field === "account") accountFocused.value = false;
  if (field === "password") passwordFocused.value = false;
};

// 真实登录功能（支持邮箱或用户名）
const handleLogin = async () => {
  // 防止重复提交
  if (isLoggingIn.value) return;
  
  // 清除之前的错误消息
  errorMessage.value = "";
  
  isLoggingIn.value = true;
  
  try {
    // 调用后端API进行登录（支持邮箱或用户名）
    const response = await login(account.value, password.value);
    
    // 登录成功：显示Element Plus成功提示
    ElMessage({
      message: response.message || "登录成功！🎉 欢迎来到技能空间！",
      type: 'success',
      center: true,
      duration: 2000,  // 缩短为2秒
      offset: 50
    });
    
    // 存储用户信息到localStorage（供路由守卫检测）
    if (response.user) {
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    // 初始化权限信息（获取菜单和权限标识）
    try {
      await permissionStore.initPermissions();
      console.log('[登录] 权限初始化成功');
    } catch (error) {
      console.error('[登录] 权限初始化失败:', error);
      // 权限初始化失败但不阻止登录流程
    }
    
    // 延迟跳转，让用户看到成功提示（800毫秒后跳转到仪表板）
    setTimeout(() => {
      router.push('/dashboard');
    }, 800);
    
  } catch (error) {
    // 登录失败处理
    console.error('登录失败:', error);
    
    // 根据错误类型生成错误消息
    let errorMsg = '';
    if (error.status === 0) {
      errorMsg = '无法连接到服务器，请检查后端服务是否启动';
    } else if (error.status === 408) {
      errorMsg = '请求超时，请检查网络连接';
    } else {
      errorMsg = error.message || '登录失败，请检查账户和密码';
    }
    
    // 使用Element Plus显示错误提示
    ElMessage({
      message: errorMsg,
      type: 'error',
      center: true,
      duration: 4000,
      offset: 50,
      showClose: true
    });
    
  } finally {
    // 恢复按钮状态
    isLoggingIn.value = false;
  }
};
</script>

<style scoped>
/* 背景容器 */
.login-container {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a2e; /* 深色基底 */
}

/* 动态渐变背景 - 性能优化版 */
.gradient-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1; /* 确保在基底之上 */
  overflow: hidden;
}

/* 渐变层基础样式 */
.gradient-layer {
  position: absolute;
  width: 150%;
  height: 150%;
  top: -25%;
  left: -25%;
  opacity: 1; /* 提高不透明度让效果更明显 */
  mix-blend-mode: screen; /* 混合模式产生丰富色彩 */
  will-change: transform; /* 启用GPU加速 */
}

/* 第一层渐变：紫蓝色调 */
.gradient-layer-1 {
  background: radial-gradient(
    circle at 20% 50%,
    rgba(106, 17, 203, 0.8) 0%,
    rgba(37, 117, 252, 0.6) 50%,
    transparent 100%
  );
  animation: drift-1 25s ease-in-out infinite;
}

/* 第二层渐变：青蓝色调 */
.gradient-layer-2 {
  background: radial-gradient(
    circle at 80% 80%,
    rgba(30, 60, 114, 0.9) 0%,
    rgba(42, 82, 152, 0.7) 50%,
    transparent 100%
  );
  animation: drift-2 30s ease-in-out infinite;
  animation-delay: -5s; /* 错开动画时间 */
}

/* 第三层渐变：深紫色调 */
.gradient-layer-3 {
  background: radial-gradient(
    circle at 50% 20%,
    rgba(88, 28, 135, 0.7) 0%,
    rgba(30, 60, 114, 0.5) 50%,
    transparent 100%
  );
  animation: drift-3 35s ease-in-out infinite;
  animation-delay: -10s; /* 错开动画时间 */
}

/* 渐变漂移动画 - 第一层 */
@keyframes drift-1 {
  0%, 100% {
    transform: translate(0, 0) scale(1) rotate(0deg);
  }
  25% {
    transform: translate(5%, -5%) scale(1.1) rotate(5deg);
  }
  50% {
    transform: translate(-3%, 8%) scale(0.95) rotate(-3deg);
  }
  75% {
    transform: translate(8%, 3%) scale(1.05) rotate(8deg);
  }
}

/* 渐变漂移动画 - 第二层 */
@keyframes drift-2 {
  0%, 100% {
    transform: translate(0, 0) scale(1) rotate(0deg);
  }
  33% {
    transform: translate(-8%, 5%) scale(1.08) rotate(-10deg);
  }
  66% {
    transform: translate(6%, -6%) scale(0.92) rotate(8deg);
  }
}

/* 渐变漂移动画 - 第三层 */
@keyframes drift-3 {
  0%, 100% {
    transform: translate(0, 0) scale(1) rotate(0deg);
  }
  40% {
    transform: translate(4%, 7%) scale(1.12) rotate(6deg);
  }
  80% {
    transform: translate(-7%, -4%) scale(0.88) rotate(-12deg);
  }
}

.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2; /* 在渐变背景之上 */
  pointer-events: none;
  overflow: hidden;
}

/* 单个粒子样式 */
.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  pointer-events: none;
  animation: float linear infinite;
}

/* 粒子浮动动画 */
@keyframes float {
  0% {
    transform: translateY(0) translateX(0) scale(1);
    opacity: 0;
  }
  10% {
    opacity: 0.8;
  }
  50% {
    transform: translateY(-50vh) translateX(20px) scale(1.2);
    opacity: 0.5;
  }
  90% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(-100vh) translateX(-10px) scale(0.8);
    opacity: 0;
  }
}

/* 卡片发光效果 */
.login-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 450px;
  padding: 45px 35px;
  position: relative;
  z-index: 10; /* 确保卡片在最上层 */
  transition: all 0.4s ease;
}

.glow-effect {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle,
    rgba(106, 17, 203, 0.3) 0%,
    transparent 70%
  );
  z-index: -1;
  opacity: 0;
  transition: opacity 0.5s;
}

.login-card:hover .glow-effect {
  opacity: 1;
}

/* 标题和副标题 */
.title {
  font-size: 2.8rem;
  font-weight: 800;
  color: #1e3c72;
  text-align: center;
  margin-bottom: 10px;
  letter-spacing: 0.5px;
}

.subtitle {
  color: #5a67d8;
  text-align: center;
  font-size: 1.1rem;
  margin-bottom: 35px;
  opacity: 0.9;
}

/* 输入框样式 */
.input-group {
  position: relative;
  margin-bottom: 28px;
}

.input-field {
  width: 100%;
  padding: 16px 20px;
  border: none;
  border-bottom: 2px solid #e2e8f0;
  font-size: 1.1rem;
  background: transparent;
  outline: none;
  transition: all 0.3s;
  border-radius: 4px;
}

.input-field:focus {
  border-bottom: 2px solid #6a11cb;
  box-shadow: 0 2px 10px rgba(106, 17, 203, 0.2);
}

.underline {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: #6a11cb;
  transition: width 0.4s;
}

.underline.active {
  width: 100%;
}

.toggle-password {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  font-size: 1.2rem;
  color: #4a5568;
  transition: all 0.2s;
}

.toggle-password:hover {
  color: #6a11cb;
}

/* 登录按钮 */
.login-btn {
  background: linear-gradient(to right, #6a11cb, #2575fc);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 16px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
  margin-bottom: 25px;
  box-shadow: 0 4px 15px rgba(106, 17, 203, 0.4);
  opacity: 0.8;
}

.login-btn.btn-active {
  opacity: 1;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(106, 17, 203, 0.6);
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 分割线 */
.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 25px 0;
}

.divider span {
  color: #718096;
  font-size: 0.95rem;
  width: 100%;
  position: relative;
}

.divider span::before,
.divider span::after {
  content: "";
  border-top: 1px solid #e2e8f0;
  position: absolute;
  top: 50%;
  width: 40%;
}

.divider span::before {
  left: 0;
}

.divider span::after {
  right: 0;
}

/* 社交登录 */
.social-login {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px;
  border: none;
  border-radius: 10px;
  font-size: 1.05rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  width: 100%;
  color: white;
  background: #4a5568;
}

.social-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.social-btn.google {
  background: #4285f4;
}

.social-btn.github {
  background: #181717;
}

.social-icon {
  width: 22px;
  height: 22px;
  margin-right: 10px;
  fill: currentColor;
}
</style>
