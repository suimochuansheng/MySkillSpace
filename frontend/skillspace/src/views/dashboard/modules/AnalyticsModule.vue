<template>
  <div class="analytics-module">
    <el-card class="module-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">数据分析</span>
        </div>
      </template>

      <div class="module-content">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6">
            <el-card shadow="hover" class="stat-card">
              <el-statistic title="简历总数" :value="statistics.resumeCount">
                <template #prefix>
                  <el-icon><Document /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <el-card shadow="hover" class="stat-card">
              <el-statistic title="任务总数" :value="statistics.taskCount">
                <template #prefix>
                  <el-icon><List /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <el-card shadow="hover" class="stat-card">
              <el-statistic title="用户总数" :value="statistics.userCount">
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <el-card shadow="hover" class="stat-card">
              <el-statistic title="活跃度" :value="statistics.activeRate" suffix="%">
                <template #prefix>
                  <el-icon><TrendCharts /></el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
        </el-row>

        <el-divider />

        <div class="chart-placeholder">
          <el-alert
            title="数据可视化功能"
            type="info"
            :closable="false"
            show-icon
          >
            <p>此模块展示系统的统计数据和分析图表</p>
            <p>可集成 ECharts 等图表库实现更丰富的数据可视化</p>
          </el-alert>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Document, List, User, TrendCharts } from '@element-plus/icons-vue';

const statistics = ref({
  resumeCount: 0,
  taskCount: 0,
  userCount: 0,
  activeRate: 0
});

// 模拟获取统计数据
const fetchStatistics = () => {
  // 这里可以调用后端API获取真实数据
  statistics.value = {
    resumeCount: 156,
    taskCount: 89,
    userCount: 23,
    activeRate: 87.5
  };
};

onMounted(() => {
  fetchStatistics();
});
</script>

<style scoped>
.analytics-module {
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

.stat-card {
  margin-bottom: 20px;
}

.chart-placeholder {
  margin-top: 20px;
  padding: 40px;
  text-align: center;
}

.chart-placeholder p {
  margin: 10px 0;
  font-size: 14px;
  color: #606266;
}

@media (max-width: 768px) {
  .el-col {
    margin-bottom: 10px;
  }
}
</style>
