<template>
  <div class="page-container">
    <MonitorDashboard />
  </div>
</template>

<script setup>
import MonitorDashboard from '@/views/dashboard/modules/MonitorDashboard.vue';

// 定义组件名称，用于 keep-alive 缓存
defineOptions({
  name: 'MonitorPage'
});
</script>

<style scoped>
.page-container {
  width: 100%;
  height: 100%;
}
</style>
