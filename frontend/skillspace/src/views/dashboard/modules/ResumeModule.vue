<template>
  <div class="resume-diagnose-container">
    <el-row :gutter="20">
      
      <!-- 左侧：输入区域 -->
      <el-col :xs="24" :md="10" :lg="8">
        <el-card class="input-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🚀 AI 简历诊断工作台</span>
            </div>
          </template>

          <el-form ref="formRef" :model="form" label-position="top">
            
            <!-- 1. 文件上传 -->
            <el-form-item label="第一步：上传简历 (PDF/TXT)" required>
              <el-upload
                class="upload-demo"
                drag
                action="#"
                :auto-upload="false"
                :limit="1"
                :on-change="handleFileChange"
                :on-exceed="handleExceed"
                :before-upload="beforeUpload"
                accept=".pdf,.txt"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处 或 <em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    限制 PDF/TXT 格式，< 5MB
                  </div>
                </template>
              </el-upload>
              <!-- 文件预览 -->
              <div v-if="form.file" class="file-preview">
                <el-tag type="success" closable @close="clearFile" effect="dark">
                  📄 {{ form.file.name }}
                </el-tag>
              </div>
            </el-form-item>

            <!-- 2. JD 输入 -->
            <el-form-item label="第二步：输入目标岗位 (JD)" required>
              <el-input
                v-model="form.jdText"
                type="textarea"
                :rows="8"
                placeholder="请粘贴 JD 内容。AI 将分析简历与该岗位的匹配度..."
                maxlength="2000"
                show-word-limit
              />
            </el-form-item>

            <!-- 3. 提交按钮 -->
            <el-button 
              type="primary" 
              size="large" 
              class="submit-btn" 
              :loading="loading" 
              @click="handleSubmit"
              :disabled="!form.file || !form.jdText"
            >
              {{ loading ? '正在连接阿里云 Qwen 进行分析...' : '开始智能诊断' }}
            </el-button>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：分析结果区域 -->
      <el-col :xs="24" :md="14" :lg="16">
        <div v-loading="loading" element-loading-text="AI 正在深度阅读您的简历..." class="result-wrapper">

          <!-- 分析报告 - 始终显示 -->
          <div class="report-content">
            
            <!-- 头部评分卡 -->
            <el-card class="score-card" shadow="never">
              <div class="score-header">
                <div class="score-circle">
                  <el-progress
                    type="dashboard"
                    :percentage="result?.score || 0"
                    :color="scoreColor"
                    :width="120"
                    :stroke-width="10"
                  >
                    <template #default="{ percentage }">
                      <span class="score-num">{{ percentage }}</span>
                      <span class="score-label">匹配分</span>
                    </template>
                  </el-progress>
                </div>
                <div class="score-summary">
                  <h3>🤖 AI 综合评价</h3>
                  <p v-if="result">{{ result.summary }}</p>
                  <p v-else class="placeholder-text">请上传简历并输入 JD，开始诊断后 AI 将为您生成综合评价...</p>
                </div>
              </div>
            </el-card>

            <!-- 优缺点分析 -->
            <el-row :gutter="15" class="mt-20">
              <el-col :span="12">
                <el-card class="pros-cons-card" shadow="hover">
                  <template #header>
                    <span class="text-success"><el-icon><CircleCheckFilled /></el-icon> 核心亮点</span>
                  </template>
                  <ul v-if="result && result.pros && result.pros.length > 0">
                    <li v-for="(item, index) in result.pros" :key="index">{{ item }}</li>
                  </ul>
                  <div v-else class="placeholder-text">
                    AI 将分析您的简历亮点，包括：
                    <ul>
                      <li>与岗位匹配的技能优势</li>
                      <li>突出的项目经验</li>
                      <li>相关的工作背景</li>
                    </ul>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="pros-cons-card" shadow="hover">
                  <template #header>
                    <span class="text-danger"><el-icon><CircleCloseFilled /></el-icon> 潜在风险</span>
                  </template>
                  <ul v-if="result && result.cons && result.cons.length > 0">
                    <li v-for="(item, index) in result.cons" :key="index">{{ item }}</li>
                  </ul>
                  <div v-else class="placeholder-text">
                    AI 将识别简历中的改进空间，例如：
                    <ul>
                      <li>技能缺口分析</li>
                      <li>经验不足的领域</li>
                      <li>表述可优化的部分</li>
                    </ul>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 详细建议 -->
            <el-card class="mt-20 suggestions-card" shadow="hover">
              <template #header>
                <span>💡 改进建议与行动指南</span>
              </template>
              <div v-if="result && result.suggestions" class="suggestion-text" v-html="formattedSuggestions"></div>
              <div v-else class="placeholder-text">
                <p>AI 将根据简历与 JD 的对比，为您提供针对性的改进建议：</p>
                <ul>
                  <li>📝 简历内容优化方向</li>
                  <li>🎯 技能提升建议</li>
                  <li>✨ 亮点包装技巧</li>
                  <li>🔧 格式与排版改进</li>
                </ul>
              </div>
            </el-card>

          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UploadFilled, CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from 'element-plus'
