<template>
  <div class="common-layout">
    <el-container>
      <!-- Header区域 -->
      <el-header class="dashboard-header">
        <div class="header-content">
          <h1 class="header-title">{{ currentTitle }}</h1>
          <div class="user-section">
            <el-dropdown @command="handleUserCommand">
              <span class="user-avatar-wrapper">
                <el-avatar 
                  :size="40" 
                  :src="currentAvatar" 
                  class="user-avatar"
                  @click.stop="showAvatarDialog = true"
                />
                <span class="username">{{ currentUser.username || currentUser.email }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人信息
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-container class="main-container">
        <!-- Aside侧边栏导航 -->
        <el-aside width="200px" class="dashboard-aside">
          <el-menu
            :default-active="activeModule"
            class="el-menu-vertical"
            @select="handleModuleChange"
          >
            <el-menu-item index="resume">
              <el-icon><Document /></el-icon>
              <span>简历管理</span>
            </el-menu-item>
            <el-menu-item index="tasks">
              <el-icon><List /></el-icon>
              <span>任务中心</span>
            </el-menu-item>
            <el-menu-item index="analytics">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据分析</span>
            </el-menu-item>
            <el-menu-item index="ai">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI助手</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- Main主内容区域 -->
        <el-container class="content-container">
          <el-main class="dashboard-main">
            <!-- 动态加载模块内容 -->
            <component :is="currentComponent" />
          </el-main>
          <el-footer class="dashboard-footer">
            <p>© 2025 SkillSpace技能空间 - 我的技能展示空间</p>
          </el-footer>
        </el-container>
      </el-container>
    </el-container>
    
    <!-- 头像选择对话框 -->
    <el-dialog 
      v-model="showAvatarDialog" 
      title="选择头像" 
      width="500px"
      align-center
    >
      <div class="avatar-selection">
        <div 
          v-for="avatar in avatarList" 
          :key="avatar.id"
          class="avatar-option"
          :class="{ 'avatar-selected': currentAvatar === avatar.url }"
          @click="selectAvatar(avatar.url)"
        >
          <el-avatar :size="80" :src="avatar.url" />
          <div class="avatar-check" v-if="currentAvatar === avatar.url">
            <el-icon><Check /></el-icon>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAvatarDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmAvatar">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, shallowRef } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Document, List, DataAnalysis, User, SwitchButton, ChatDotRound, Check } from '@element-plus/icons-vue';
import { authAPI } from '@/api';

// 导入模块组件
import ResumeModule from './modules/ResumeModule.vue';
import TasksModule from './modules/TasksModule.vue';
import AnalyticsModule from './modules/AnalyticsModule.vue';
import ProfileModule from './modules/ProfileModule.vue';
import AiModule from './modules/AiModule.vue';

// 当前激活的模块
const activeModule = ref('resume');
const currentComponent = shallowRef(ResumeModule);

// 当前登录用户信息
const currentUser = ref({
  username: '',
  email: ''
});

// 头像相关状态
const showAvatarDialog = ref(false);
const currentAvatar = ref('http://localhost:8000/static/avatars/avatar1.svg');
const selectedAvatar = ref('http://localhost:8000/static/avatars/avatar1.svg');

// 可选头像列表
const avatarList = [
  {
    id: 1,
    url: 'http://localhost:8000/static/avatars/avatar1.svg'
  },
  {
    id: 2,
    url: 'http://localhost:8000/static/avatars/avatar2.svg'
  },
  {
    id: 3,
    url: 'http://localhost:8000/static/avatars/avatar3.svg'
  }
];

// 模块配置映射
const moduleConfig = {
  resume: {
    title: '简历管理',
    component: ResumeModule
  },
  tasks: {
    title: '任务中心',
    component: TasksModule
  },
  analytics: {
    title: '数据分析',
    component: AnalyticsModule
  },
  ai: {
    title: 'AI助手',
    component: AiModule
  },
  profile: {
    title: '个人信息',
    component: ProfileModule
  }
};

// 动态计算Header标题
const currentTitle = computed(() => {
  if (activeModule.value === 'profile') {
    return moduleConfig.profile.title;
  }
  return moduleConfig[activeModule.value]?.title || 'SkillSpace技能空间';
});

// 处理模块切换
const handleModuleChange = (index) => {
  activeModule.value = index;
  currentComponent.value = moduleConfig[index].component;
};

// 处理用户下拉菜单命令
const handleUserCommand = async (command) => {
  if (command === 'profile') {
    // 切换到个人信息页面
    activeModule.value = 'profile';
    currentComponent.value = moduleConfig.profile.component;
  } else if (command === 'logout') {
    // 退出登录
    try {
      await ElMessageBox.confirm(
        '确定要退出登录吗？',
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      );
      
      // 调用登出API
      await authAPI.logout();
      
      // 清除本地存储的用户信息
      localStorage.removeItem('user');
      
      ElMessage.success('退出登录成功');
      
      // 跳转到登录页面
      window.location.href = '/';
      
    } catch (error) {
      if (error !== 'cancel') {
        console.error('退出登录失败:', error);
        ElMessage.error('退出登录失败，请重试');
      }
    }
  }
};

// 获取当前用户信息
const fetchCurrentUser = async () => {
  try {
    // 先尝试从localStorage获取
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      currentUser.value = JSON.parse(storedUser);
    }
    
    // 从localStorage加载头像设置
    const storedAvatar = localStorage.getItem('userAvatar');
    if (storedAvatar) {
      currentAvatar.value = storedAvatar;
      selectedAvatar.value = storedAvatar;
    }
    
    // 再从后端API获取最新信息
    const response = await authAPI.getCurrentUser();
    currentUser.value = response;
    localStorage.setItem('user', JSON.stringify(response));
  } catch (error) {
    console.error('获取用户信息失败:', error);
    // 如果获取失败，可能是未登录，跳转到登录页
    if (error.status === 401 || error.status === 403) {
      ElMessage.warning('请先登录');
      window.location.href = '/';
    }
  }
};

