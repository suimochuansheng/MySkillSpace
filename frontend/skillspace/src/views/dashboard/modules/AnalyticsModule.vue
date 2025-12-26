<template>
  <div class="analytics-module">
    <el-card class="module-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="card-title">实时系统监控</span>
            <el-tag :type="wsStatus === 'OPEN' ? 'success' : 'danger'" size="small">
              {{ wsStatus === 'OPEN' ? '已连接' : '未连接' }}
            </el-tag>
          </div>
          <div class="header-right">
            <span class="update-time">更新时间: {{ lastUpdateTime }}</span>
          </div>
        </div>
      </template>

      <div class="module-content">
        <!-- Linux环境提示信息 -->
        <div v-if="isLinuxEnvironment" class="environment-notice">
          <el-result
            icon="info"
            title="Windows系统监控"
            sub-title="此功能仅在Windows开发环境可用"
          >
            <template #extra>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="当前系统">{{ systemData.system.platform }}</el-descriptions-item>
                <el-descriptions-item label="主机名">{{ systemData.system.hostname }}</el-descriptions-item>
                <el-descriptions-item label="说明">
                  当前服务器运行在 {{ systemData.system.platform }} 环境下。如需查看本服务器监控数据，请访问"云服务器监控"标签页。
                </el-descriptions-item>
              </el-descriptions>
            </template>
          </el-result>
        </div>

        <!-- Windows环境正常显示监控数据 -->
        <div v-else class="dashboard-grid">
          <!-- CPU 使用率图表 -->
          <el-card shadow="hover" class="chart-card">
            <div class="chart-header">
              <el-icon class="chart-icon cpu-icon"><Cpu /></el-icon>
              <span class="chart-title">CPU 使用率</span>
              <el-tag type="info" size="small">{{ systemData.cpu.usage_percent }}%</el-tag>
            </div>
            <div ref="cpuChart" class="chart-container"></div>
            <div class="chart-info">
              <span>核心: {{ systemData.cpu.physical_cores }}物理 / {{ systemData.cpu.logical_cores }}逻辑</span>
              <span>频率: {{ systemData.cpu.current_freq }} MHz</span>
            </div>
          </el-card>

          <!-- 内存使用率图表 -->
          <el-card shadow="hover" class="chart-card">
            <div class="chart-header">
              <el-icon class="chart-icon memory-icon"><Coin /></el-icon>
              <span class="chart-title">内存使用率</span>
              <el-tag type="info" size="small">{{ systemData.memory.usage_percent }}%</el-tag>
            </div>
            <div ref="memoryChart" class="chart-container"></div>
            <div class="chart-info">
              <span>已用: {{ systemData.memory.used }} GB</span>
              <span>可用: {{ systemData.memory.available }} GB</span>
              <span>总计: {{ systemData.memory.total }} GB</span>
            </div>
          </el-card>

          <!-- 磁盘使用情况 -->
          <el-card shadow="hover" class="chart-card">
            <div class="chart-header">
              <el-icon class="chart-icon disk-icon"><Folder /></el-icon>
              <span class="chart-title">磁盘使用情况</span>
            </div>
            <div ref="diskChart" class="chart-container"></div>
          </el-card>

          <!-- 网络流量趋势 -->
          <el-card shadow="hover" class="chart-card">
            <div class="chart-header">
              <el-icon class="chart-icon network-icon"><Connection /></el-icon>
              <span class="chart-title">网络流量趋势</span>
            </div>
            <div ref="networkChart" class="chart-container"></div>
            <div class="chart-info">
              <span>发送: {{ systemData.network.bytes_sent }} GB</span>
              <span>接收: {{ systemData.network.bytes_recv }} GB</span>
            </div>
          </el-card>

          <!-- 系统信息卡片 -->
          <el-card shadow="hover" class="info-card-large">
            <div class="chart-header">
              <el-icon class="chart-icon system-icon"><Monitor /></el-icon>
              <span class="chart-title">系统信息</span>
            </div>
            <div class="system-info-grid">
              <div class="info-item">
                <span class="label">操作系统</span>
                <span class="value">{{ systemData.system.platform }} {{ systemData.system.platform_release }}</span>
              </div>
              <div class="info-item">
                <span class="label">主机名</span>
                <span class="value">{{ systemData.system.hostname }}</span>
              </div>
              <div class="info-item">
                <span class="label">架构</span>
                <span class="value">{{ systemData.system.architecture }}</span>
              </div>
              <div class="info-item">
                <span class="label">运行时间</span>
                <span class="value">{{ systemData.system.uptime }}</span>
              </div>
              <div class="info-item">
                <span class="label">处理器</span>
                <span class="value">{{ systemData.system.processor }}</span>
              </div>
              <div class="info-item">
                <span class="label">启动时间</span>
                <span class="value">{{ systemData.system.boot_time }}</span>
              </div>
            </div>
          </el-card>

          <!-- 数据库状态卡片 -->
          <el-card shadow="hover" class="info-card-large">
            <div class="chart-header">
              <el-icon class="chart-icon database-icon"><DataAnalysis /></el-icon>
              <span class="chart-title">数据库状态</span>
            </div>
            <div class="system-info-grid">
              <div class="info-item full-width">
                <span class="label">数据库名称</span>
                <span class="value">{{ systemData.database.database_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">连接状态</span>
                <el-tag :type="systemData.database.status === 'connected' ? 'success' : 'danger'" size="small">
                  {{ systemData.database.status === 'connected' ? '已连接' : '断开' }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="label">数据库大小</span>
                <span class="value">{{ systemData.database.size || '-' }}</span>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Monitor,
  Cpu,
  Coin,
  Folder,
  Connection,
  DataAnalysis
} from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import { createMonitorWebSocket } from '@/utils/websocket';

// WebSocket 状态
const wsStatus = ref('CLOSED');
const lastUpdateTime = ref('-');
let wsManager = null;

// ECharts 实例
const cpuChart = ref(null);
const memoryChart = ref(null);
const diskChart = ref(null);
const networkChart = ref(null);

let cpuChartInstance = null;
let memoryChartInstance = null;
let diskChartInstance = null;
let networkChartInstance = null;

// 历史数据（用于趋势图）
const cpuHistory = ref([]);
const memoryHistory = ref([]);
const networkHistory = ref({ sent: [], recv: [], time: [] });
const maxHistoryLength = 30; // 保留最近30个数据点

// 系统数据
const systemData = ref({
  timestamp: '',
  system: {
    platform: '',
    platform_release: '',
    hostname: '',
    architecture: '',
    uptime: '',
    processor: '',
    boot_time: ''
  },
  cpu: {
    usage_percent: 0,
    physical_cores: 0,
    logical_cores: 0,
    current_freq: 0,
    per_core_usage: []
  },
  memory: {
    total: 0,
    used: 0,
    available: 0,
    usage_percent: 0
  },
  disk: {
    partitions: []
  },
  network: {
    bytes_sent: 0,
    bytes_recv: 0,
    packets_sent: 0,
    packets_recv: 0
  },
  database: {
    database_name: '',
    status: '',
    size: ''
  }
});

// 判断是否为Linux环境
const isLinuxEnvironment = computed(() => {
  return systemData.value.system.platform === 'Linux';
});

// 初始化 ECharts
const initCharts = () => {
  // CPU 图表
  if (cpuChart.value) {
    cpuChartInstance = echarts.init(cpuChart.value);
    cpuChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}%'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: []
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [{
        name: 'CPU使用率',
        type: 'line',
        smooth: true,
        data: [],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        },
        lineStyle: {
          color: '#409eff'
        },
        itemStyle: {
          color: '#409eff'
        }
      }]
    });
  }

  // 内存图表
  if (memoryChart.value) {
    memoryChartInstance = echarts.init(memoryChart.value);
    memoryChartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}%'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: []
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [{
        name: '内存使用率',
        type: 'line',
        smooth: true,
        data: [],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        },
        lineStyle: {
          color: '#67c23a'
        },
        itemStyle: {
          color: '#67c23a'
        }
      }]
    });
  }

  // 磁盘图表（饼图）
  if (diskChart.value) {
    diskChartInstance = echarts.init(diskChart.value);
    diskChartInstance.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} GB ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: []
      },
      series: [{
        name: '磁盘使用',
        type: 'pie',
        radius: '60%',
        center: ['60%', '50%'],
        data: [],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    });
  }

  // 网络流量图表
  if (networkChart.value) {
    networkChartInstance = echarts.init(networkChart.value);
    networkChartInstance.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['发送', '接收']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: []
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value} GB'
        }
      },
      series: [
        {
          name: '发送',
          type: 'line',
          smooth: true,
          data: [],
          lineStyle: {
            color: '#f56c6c'
          },
          itemStyle: {
            color: '#f56c6c'
          }
        },
        {
          name: '接收',
          type: 'line',
          smooth: true,
          data: [],
          lineStyle: {
            color: '#409eff'
          },
          itemStyle: {
            color: '#409eff'
          }
        }
      ]
    });
  }
};

