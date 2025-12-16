<template>
  <div class="login-log-management">
    <el-card class="page-header">
      <div class="header-actions">
        <h2>登录日志</h2>
        <div class="header-buttons">
          <el-button type="primary" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          <el-button @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :xs="24" :sm="12" :md="6">
        <el-statistic title="今日登录" :value="todayLoginCount" />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-statistic title="登录成功" :value="successCount" />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-statistic title="登录失败" :value="failureCount" />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-statistic title="异常登录" :value="abnormalCount" />
      </el-col>
    </el-row>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="登录账号">
          <el-input v-model="searchForm.username" placeholder="请输入登录账号" clearable />
        </el-form-item>
        <el-form-item label="登录IP">
          <el-input v-model="searchForm.ip_address" placeholder="请输入登录IP" clearable />
        </el-form-item>
        <el-form-item label="登录状态">
          <el-select v-model="searchForm.status" placeholder="选择登录状态" clearable>
            <el-option label="成功" value="0" />
            <el-option label="失败" value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="登录时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 登录日志列表 -->
    <el-card class="table-card">
      <el-table :data="logList" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="登录账号" width="120" />
        <el-table-column prop="ip_address" label="登录IP" width="140" />
        <el-table-column prop="login_location" label="登录地点" width="140" />
        <el-table-column prop="browser" label="浏览器" width="120" />
        <el-table-column prop="os" label="操作系统" width="120" />
        <el-table-column prop="device" label="设备类型" width="100" />
        <el-table-column prop="status" label="登录状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '0' ? 'success' : 'danger'">
              {{ row.status === '0' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="msg" label="提示信息" show-overflow-tooltip />
        <el-table-column prop="login_time" label="登录时间" width="180" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchLogList"
        @current-change="fetchLogList"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="登录日志详情"
      width="600px"
    >
      <el-descriptions :column="1" border v-if="currentLog">
        <el-descriptions-item label="日志ID">{{ currentLog.id }}</el-descriptions-item>
        <el-descriptions-item label="登录账号">{{ currentLog.username }}</el-descriptions-item>
        <el-descriptions-item label="登录IP">
          <el-link type="primary">{{ currentLog.ip_address }}</el-link>
        </el-descriptions-item>
        <el-descriptions-item label="登录地点">{{ currentLog.login_location }}</el-descriptions-item>
        <el-descriptions-item label="浏览器">{{ currentLog.browser }}</el-descriptions-item>
        <el-descriptions-item label="操作系统">{{ currentLog.os }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentLog.device }}</el-descriptions-item>
        <el-descriptions-item label="登录状态">
          <el-tag :type="currentLog.status === '0' ? 'success' : 'danger'">
            {{ currentLog.status === '0' ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提示信息">{{ currentLog.msg }}</el-descriptions-item>
        <el-descriptions-item label="登录时间">{{ currentLog.login_time }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Refresh } from '@element-plus/icons-vue'
import { loginLogManagement } from '@/api/auth'

// 数据状态
const loading = ref(false)
const logList = ref([])
const dateRange = ref(null)
const searchForm = reactive({
  username: '',
  ip_address: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 详情对话框
const detailDialogVisible = ref(false)
const currentLog = ref(null)

// 计算统计数据
const todayLoginCount = computed(() => {
  // 实际应该根据日期过滤，这里仅演示
  return logList.value.length
})

const successCount = computed(() => {
  return logList.value.filter(log => log.status === '0').length
})

const failureCount = computed(() => {
  return logList.value.filter(log => log.status === '1').length
})

const abnormalCount = computed(() => {
  // 可以自定义异常条件，比如同一IP频繁失败登录
  return 0
})

// 获取登录日志列表
const fetchLogList = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.pageSize
    }
    const response = await loginLogManagement.getList(params)

    if (response.results) {
      logList.value = response.results
      pagination.total = response.count || 0
    } else {
      logList.value = Array.isArray(response) ? response : []
      pagination.total = logList.value.length
    }
  } catch (error) {
    console.error('获取登录日志失败:', error)
    ElMessage.error(error.message || '获取登录日志失败')
    logList.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchLogList()
}

// 重置
const handleReset = () => {
  searchForm.username = ''
  searchForm.ip_address = ''
  searchForm.status = ''
  dateRange.value = null
  handleSearch()
}

// 刷新
const handleRefresh = () => {
  fetchLogList()
}

// 导出
const handleExport = async () => {
  try {
    ElMessage.info('正在生成导出文件，请稍候...')
    // 这里可以调用后端导出接口
    ElMessage.success('导出功能开发中...')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

// 查看详情
const handleDetail = (row) => {
  currentLog.value = row
  detailDialogVisible.value = true
}

// 初始化
onMounted(() => {
  fetchLogList()
})
</script>

<style scoped>
.login-log-management {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.el-pagination {
  margin-top: 20px;
  text-align: right;
}
</style>
