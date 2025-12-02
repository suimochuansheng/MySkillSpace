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
                <el-avatar :size="40" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, shallowRef } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Document, List, DataAnalysis, User, SwitchButton } from '@element-plus/icons-vue';
import { authAPI } from '@/api';

// 导入模块组件
import ResumeModule from './modules/ResumeModule.vue';
import TasksModule from './modules/TasksModule.vue';
import AnalyticsModule from './modules/AnalyticsModule.vue';
import ProfileModule from './modules/ProfileModule.vue';

// 当前激活的模块
const activeModule = ref('resume');
const currentComponent = shallowRef(ResumeModule);

// 当前登录用户信息
const currentUser = ref({
  username: '',
  email: ''
});

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

.username {
  font-size: 14px;
  font-weight: 500;
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
