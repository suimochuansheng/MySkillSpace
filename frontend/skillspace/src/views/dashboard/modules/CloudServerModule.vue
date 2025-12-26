<template>
  <div class="cloud-server-module">
    <el-card class="module-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="card-title">云服务器监控 (Linux)</span>
            <el-tag :type="wsStatus === 'OPEN' ? 'success' : 'danger'" size="small">
              {{ wsStatus === 'OPEN' ? '已连接' : '未连接' }}
            </el-tag>
            <el-tag type="info" size="small">{{ serverName }}</el-tag>
          </div>
          <div class="header-right">
            <span class="update-time">更新时间: {{ lastUpdateTime }}</span>
          </div>
        </div>
      </template>

      <div class="module-content">
        <!-- 使用 Grid 布局 -->
        <div class="dashboard-grid">
          <!-- CPU 使用率图表 -->
          <el-card shadow="hover" class="chart-card">
            <div class="chart-header">
              <el-icon class="chart-icon cpu-icon"><Cpu /></el-icon>
              <span class="chart-title">CPU 使用率</span>
              <el-tag type="info" size="small">{{ cloudData.cpu.usage_percent }}%</el-tag>
            </div>
            <div ref="cpuChart" class="chart-container"></div>
            <div class="chart-info">
              <span>核心数: {{ cloudData.cpu.cores }}</span>
              <span>负载: {{ cloudData.cpu.load_avg_1 }}</span>
            </div>
          </el-card>

          <!-- 内存使用率图表 -->
          <el-card shadow="hover" class="chart-card">
            <div class="chart-header">
              <el-icon class="chart-icon memory-icon"><Coin /></el-icon>
              <span class="chart-title">内存使用率</span>
              <el-tag type="info" size="small">{{ cloudData.memory.usage_percent }}%</el-tag>
            </div>
            <div ref="memoryChart" class="chart-container"></div>
            <div class="chart-info">
              <span>已用: {{ formatBytes(cloudData.memory.used) }}</span>
              <span>可用: {{ formatBytes(cloudData.memory.available) }}</span>
              <span>总计: {{ formatBytes(cloudData.memory.total) }}</span>
            </div>
          </el-card>

          <!-- 磁盘使用情况 -->
          <el-card shadow="hover" class="chart-card">
            <div class="chart-header">
              <el-icon class="chart-icon disk-icon"><Folder /></el-icon>
              <span class="chart-title">磁盘使用情况</span>
              <el-tag type="info" size="small">{{ cloudData.disk.usage_percent }}%</el-tag>
            </div>
            <div ref="diskChart" class="chart-container"></div>
            <div class="chart-info">
              <span>已用: {{ formatBytes(cloudData.disk.used) }}</span>
              <span>总计: {{ formatBytes(cloudData.disk.total) }}</span>
            </div>
          </el-card>

          <!-- 网络流量趋势 -->
          <el-card shadow="hover" class="chart-card">
            <div class="chart-header">
              <el-icon class="chart-icon network-icon"><Connection /></el-icon>
              <span class="chart-title">网络流量趋势</span>
            </div>
            <div ref="networkChart" class="chart-container"></div>
            <div class="chart-info">
              <span>发送: {{ formatBytes(cloudData.network.bytes_sent) }}</span>
              <span>接收: {{ formatBytes(cloudData.network.bytes_recv) }}</span>
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
                <span class="label">主机名</span>
                <span class="value">{{ cloudData.system.hostname }}</span>
              </div>
              <div class="info-item">
                <span class="label">运行时间</span>
                <span class="value">{{ cloudData.system.uptime }}</span>
              </div>
              <div class="info-item">
                <span class="label">操作系统</span>
                <span class="value">Linux</span>
              </div>
              <div class="info-item">
                <span class="label">CPU负载 (1/5/15分钟)</span>
                <span class="value">{{ cloudData.cpu.load_avg_1 }} / {{ cloudData.cpu.load_avg_5 }} / {{ cloudData.cpu.load_avg_15 }}</span>
              </div>
            </div>
          </el-card>

          <!-- 服务状态卡片 -->
          <el-card shadow="hover" class="info-card-large">
            <div class="chart-header">
              <el-icon class="chart-icon service-icon"><DataAnalysis /></el-icon>
              <span class="chart-title">服务状态</span>
            </div>
            <div class="services-grid">
              <div
                v-for="service in cloudData.services"
                :key="service.name"
                class="service-item"
              >
                <div class="service-header">
                  <span class="service-name">{{ service.name }}</span>
                  <el-tag
                    :type="service.status === 'running' ? 'success' : 'danger'"
                    size="small"
                  >
                    {{ service.status === 'running' ? '运行中' : '已停止' }}
                  </el-tag>
                </div>
                <div class="service-info">
                  <span>类型: {{ service.type }}</span>
                  <span v-if="service.port">端口: {{ service.port }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- Docker容器卡片 -->
          <el-card shadow="hover" class="info-card-large" v-if="cloudData.containers.length > 0">
            <div class="chart-header">
              <el-icon class="chart-icon docker-icon"><Box /></el-icon>
              <span class="chart-title">Docker 容器</span>
              <el-tag type="info" size="small">{{ cloudData.containers.length }} 个</el-tag>
            </div>
            <div class="containers-grid">
              <div
                v-for="container in cloudData.containers"
                :key="container.container_id"
                class="container-item"
              >
                <div class="container-header">
                  <span class="container-name">{{ container.name }}</span>
                  <el-tag
                    :type="container.status === 'running' ? 'success' : 'warning'"
                    size="small"
                  >
                    {{ container.status }}
                  </el-tag>
                </div>
                <div class="container-info">
                  <span>镜像: {{ container.image }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Monitor,
  Cpu,
  Coin,
  Folder,
  Connection,
  DataAnalysis,
  Box
} from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import WebSocketManager from '@/utils/websocket';

// Props
const props = defineProps({
  serverName: {
    type: String,
    default: '示例生产服务器'
  }
});

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

// 云服务器数据
const cloudData = ref({
  timestamp: '',
  system: {
    hostname: '-',
    uptime: '-'
  },
  cpu: {
    usage_percent: 0,
    cores: 0,
    load_avg_1: 0,
    load_avg_5: 0,
    load_avg_15: 0
  },
  memory: {
    total: 0,
    used: 0,
    available: 0,
    usage_percent: 0
  },
  disk: {
    total: 0,
    used: 0,
    free: 0,
    usage_percent: 0
  },
  network: {
    bytes_sent: 0,
    bytes_recv: 0
  },
  services: [],
  containers: []
});

// 格式化字节数
const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
};

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

  // 磁盘图表（仪表盘）
  if (diskChart.value) {
    diskChartInstance = echarts.init(diskChart.value);
    diskChartInstance.setOption({
      tooltip: {
        formatter: '{b}: {c}%'
      },
      series: [{
        name: '磁盘使用率',
        type: 'gauge',
        progress: {
          show: true,
          width: 18
        },
        axisLine: {
          lineStyle: {
            width: 18
          }
        },
        axisTick: {
          show: false
        },
        splitLine: {
          length: 15,
          lineStyle: {
            width: 2,
            color: '#999'
          }
        },
        axisLabel: {
          distance: 25,
          color: '#999',
          fontSize: 12
        },
        anchor: {
          show: true,
          showAbove: true,
          size: 25,
          itemStyle: {
            borderWidth: 10
          }
        },
        title: {
          show: false
        },
        detail: {
          valueAnimation: true,
          fontSize: 20,
          offsetCenter: [0, '70%'],
          formatter: '{value}%'
        },
        data: [{
          value: 0,
          name: '磁盘使用率'
        }]
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
          formatter: function(value) {
            if (value >= 1024 * 1024 * 1024) {
              return (value / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
            } else if (value >= 1024 * 1024) {
              return (value / (1024 * 1024)).toFixed(2) + ' MB';
            } else if (value >= 1024) {
              return (value / 1024).toFixed(2) + ' KB';
            }
            return value + ' B';
          }
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
  if (diskChartInstance) {
    diskChartInstance.setOption({
      series: [{
        data: [{
          value: data.disk.usage_percent,
          name: '磁盘使用率'
        }]
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
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  // 动态获取主机地址，自动适配本地和云端
  const host = import.meta.env.VITE_WS_HOST || window.location.host;
  const url = `${protocol}//${host}/ws/monitor/cloud/${encodeURIComponent(props.serverName)}/`;

  wsManager = new WebSocketManager(url, {
    onOpen: () => {
      wsStatus.value = 'OPEN';
      ElMessage.success(`云服务器 ${props.serverName} 监控已连接`);
    },
    onMessage: (data) => {
      if (data.type === 'cloud_status' && data.data) {
        // 防御性检查：确保数据结构完整
        if (!data.data.cpu || !data.data.memory || !data.data.disk || !data.data.network) {
          console.error('云监控数据格式不完整:', data.data);
          return;
        }

        cloudData.value = data.data;
        lastUpdateTime.value = data.data.timestamp || new Date().toLocaleTimeString();
        updateCharts(data.data);
      }
    },
    onClose: () => {
      wsStatus.value = 'CLOSED';
    },
    onError: (error) => {
      console.error('WebSocket错误:', error);
      ElMessage.error(`云服务器 ${props.serverName} 监控连接失败`);
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
.cloud-server-module {
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

.service-icon {
  color: #f56c6c;
}

.docker-icon {
  color: #2496ed;
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

.info-item .label {
  font-size: 13px;
  color: #909399;
}

.info-item .value {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

/* 服务状态网格 */
.services-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.service-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background-color: #fafafa;
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.service-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.service-info {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #606266;
}

/* Docker容器网格 */
.containers-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.container-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background-color: #f0f9ff;
}

.container-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.container-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  font-family: 'Courier New', monospace;
}

.container-info {
  font-size: 12px;
  color: #606266;
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

  .services-grid {
    grid-template-columns: 1fr;
  }
}
</style>