// 更新图表数据
const updateCharts = (data) => {
  // 更新 CPU 图表
  if (cpuChartInstance) {
    cpuHistory.value.push({
      time: new Date().toLocaleTimeString(),
      value: data.cpu.usage_percent
    });

    if (cpuHistory.value.length > maxHistoryLength) {
      cpuHistory.value.shift();
    }

    cpuChartInstance.setOption({
      xAxis: {
        data: cpuHistory.value.map(item => item.time)
      },
      series: [{
        data: cpuHistory.value.map(item => item.value)
      }]
    });
  }

  // 更新内存图表
  if (memoryChartInstance) {
    memoryHistory.value.push({
      time: new Date().toLocaleTimeString(),
      value: data.memory.usage_percent
    });

    if (memoryHistory.value.length > maxHistoryLength) {
      memoryHistory.value.shift();
    }

    memoryChartInstance.setOption({
      xAxis: {
        data: memoryHistory.value.map(item => item.time)
      },
      series: [{
        data: memoryHistory.value.map(item => item.value)
      }]
    });
  }

  // 更新磁盘图表
  if (diskChartInstance && data.disk.partitions.length > 0) {
    const diskData = data.disk.partitions.map(disk => ({
      name: disk.mountpoint,
      value: disk.used
    }));

    diskChartInstance.setOption({
      legend: {
        data: data.disk.partitions.map(disk => disk.mountpoint)
      },
      series: [{
        data: diskData
      }]
    });
  }

  // 更新网络流量图表
  if (networkChartInstance) {
    const currentTime = new Date().toLocaleTimeString();
    networkHistory.value.time.push(currentTime);
    networkHistory.value.sent.push(data.network.bytes_sent);
    networkHistory.value.recv.push(data.network.bytes_recv);

    if (networkHistory.value.time.length > maxHistoryLength) {
      networkHistory.value.time.shift();
      networkHistory.value.sent.shift();
      networkHistory.value.recv.shift();
    }

    networkChartInstance.setOption({
      xAxis: {
        data: networkHistory.value.time
      },
      series: [
        { data: networkHistory.value.sent },
        { data: networkHistory.value.recv }
      ]
    });
  }
};

