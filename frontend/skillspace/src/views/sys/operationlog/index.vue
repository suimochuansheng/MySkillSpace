<template>
  <div class="operation-log-management">
    <el-card class="page-header">
      <div class="header-actions">
        <h2>操作日志</h2>
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

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="操作人">
          <el-input v-model="searchForm.username" placeholder="请输入操作人账号" clearable />
        </el-form-item>
        <el-form-item label="操作模块">
          <el-input v-model="searchForm.module" placeholder="请输入操作模块" clearable />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="searchForm.action" placeholder="选择操作类型" clearable>
            <el-option label="新增" value="新增" />
            <el-option label="修改" value="修改" />
            <el-option label="删除" value="删除" />
            <el-option label="查询" value="查询" />
            <el-option label="导出" value="导出" />
            <el-option label="登录" value="登录" />
            <el-option label="登出" value="登出" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作状态">
          <el-select v-model="searchForm.status" placeholder="选择操作状态" clearable>
            <el-option label="成功" value="0" />
            <el-option label="失败" value="1" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作日志列表 -->
    <el-card class="table-card">
      <el-table :data="logList" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column prop="module" label="操作模块" width="120" />
        <el-table-column prop="action" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="method" label="请求方法" width="100" />
        <el-table-column prop="url" label="请求URL" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '0' ? 'success' : 'danger'">
              {{ row.status === '0' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时(ms)" width="100" />
        <el-table-column prop="created_at" label="操作时间" width="180" />
        <el-table-column label="操作" width="120" fixed="right">
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
      title="操作日志详情"
      width="700px"
    >
      <el-descriptions :column="1" border v-if="currentLog">
        <el-descriptions-item label="操作ID">{{ currentLog.id }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ currentLog.username }}</el-descriptions-item>
        <el-descriptions-item label="操作模块">{{ currentLog.module }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getActionType(currentLog.action)">{{ currentLog.action }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作描述">{{ currentLog.description }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">{{ currentLog.method }}</el-descriptions-item>
        <el-descriptions-item label="请求URL">{{ currentLog.url }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentLog.ip_address }}</el-descriptions-item>
        <el-descriptions-item label="浏览器">{{ currentLog.user_agent }}</el-descriptions-item>
        <el-descriptions-item label="请求参数">
          <el-input
            v-model="currentLog.request_params"
            type="textarea"
            :rows="3"
            readonly
          />
        </el-descriptions-item>
        <el-descriptions-item label="响应数据">
          <el-input
            v-model="currentLog.response_data"
            type="textarea"
            :rows="3"
            readonly
          />
        </el-descriptions-item>
        <el-descriptions-item label="操作状态">
          <el-tag :type="currentLog.status === '0' ? 'success' : 'danger'">
            {{ currentLog.status === '0' ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" v-if="currentLog.error_msg">
          <el-input
            v-model="currentLog.error_msg"
            type="textarea"
            :rows="2"
            readonly
          />
        </el-descriptions-item>
        <el-descriptions-item label="执行耗时">{{ currentLog.duration }}ms</el-descriptions-item>
        <el-descriptions-item label="操作时间">{{ currentLog.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Refresh } from '@element-plus/icons-vue'
import { operationLogManagement } from '@/api/auth'

// 数据状态
const loading = ref(false)
const logList = ref([])
const searchForm = reactive({
  username: '',
  module: '',
  action: '',
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

// 获取操作日志列表
const fetchLogList = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.pageSize
    }
    const response = await operationLogManagement.getList(params)

    if (response.results) {
      logList.value = response.results
      pagination.total = response.count || 0
    } else {
      logList.value = Array.isArray(response) ? response : []
      pagination.total = logList.value.length
    }
  } catch (error) {
    console.error('获取操作日志失败:', error)
    ElMessage.error(error.message || '获取操作日志失败')
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
  searchForm.module = ''
  searchForm.action = ''
  searchForm.status = ''
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
    // 暂时只弹出提示
    ElMessage.success('导出功能开发中...')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

// 查看详情
const handleDetail = async (row) => {
  try {
    currentLog.value = row
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取详情失败: ' + error.message)
  }
}

// 获取操作类型的标签类型
const getActionType = (action) => {
  const typeMap = {
    '新增': 'success',
    '修改': 'info',
    '删除': 'danger',
    '查询': 'primary',
    '导出': 'warning',
    '导入': 'warning',
    '登录': 'success',
    '登出': 'info',
    '其他': 'info'
  }
  return typeMap[action] || 'info'
}

// 初始化
onMounted(() => {
  fetchLogList()
})
</script>

<style scoped>
.operation-log-management {
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
