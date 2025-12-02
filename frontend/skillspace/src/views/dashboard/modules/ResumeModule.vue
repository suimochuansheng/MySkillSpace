<template>
  <div class="resume-module">
    <el-card class="module-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">简历管理</span>
          <el-button type="primary" size="small" @click="handleAddResume">
            <el-icon><Plus /></el-icon>
            新增简历
          </el-button>
        </div>
      </template>

      <div class="module-content">
        <el-table 
          v-loading="loading"
          :data="resumeList" 
          style="width: 100%"
          stripe
        >
          <el-table-column prop="name" label="姓名" width="150" />
          <el-table-column prop="position" label="职位" width="180" />
          <el-table-column prop="education" label="教育背景" show-overflow-tooltip />
          <el-table-column prop="skills" label="技能" show-overflow-tooltip />
          <el-table-column label="操作" width="200" align="center">
            <template #default="scope">
              <el-button size="small" @click="handleView(scope.row)">查看</el-button>
              <el-button size="small" type="primary" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="!loading && resumeList.length === 0" class="empty-state">
          <el-empty description="暂无简历数据，点击上方按钮新增简历" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { http } from '@/api';

const loading = ref(false);
const resumeList = ref([]);

// 获取简历列表
const fetchResumeList = async () => {
  loading.value = true;
  try {
    const response = await http.get('/api/resume/');
    resumeList.value = response;
    ElMessage.success('简历数据加载成功');
  } catch (error) {
    console.error('获取简历列表失败:', error);
    ElMessage.error('获取简历列表失败');
  } finally {
    loading.value = false;
  }
};

// 新增简历
const handleAddResume = () => {
  ElMessage.info('新增简历功能开发中...');
};

// 查看简历
const handleView = (row) => {
  ElMessage.info(`查看简历: ${row.name}`);
};

// 编辑简历
const handleEdit = (row) => {
  ElMessage.info(`编辑简历: ${row.name}`);
};

// 删除简历
const handleDelete = (row) => {
  ElMessage.info(`删除简历: ${row.name}`);
};

onMounted(() => {
  fetchResumeList();
});
</script>

<style scoped>
.resume-module {
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

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>
