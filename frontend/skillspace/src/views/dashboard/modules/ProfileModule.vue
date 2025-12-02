<template>
  <div class="profile-module">
    <el-card class="module-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">个人信息</span>
          <el-button type="primary" size="small" @click="handleEdit">
            <el-icon><Edit /></el-icon>
            编辑资料
          </el-button>
        </div>
      </template>

      <div class="module-content">
        <div class="profile-section">
          <el-avatar :size="100" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
          
          <el-descriptions title="基本信息" :column="2" border class="profile-desc">
            <el-descriptions-item label="用户名">
              {{ userInfo.username || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ userInfo.email }}
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">
              {{ formatDate(userInfo.date_joined) }}
            </el-descriptions-item>
            <el-descriptions-item label="最后登录">
              {{ formatDate(userInfo.last_login) }}
            </el-descriptions-item>
            <el-descriptions-item label="账户状态">
              <el-tag :type="userInfo.is_active ? 'success' : 'danger'">
                {{ userInfo.is_active ? '正常' : '已禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="管理员权限">
              <el-tag :type="userInfo.is_staff ? 'warning' : 'info'">
                {{ userInfo.is_staff ? '是' : '否' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Edit } from '@element-plus/icons-vue';
import { authAPI } from '@/api';

const userInfo = ref({
  username: '',
  email: '',
  date_joined: '',
  last_login: '',
  is_active: true,
  is_staff: false
});

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    // 先从localStorage获取
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      userInfo.value = JSON.parse(storedUser);
    }
    
    // 从API获取最新信息
    const response = await authAPI.getCurrentUser();
    userInfo.value = response;
  } catch (error) {
    console.error('获取用户信息失败:', error);
    ElMessage.error('获取用户信息失败');
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

// 编辑资料
const handleEdit = () => {
  ElMessage.info('编辑资料功能开发中...');
};

onMounted(() => {
  fetchUserInfo();
});
</script>

<style scoped>
.profile-module {
  height: 100%;
}

.module-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.module-content {
  min-height: 400px;
}

.profile-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.profile-desc {
  margin-top: 20px;
  width: 100%;
  max-width: 800px;
}
</style>
