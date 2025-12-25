<template>
  <div class="home-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2>欢迎使用 SkillSpace 技能空间</h2>
        <p>这是您的个人技能展示与管理平台</p>
      </el-col>
    </el-row>

    <!-- 快捷入口 -->
    <el-row :gutter="20" style="margin-top: 30px;">
      <el-col :span="6" v-for="card in quickCards" :key="card.path">
        <el-card class="quick-card" shadow="hover" @click="navigateTo(card.path)">
          <div class="card-content">
            <el-icon :size="48" :color="card.color">
              <component :is="card.icon" />
            </el-icon>
            <h3>{{ card.title }}</h3>
            <p>{{ card.desc }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { Document, List, DataAnalysis, ChatDotRound } from '@element-plus/icons-vue';

const router = useRouter();

const quickCards = ref([
  { title: 'AI简历诊断', desc: '智能分析简历', path: '/resume', icon: 'Document', color: '#409EFF' },
  { title: '任务中心', desc: '管理您的任务', path: '/tasks', icon: 'List', color: '#67C23A' },
  { title: '系统监控', desc: '查看系统状态', path: '/monitor', icon: 'DataAnalysis', color: '#E6A23C' },
  { title: 'AI助手', desc: '智能对话助手', path: '/ai', icon: 'ChatDotRound', color: '#F56C6C' }
]);

const navigateTo = (path) => {
  router.push(path);
};
</script>

<style scoped>
.home-page {
  padding: 20px;
}

.quick-card {
  cursor: pointer;
  transition: all 0.3s;
  height: 180px;
}

.quick-card:hover {
  transform: translateY(-5px);
}

.card-content {
  text-align: center;
  padding: 20px;
}

.card-content h3 {
  margin: 15px 0 10px;
  font-size: 18px;
}

.card-content p {
  color: #909399;
  font-size: 14px;
}
</style>