import { diagnoseResume } from '@/api/resume'

const loading = ref(false)
const form = ref({ file: null, jdText: '' })
const result = ref(null)

// 颜色根据分数变化
const scoreColor = computed(() => {
  // 强制转为数字，防止 NaN
  const s = Number(result.value?.score) || 0
  if (s < 60) return '#F56C6C'
  if (s < 80) return '#E6A23C'
  return '#67C23A'
})

// 安全地处理建议文本（防止后端返回非字符串导致 .replace 报错）
const formattedSuggestions = computed(() => {
  const raw = result.value?.suggestions
  if (!raw) return '暂无建议'
  
  // 如果 AI 返回的是数组，自动连接成字符串
  if (Array.isArray(raw)) {
    return raw.join('<br/>')
  }
  
  // 强制转字符串再 replace
  return String(raw).replace(/\n/g, '<br/>')
})

const handleFileChange = (uploadFile) => {
  const rawFile = uploadFile.raw
  if (rawFile.type !== 'application/pdf' && rawFile.type !== 'text/plain') {
    ElMessage.error('仅支持 PDF 或 TXT 文件')
    form.value.file = null
    return
  }
  if (rawFile.size / 1024 / 1024 > 5) {
    ElMessage.error('文件大小需小于 5MB')
    form.value.file = null
    return
  }
  form.value.file = rawFile
}

const handleExceed = () => ElMessage.warning('请删除旧文件后重新上传')
const clearFile = () => form.value.file = null
const beforeUpload = () => false

const handleSubmit = async () => {
  loading.value = true
  result.value = null
  try {
    const fd = new FormData()
    fd.append('resume_file', form.value.file)
    fd.append('jd_text', form.value.jdText)

    const res = await diagnoseResume(fd)
    
    // console.log('API返回:', res) // 调试用

    if (res && res.code === 200) {
        // 🔥 关键修正：数据清洗 (Data Sanitization)
        // 确保哪怕后端乱返回，前端也不会崩
        const rawData = res.data || {}
        
        result.value = {
            score: Number(rawData.score) || 0, // 确保是数字
            summary: rawData.summary || 'AI 未生成总结',
            // 确保是数组，防止 v-for 报错
            pros: Array.isArray(rawData.pros) ? rawData.pros : [],
            cons: Array.isArray(rawData.cons) ? rawData.cons : [],
            suggestions: rawData.suggestions || ''
        }
        
        ElNotification.success({ title: '诊断完成', message: `得分：${result.value.score}` })
    } else {
        ElMessage.error(res.message || '诊断失败')
    }
  } catch (error) {
    console.error('前端处理错误:', error)
    ElMessage.error('请求出错，请检查网络或后端日志')
  } finally {
    loading.value = false
  }
}
</script>


<style scoped>
.resume-diagnose-container {
  /* 移除固定高度，适应 Dashboard 内容区 */
  background-color: transparent; 
}

.input-card {
  border-radius: 8px;
}
.card-header span {
  font-weight: bold;
  font-size: 16px;
}

.submit-btn {
  width: 100%;
  margin-top: 20px;
  font-weight: bold;
  letter-spacing: 1px;
}

.file-preview {
  margin-top: 10px;
}

/* 结果区域样式 */
.score-header {
  display: flex;
  align-items: center;
  gap: 20px;
}
.score-summary h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
}
.score-summary p {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}
.score-num {
  font-size: 28px;
  font-weight: bold;
  display: block;
}
.score-label {
  font-size: 12px;
  color: #909399;
}

.mt-20 { margin-top: 20px; }
.text-success { color: #67C23A; font-weight: bold; display: flex; align-items: center; gap: 5px; }
.text-danger { color: #F56C6C; font-weight: bold; display: flex; align-items: center; gap: 5px; }

.pros-cons-card ul {
  padding-left: 18px;
  margin: 0;
}
.pros-cons-card li {
  margin-bottom: 8px;
  color: #606266;
}

.suggestion-text {
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
}

/* 占位文本样式 */
.placeholder-text {
  color: #909399;
  font-size: 14px;
  line-height: 1.8;
  padding: 20px 10px;
}

.placeholder-text p {
  margin-bottom: 10px;
  color: #606266;
}

.placeholder-text ul {
  padding-left: 20px;
  margin: 5px 0;
}

.placeholder-text li {
  margin-bottom: 8px;
  color: #909399;
}
</style>