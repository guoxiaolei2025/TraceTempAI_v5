<template>
  <div v-if="total > 0" class="status-alert" :class="alertClass">
    <div class="alert-icon">
      <el-icon v-if="unhandledCount === 0" name="check-circle" />
      <el-icon v-else name="alert-circle" />
    </div>
    <div class="alert-content">
      <p class="alert-message">
        <template v-if="unhandledCount === 0">
          ✅ 选定时间范围内的报警数据已全部处理完成，分析结果准确可靠
        </template>
        <template v-else>
          ⚠️ 选定时间范围内存在未处理报警（{{ unhandledCount }}条），AI分析效果可能受到影响
        </template>
      </p>
      <p class="alert-stats">
        共 {{ total }} 条报警记录，已处理 {{ handledCount }} 条，未处理 {{ unhandledCount }} 条
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  handledCount: {
    type: Number,
    default: 0
  },
  unhandledCount: {
    type: Number,
    default: 0
  }
})

const total = computed(() => props.handledCount + props.unhandledCount)

const alertClass = computed(() => ({
  'alert-success': props.unhandledCount === 0,
  'alert-warning': props.unhandledCount > 0
}))
</script>

<style lang="scss" scoped>
.status-alert {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  border-radius: var(--radius-sm);
  margin-bottom: 20px;
  
  &.alert-success {
    background: var(--bg-success-light);
    border: 1px solid var(--border-light);
    
    .alert-icon {
      color: var(--color-success);
    }
  }
  
  &.alert-warning {
    background: var(--bg-warning-light);
    border: 1px solid var(--border-light);
    
    .alert-icon {
      color: var(--color-warning);
    }
  }
}

.alert-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

.alert-message {
  font-weight: 500;
  margin: 0 0 4px 0;
}

.alert-stats {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}
</style>
