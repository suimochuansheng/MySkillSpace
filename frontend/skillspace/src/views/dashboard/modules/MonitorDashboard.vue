<template>
  <div class="monitor-dashboard">
    <el-tabs v-model="activeTab" type="card" class="monitor-tabs">
      <el-tab-pane label="云服务器监控" name="cloud">
        <CloudServerModule :server-name="selectedServer" />
      </el-tab-pane>
      <el-tab-pane label="Windows系统监控" name="windows">
        <AnalyticsModule />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import CloudServerModule from './CloudServerModule.vue';
import AnalyticsModule from './AnalyticsModule.vue';

// 默认激活云服务器监控
const activeTab = ref('cloud');

// 默认选择的服务器（与配置文件中的服务器名称一致）
const selectedServer = ref('示例生产服务器');
</script>

<style scoped>
.monitor-dashboard {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.monitor-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.monitor-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
}

.monitor-tabs :deep(.el-tab-pane) {
  height: 100%;
}

.monitor-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.monitor-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  padding: 12px 24px;
}

.monitor-tabs :deep(.el-tabs__item.is-active) {
  color: #409eff;
  background-color: #ecf5ff;
}
</style>
