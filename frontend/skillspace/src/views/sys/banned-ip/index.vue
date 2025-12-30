<template>
  <div class="banned-ip-management">
    <el-card class="page-header">
      <div class="header-actions">
        <h2>封禁IP管理</h2>
        <div class="header-buttons">
          <el-button type="primary" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :xs="24" :sm="8">
        <el-statistic title="当前封禁IP数量" :value="bannedIPList.length" />
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-statistic title="封禁规则" value="5次失败/10分钟" />
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-statistic title="封禁时长" value="1小时" />
      </el-col>
    </el-row>

    <!-- 封禁IP列表 -->
    <el-card class="table-card">
      <el-alert
        v-if="!fail2banAvailable"
        title="fail2ban未配置"
        type="warning"
        description="服务器上未安装或未配置fail2ban服务，无法查看封禁IP列表。请联系管理员配置。"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <el-table :data="bannedIPList" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="ip" label="封禁IP" width="180">
          <template #default="{ row }">
            <el-tag type="danger" effect="dark">{{ row.ip }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="banned_at" label="封禁时间" width="180" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag type="warning" v-if="row.status === 'banned'">已封禁</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="说明">
          <template #default="{ row }">
            <span>该IP因连续登录失败次数过多被系统自动封禁，封禁时长1小时后自动解除</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              @click="handleUnban(row)"
              :loading="unbanLoading[row.ip]"
            >
              解封
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && bannedIPList.length === 0" description="暂无封禁IP" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

// 数据
const bannedIPList = ref([])
const loading = ref(false)
const unbanLoading = reactive({}) // 每个IP的解封loading状态
const fail2banAvailable = ref(true)

// 获取封禁IP列表
const fetchBannedIPs = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/auth/banned-ips/')

    if (response.data.code === 200) {
      bannedIPList.value = response.data.data || []

      // 检查fail2ban是否可用
      if (response.data.message &&
          (response.data.message.includes('未安装') ||
           response.data.message.includes('未配置') ||
           response.data.message.includes('未启用'))) {
        fail2banAvailable.value = false
      } else {
        fail2banAvailable.value = true
      }

      ElMessage.success(response.data.message || '查询成功')
    }
  } catch (error) {
    console.error('获取封禁IP失败:', error)
    ElMessage.error(error.response?.data?.message || '获取封禁IP列表失败')
    fail2banAvailable.value = false
  } finally {
    loading.value = false
  }
}

// 解封IP
const handleUnban = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要解封IP: ${row.ip} 吗？解封后该IP可以立即访问系统。`,
      '解封确认',
      {
        confirmButtonText: '确定解封',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 设置该IP的loading状态
    unbanLoading[row.ip] = true

    const response = await axios.post('/api/auth/banned-ips/unban/', {
      ip: row.ip
    })

    if (response.data.code === 200) {
      ElMessage.success(response.data.message || '解封成功')
      // 刷新列表
      await fetchBannedIPs()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('解封IP失败:', error)
      ElMessage.error(error.response?.data?.message || '解封失败')
    }
  } finally {
    unbanLoading[row.ip] = false
  }
}

// 刷新
const handleRefresh = () => {
  fetchBannedIPs()
}

// 初始化
onMounted(() => {
  fetchBannedIPs()
})
</script>

<style scoped>
.banned-ip-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.table-card {
  margin-top: 20px;
}
</style>
