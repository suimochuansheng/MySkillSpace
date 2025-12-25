<template>
  <div class="main-layout">
    <el-container>
      <!-- Header -->
      <el-header class="layout-header">
        <div class="header-content">
          <h1 class="header-title">SkillSpace 技能空间</h1>
          <div class="user-section">
            <el-dropdown @command="handleUserCommand">
              <span class="user-avatar-wrapper">
                <el-avatar :size="40" :src="currentAvatar" />
                <span class="username">{{ currentUser.username || currentUser.email }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
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
        <!-- 动态侧边栏 -->
        <el-aside width="200px" class="layout-aside">
          <el-menu
            :default-active="currentMenuPath"
            :router="true"
            class="el-menu-vertical"
            @select="handleMenuSelect"
          >
            <!-- 固定的Dashboard入口 -->
            <el-menu-item index="/dashboard">
              <el-icon><HomeFilled /></el-icon>
              <span>工作台</span>
            </el-menu-item>

            <!-- 分隔线 -->
            <el-divider style="margin: 10px 0;" />

            <!-- 动态菜单 -->
            <template v-for="menu in filteredMenuList" :key="menu.id">
              <!-- 一级菜单（目录） -->
              <el-sub-menu v-if="menu.children && menu.children.length > 0" :index="menu.path || String(menu.id)">
                <template #title>
                  <el-icon v-if="menu.icon"><component :is="menu.icon" /></el-icon>
                  <span>{{ menu.name }}</span>
                </template>

                <!-- 二级菜单 -->
                <el-menu-item
                  v-for="child in menu.children"
                  :key="child.id"
                  :index="child.path"
                >
                  <el-icon v-if="child.icon"><component :is="child.icon" /></el-icon>
                  <span>{{ child.name }}</span>
                </el-menu-item>
              </el-sub-menu>

              <!-- 一级菜单（无子菜单） -->
              <el-menu-item v-else :index="menu.path">
                <el-icon v-if="menu.icon"><component :is="menu.icon" /></el-icon>
                <span>{{ menu.name }}</span>
              </el-menu-item>
            </template>
          </el-menu>
        </el-aside>

        <!-- 主内容区域 -->
        <el-container class="content-container">
          <el-main class="layout-main">
            <router-view />
          </el-main>

          <el-footer class="layout-footer">
            <p>© 2025 SkillSpace技能空间 - 我的技能展示空间</p>
          </el-footer>
        </el-container>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { usePermissionStore } from '@/stores/usePermissionStore';
import { ElMessage } from 'element-plus';
import { SwitchButton, HomeFilled } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const permissionStore = usePermissionStore();

const currentUser = computed(() => permissionStore.user);
const menuList = computed(() => permissionStore.menuList);
const currentAvatar = ref('http://localhost:8000/static/avatars/avatar1.svg');

// 过滤菜单列表，移除工作台（因为已在顶部固定显示）
const filteredMenuList = computed(() => {
  return menuList.value.filter(menu => menu.path !== '/dashboard');
});

// 当前激活的菜单路径
const currentMenuPath = computed(() => {
  return route.path;
});

// 处理菜单选择事件
const handleMenuSelect = (index) => {
  console.log('[菜单切换] 导航到:', index);
  router.push(index);
};

const handleUserCommand = async (command) => {
  if (command === 'logout') {
    // 清除本地存储的用户信息
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    // 重置权限信息
    permissionStore.resetPermissions();
    ElMessage.success('退出成功');
    router.push('/login');
  }
};

onMounted(async () => {
  // 如果没有菜单数据，重新获取
  if (!menuList.value || menuList.value.length === 0) {
    await permissionStore.initPermissions();
  }
});

// 监听路由变化，更新菜单高亮
watch(() => route.path, (newPath) => {
  console.log('[路由变化] 当前路径:', newPath);
});
</script>

<style scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
}

.layout-header {
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.user-avatar-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #303133;
}

.main-container {
  height: calc(100vh - 60px);
}

.layout-aside {
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.el-menu-vertical {
  border-right: none;
}

.layout-main {
  padding: 20px;
  background: #ffffff;
  overflow-y: auto;
}

.layout-footer {
  text-align: center;
  padding: 10px;
  border-top: 1px solid #e4e7ed;
  background: #f5f7fa;
  font-size: 12px;
  color: #909399;
}
</style>