// 选择头像
const selectAvatar = (url) => {
  selectedAvatar.value = url;
};

// 确认头像选择
const confirmAvatar = () => {
  currentAvatar.value = selectedAvatar.value;
  // 保存到localStorage
  localStorage.setItem('userAvatar', selectedAvatar.value);
  showAvatarDialog.value = false;
  ElMessage.success('头像更新成功');
};

// 组件挂载时获取用户信息
onMounted(() => {
  fetchCurrentUser();
});
</script>

<style scoped>
.common-layout {
  height: 100vh;
  overflow: hidden;
}

.el-container {
  height: 100%;
}

/* Header样式 */
.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.user-section {
  display: flex;
  align-items: center;
}

.user-avatar-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.user-avatar-wrapper:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* 头像样式优化 */
.user-avatar {
  cursor: pointer;
  border: 2px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.user-avatar:hover {
  border-color: #ffffff;
  transform: scale(1.05);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
}

/* 用户名样式优化 - 提高辨识度 */
.username {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  text-shadow: 
    0 1px 2px rgba(0, 0, 0, 0.3),
    0 0 8px rgba(0, 0, 0, 0.2);
  background: rgba(0, 0, 0, 0.15);
  padding: 4px 12px;
  border-radius: 12px;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

/* Aside侧边栏样式 */
.dashboard-aside {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.el-menu-vertical {
  border-right: none;
  background-color: transparent;
}

.el-menu-item {
  font-size: 14px;
}

.el-menu-item.is-active {
  background-color: #ecf5ff;
  color: #409eff;
}

/* Main内容区域样式 */
.main-container {
  height: calc(100vh - 60px);
}

.content-container {
  display: flex;
  flex-direction: column;
}

.dashboard-main {
  flex: 1;
  background-color: #ffffff;
  padding: 20px;
  overflow-y: auto;
}

/* Footer样式 */
.dashboard-footer {
  height: 40px;
  background-color: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
}

.dashboard-footer p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

/* 头像选择对话框样式 */
.avatar-selection {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  padding: 20px;
  justify-items: center;
}

.avatar-option {
  position: relative;
  cursor: pointer;
  border: 3px solid transparent;
  border-radius: 50%;
  padding: 5px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-option:hover {
  border-color: #409eff;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.avatar-option.avatar-selected {
  border-color: #67c23a;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}

.avatar-check {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #67c23a;
  color: white;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-aside {
    width: 60px !important;
  }
  
  .el-menu-item span {
    display: none;
  }
  
  .header-title {
    font-size: 18px;
  }
  
  .username {
    display: none;
  }
}
</style>