// 连接 WebSocket
const connectWebSocket = () => {
  wsManager = createMonitorWebSocket({
    onOpen: () => {
      wsStatus.value = 'OPEN';
      ElMessage.success('系统监控服务已连接');
    },
    onMessage: (data) => {
      if (data.type === 'system_status' && data.data) {
        systemData.value = data.data;
        lastUpdateTime.value = data.data.timestamp || new Date().toLocaleTimeString();
        updateCharts(data.data);
      }
    },
    onClose: () => {
      wsStatus.value = 'CLOSED';
    },
    onError: (error) => {
      console.error('WebSocket错误:', error);
      ElMessage.error('系统监控服务连接失败');
    }
  });

  wsManager.connect();
};

// 窗口大小改变时调整图表
const handleResize = () => {
  cpuChartInstance?.resize();
  memoryChartInstance?.resize();
  diskChartInstance?.resize();
  networkChartInstance?.resize();
};

onMounted(() => {
  nextTick(() => {
    initCharts();
    connectWebSocket();
    window.addEventListener('resize', handleResize);
  });
});

onUnmounted(() => {
  // 关闭 WebSocket
  wsManager?.close();

  // 销毁图表
  cpuChartInstance?.dispose();
  memoryChartInstance?.dispose();
  diskChartInstance?.dispose();
  networkChartInstance?.dispose();

  // 移除事件监听
  window.removeEventListener('resize', handleResize);
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

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.update-time {
  font-size: 13px;
  color: #909399;
}

.module-content {
  min-height: 500px;
}

/* 环境提示信息 */
.environment-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 40px 20px;
}

.environment-notice :deep(.el-result__title) {
  font-size: 24px;
  margin-top: 20px;
}

.environment-notice :deep(.el-result__subtitle) {
  font-size: 16px;
  margin-top: 12px;
}

.environment-notice :deep(.el-descriptions) {
  max-width: 600px;
  margin-top: 20px;
}

/* Grid 布局 */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

/* 图表卡片 */
.chart-card {
  min-height: 350px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.chart-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.chart-icon {
  font-size: 22px;
}

.cpu-icon {
  color: #409eff;
}

.memory-icon {
  color: #67c23a;
}

.disk-icon {
  color: #e6a23c;
}

.network-icon {
  color: #909399;
}

.system-icon {
  color: #409eff;
}

.database-icon {
  color: #f56c6c;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.chart-container {
  width: 100%;
  height: 220px;
}

.chart-info {
  display: flex;
  justify-content: space-around;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  font-size: 13px;
  color: #606266;
}

/* 信息卡片 */
.info-card-large {
  min-height: 250px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.info-card-large:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.system-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item .label {
  font-size: 13px;
  color: #909399;
}

.info-item .value {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
