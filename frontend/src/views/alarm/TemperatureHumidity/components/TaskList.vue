<template>
  <div class="task-list">
    <div class="list-header">
      <h2 class="list-title">任务列表</h2>
      <el-button text @click="$emit('refresh')">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>
    
    <div v-if="tasks.length === 0" class="empty-tasks">
      <el-icon :size="40" color="#c0c4cc"><Document /></el-icon>
      <p>暂无报告生成任务</p>
    </div>
    
    <div v-else class="tasks-container">
      <TransitionGroup name="task-list">
        <div v-for="task in tasks" :key="task.task_id" class="task-item" :class="{ 'is-processing': task.status === '处理中', 'is-done': task.status === '已完成' }">
          <div class="task-info">
            <div class="task-header">
              <div class="task-name-row">
                <span class="task-name">{{ getReportTypeName(task.report_type) }}</span>
                <el-tag 
                  :type="getStatusTagType(task.status)" 
                  size="small"
                  :class="{ 'pulse-tag': task.status === '处理中' }"
                >
                  {{ task.status }}
                </el-tag>
              </div>
            </div>
            <div class="task-meta">
              <span class="task-time">
                <el-icon :size="14"><Clock /></el-icon>
                {{ task.created_at || '-' }}
              </span>
              <span v-if="task.completed_at" class="task-complete">
                <el-icon :size="14"><CircleCheck /></el-icon>
                {{ task.completed_at }}
              </span>
            </div>
          </div>
          
          <div class="task-actions">
            <template v-if="task.status === '处理中'">
              <div class="progress-wrapper">
                <el-progress 
                  :percentage="task.progress || 0" 
                  :stroke-width="20"
                  :show-text="true"
                  class="task-progress"
                />
                <span v-if="elapsedTimers && elapsedTimers.get(task.task_id) !== undefined" class="elapsed-time">
                  {{ formatTime(elapsedTimers.get(task.task_id)) }}
                </span>
              </div>
            </template>
            <template v-else-if="task.status === '已完成'">
              <span class="done-icon"><el-icon :size="20" color="#67c23a"><CircleCheckFilled /></el-icon></span>
              <el-button 
                type="primary" 
                size="small" 
                @click="handleDownloadAll(task.file_ids)"
                :disabled="!task.file_ids || task.file_ids.length === 0"
              >
                <el-icon><Download /></el-icon> 下载 ({{ task.file_ids?.length || 0 }})
              </el-button>
            </template>
            <template v-else-if="task.status === '失败'">
              <span class="task-error">
                <el-icon :size="16"><WarningFilled /></el-icon>
                {{ task.error || '任务失败' }}
              </span>
            </template>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import {
  Refresh, Document, Download, Clock, CircleCheck, CircleCheckFilled, WarningFilled
} from '@element-plus/icons-vue'

defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
  elapsedTimers: {
    type: Map,
    default: null
  }
})

defineEmits(['refresh'])

function getReportTypeName(type) {
  const types = {
    'monthly_review': '温湿度监控月度回顾表',
    'correction': '环境失控纠正报告'
  }
  return types[type] || type
}

function getStatusTagType(status) {
  const typeMap = {
    '待处理': 'info',
    '处理中': 'warning',
    '已完成': 'success',
    '失败': 'danger'
  }
  return typeMap[status] || 'info'
}

function formatTime(seconds) {
  if (seconds < 60) return `${seconds}s`
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}m ${secs}s`
}

// 构建携带访问令牌的请求头（与 axios 拦截器保持一致）
function authHeaders(extraHeaders = {}) {
  const headers = { ...extraHeaders }
  const token = localStorage.getItem('token')
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

async function handleDownloadAll(fileIds) {
  if (!fileIds || fileIds.length === 0) return
  
  try {
    if (fileIds.length === 1) {
      const response = await fetch(
        `/api/reports/download/${encodeURIComponent(fileIds[0])}`,
        { headers: authHeaders() }
      )
      
      if (response.status === 401) {
        window.dispatchEvent(new CustomEvent('auth:required'))
        return
      }
      if (!response.ok) {
        throw new Error('文件下载失败')
      }
      
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      const contentDisposition = response.headers.get('content-disposition')
      let filename = fileIds[0]
      if (contentDisposition) {
        const filenameStarMatch = contentDisposition.match(/filename\*\s*=\s*utf-8''([^;]+)/i)
        if (filenameStarMatch && filenameStarMatch[1]) {
          filename = decodeURIComponent(filenameStarMatch[1].trim())
        } else {
          const filenameMatch = contentDisposition.match(/filename[^;]*=\s*([^;]+)/i)
          if (filenameMatch && filenameMatch[1]) {
            filename = decodeURIComponent(filenameMatch[1].trim().replace(/['"]/g, ''))
          }
        }
      }
      link.setAttribute('download', filename)
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } else {
      const response = await fetch('/api/reports/download-batch', {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ file_ids: fileIds })
      })
      
      if (response.status === 401) {
        window.dispatchEvent(new CustomEvent('auth:required'))
        return
      }
      if (!response.ok) {
        throw new Error('批量下载失败')
      }
      
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      const contentDisposition = response.headers.get('content-disposition')
      let zipFilename = `reports_batch_${Date.now()}.zip`
      if (contentDisposition) {
        const filenameStarMatch = contentDisposition.match(/filename\*\s*=\s*utf-8''([^;]+)/i)
        if (filenameStarMatch && filenameStarMatch[1]) {
          zipFilename = decodeURIComponent(filenameStarMatch[1].trim())
        } else {
          const filenameMatch = contentDisposition.match(/filename[^;]*=\s*([^;]+)/i)
          if (filenameMatch && filenameMatch[1]) {
            zipFilename = decodeURIComponent(filenameMatch[1].trim().replace(/['"]/g, ''))
          }
        }
      }
      link.setAttribute('download', zipFilename)
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    }
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败，请稍后重试')
  }
}
</script>

<style lang="scss" scoped>
.task-list {
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.list-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.empty-tasks {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.empty-tasks p {
  color: var(--text-muted);
  margin: 12px 0 0;
}

.tasks-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f9fafb;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: all 0.3s ease;

  &.is-processing {
    background: #fefce8;
    border-color: #fde68a;
  }

  &.is-done {
    background: #f0fdf4;
    border-color: #bbf7d0;
  }
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-header {
  margin-bottom: 8px;
}

.task-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.pulse-tag {
  animation: tagPulse 2s ease-in-out infinite;
}

@keyframes tagPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 12px;
  color: var(--text-muted);

  .el-icon {
    margin-right: 4px;
    vertical-align: -2px;
  }
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  margin-left: 20px;
}

.progress-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.task-progress {
  width: 200px;

  :deep(.el-progress-bar__outer) {
    background: #e5e7eb;
    border-radius: 10px;
  }

  :deep(.el-progress-bar__inner) {
    background: linear-gradient(90deg, #1a73e8, #4fc3f7);
    border-radius: 10px;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }

  :deep(.el-progress__text) {
    font-size: 12px;
    font-weight: 600;
    color: var(--primary-color);
  }
}

.elapsed-time {
  font-size: 11px;
  color: var(--text-muted);
}

.done-icon {
  display: flex;
  align-items: center;
  animation: popIn 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes popIn {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.task-error {
  font-size: 12px;
  color: #f56c6c;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* Task list transition */
.task-list-enter-active,
.task-list-leave-active {
  transition: all 0.4s ease;
}

.task-list-enter-from {
  opacity: 0;
  transform: translateY(-12px);
}

.task-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.task-list-move {
  transition: transform 0.4s ease;
}
</style>
