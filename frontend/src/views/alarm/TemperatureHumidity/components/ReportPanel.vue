<template>
  <div class="report-panel">
    <h2 class="panel-title">报告生成</h2>
    <div class="panel-content">
      <el-form :inline="true" class="report-form">
        <el-form-item label="报告类型">
          <el-select v-model="reportType" placeholder="请选择报告类型" style="width: 220px;">
            <el-option label="温湿度监控月度回顾表" value="monthly_review" />
            <el-option label="环境失控纠正报告" value="correction" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleGenerate"
            :disabled="!alarmData || isLoading"
            :loading="isLoading"
          >
            生成报告
          </el-button>
        </el-form-item>
      </el-form>
      
      <div v-if="!alarmData" class="disabled-hint">
        <el-icon name="warning" /> 请先查询数据后再生成报告
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  alarmData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['generate'])

const reportType = ref('monthly_review')
const isLoading = ref(false)

async function handleGenerate() {
  if (!props.alarmData) return
  
  isLoading.value = true
  try {
    await emit('generate', reportType.value)
    ElMessage.success('报告生成任务已创建')
  } catch (error) {
    ElMessage.error('生成报告失败')
  } finally {
    isLoading.value = false
  }
}

import { ElMessage } from 'element-plus'
</script>

<style lang="scss" scoped>
.report-panel {
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-lg);
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.panel-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.report-form {
  display: flex;
  align-items: center;
  gap: 16px;
}

:deep(.el-form-item) {
  margin-bottom: 0;
}

.disabled-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-warning);
  font-size: 14px;
}
</style>
