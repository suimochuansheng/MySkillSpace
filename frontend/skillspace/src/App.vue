<script setup>
import { ref, onMounted } from 'vue';
import LoginPage from "@/views/login/LoginPage.vue";
import DashboardPage from "@/views/dashboard/DashboardPage.vue";

// 当前显示的页面
const currentPage = ref('login');

// 检查是否已登录
onMounted(() => {
  const user = localStorage.getItem('user');
  // console.log('User:', user);
  if (user) {
    // 已登录，显示仪表板
    currentPage.value = 'dashboard';
  }
});
</script>

<template>
  <LoginPage v-if="currentPage === 'login'" />
  <DashboardPage v-else-if="currentPage === 'dashboard'" />
</template>

<style scoped>
/* App根组件样式 */
</style>
