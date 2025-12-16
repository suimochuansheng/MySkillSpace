<template>
  <div class="permission-denied-container">
    <div class="denied-content">
      <div class="denied-icon">
        <el-icon :size="80"><CircleCloseFilled /></el-icon>
      </div>
      <h1 class="denied-title">403</h1>
      <p class="denied-message">权限不足</p>
      <p class="denied-description">您没有权限访问此页面，如有疑问请联系系统管理员</p>
      
      <div class="denied-actions">
        <el-button type="primary" @click="handleGoBack">返回上一页</el-button>
        <el-button @click="handleGoHome">返回首页</el-button>
      </div>

      <div class="denied-info">
        <el-alert
          title="可能的原因"
          :closable="false"
          type="info"
        >
          <ul>
            <li>您的账户权限不足</li>
            <li>您的账户已被禁用</li>
            <li>会话已过期，请重新登录</li>
            <li>请求的资源不存在或已被删除</li>
          </ul>
        </el-alert>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { CircleCloseFilled } from '@element-plus/icons-vue'

const router = useRouter()

// 返回上一页
const handleGoBack = () => {
  router.back()
}

// 返回首页
const handleGoHome = () => {
  router.push('/dashboard')
}
</script>

<style scoped>
.permission-denied-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.denied-content {
  text-align: center;
  background: white;
  border-radius: 8px;
  padding: 60px 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 100%;
}

.denied-icon {
  margin-bottom: 20px;
  color: #f56c6c;
}

.denied-title {
  font-size: 60px;
  font-weight: bold;
  margin: 20px 0;
  color: #303133;
}

.denied-message {
  font-size: 24px;
  color: #606266;
  margin: 10px 0;
}

.denied-description {
  font-size: 14px;
  color: #909399;
  margin: 20px 0 40px;
  line-height: 1.6;
}

.denied-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 30px;
}

.denied-actions .el-button {
  flex: 1;
  min-width: 120px;
}

.denied-info {
  text-align: left;
}

.denied-info ul {
  margin: 12px 0;
  padding-left: 20px;
}

.denied-info li {
  margin: 8px 0;
  color: #606266;
  font-size: 14px;
}

@media (max-width: 768px) {
  .permission-denied-container {
    padding: 20px;
  }

  .denied-content {
    padding: 40px 20px;
  }

  .denied-title {
    font-size: 48px;
  }

  .denied-message {
    font-size: 18px;
  }

  .denied-actions {
    flex-direction: column;
  }
}
</style>
