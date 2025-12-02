<template>
  <div class="tasks-module">
    <el-card class="module-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">任务中心</span>
          <el-button type="primary" size="small" @click="handleTriggerTask">
            <el-icon><Plus /></el-icon>
            触发新任务
          </el-button>
        </div>
      </template>

      <div class="module-content">
        <el-tabs v-model="activeTab" class="task-tabs">
          <el-tab-pane label="文件处理" name="file">
            <div class="task-trigger-section">
              <el-input
                v-model="fileTaskData.fileName"
                placeholder="请输入文件名"
                style="max-width: 300px; margin-right: 10px;"
              />
              <el-button type="primary" @click="triggerTask('file')">
                触发文件处理任务
              </el-button>
            </div>
          </el-tab-pane>

          <el-tab-pane label="数据采集" name="data">
            <div class="task-trigger-section">
              <el-input
                v-model="dataTaskData.source"
                placeholder="请输入数据源"
                style="max-width: 300px; margin-right: 10px;"
              />
              <el-button type="primary" @click="triggerTask('data')">
                触发数据采集任务
              </el-button>
            </div>
          </el-tab-pane>

          <el-tab-pane label="邮件发送" name="email">
            <div class="task-trigger-section">
              <el-input
                v-model="emailTaskData.email"
                placeholder="请输入邮箱地址"
                style="max-width: 300px; margin-right: 10px;"
              />
              <el-button type="primary" @click="triggerTask('email')">
                触发邮件发送任务
              </el-button>
            </div>
          </el-tab-pane>
        </el-tabs>

        <el-divider />

        <div class="task-info">
          <el-alert
            title="任务说明"
            type="info"
            :closable="false"
            show-icon
          >
            <p>• 文件处理：模拟文件压缩、转码等耗时操作</p>
            <p>• 数据采集：模拟从外部API获取实时数据</p>
            <p>• 邮件发送：发送欢迎邮件（控制台打印）</p>
          </el-alert>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { http } from '@/api';

const activeTab = ref('file');

const fileTaskData = ref({
  fileName: 'example.jpg'
});

const dataTaskData = ref({
  source: 'stock_api'
});

const emailTaskData = ref({
  email: 'test@example.com'
});

// 触发任务
const triggerTask = async (taskType) => {
  try {
    let requestData = { task_type: taskType };
    
    if (taskType === 'file') {
      requestData.file_name = fileTaskData.value.fileName;
    } else if (taskType === 'data') {
      requestData.source = dataTaskData.value.source;
    } else if (taskType === 'email') {
      requestData.email = emailTaskData.value.email;
    }
    
    const response = await http.post('/api/tasks/trigger/', requestData);
    
    ElMessage.success({
      message: `任务已触发！Task ID: ${response.task_id}`,
      duration: 3000
    });
    
  } catch (error) {
    console.error('触发任务失败:', error);
    ElMessage.error('触发任务失败，请重试');
  }
};

const handleTriggerTask = () => {
  ElMessage.info('请在下方选项卡中选择任务类型并触发');
};
</script>

<style scoped>
.tasks-module {
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

.task-tabs {
  margin-top: 20px;
}

.task-trigger-section {
  display: flex;
  align-items: center;
  padding: 20px 0;
}

.task-info {
  margin-top: 20px;
}

.task-info p {
  margin: 5px 0;
  font-size: 14px;
}
</style>
