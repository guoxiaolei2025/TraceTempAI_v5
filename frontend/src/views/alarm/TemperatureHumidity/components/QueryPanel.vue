<template>
  <div class="query-panel">
    <el-form :inline="true" class="query-form">
      <el-form-item label="学科选择">
        <el-select
          v-model="selectedDeptId"
          placeholder="请选择学科"
          style="width: 220px"
        >
          <el-option
            v-for="dept in departments"
            :key="dept.id"
            :label="dept.name"
            :value="dept.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="开始日期">
        <el-date-picker
          v-model="startDate"
          type="date"
          placeholder="选择开始日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="结束日期">
        <el-date-picker
          v-model="endDate"
          type="date"
          placeholder="选择结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleQuery" :loading="isLoading">
          查询
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['query'])

const departments = ref([])
const selectedDeptId = ref('')
const startDate = ref('')
const endDate = ref('')
const isLoading = ref(false)

async function loadDepartments() {
  try {
    const response = await fetch('/api/departments')
    const data = await response.json()
    if (data.code === 0 && data.data) {
      departments.value = data.data
      if (data.data.length > 0) {
        selectedDeptId.value = data.data[0].id
      }
    }
  } catch (error) {
    console.error('加载学科列表失败:', error)
  }
}

async function handleQuery() {
  if (!selectedDeptId.value) {
    ElMessage.warning('请选择学科')
    return
  }
  
  if (!startDate.value || !endDate.value) {
    ElMessage.warning('请选择日期范围')
    return
  }
  
  if (startDate.value > endDate.value) {
    ElMessage.warning('开始日期不能大于结束日期')
    return
  }
  
  isLoading.value = true
  try {
    emit('query', {
      startDate: startDate.value,
      endDate: endDate.value,
      deptId: selectedDeptId.value
    })
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadDepartments()
  
  const today = new Date()
  const year = today.getFullYear()
  const month = today.getMonth()

  const firstDayOfPrevMonth = new Date(year, month - 1, 1)
  const lastDayOfPrevMonth = new Date(year, month, 0)

  const formatDate = (d) => {
    const yyyy = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    return `${yyyy}-${mm}-${dd}`
  }

  startDate.value = formatDate(firstDayOfPrevMonth)
  endDate.value = formatDate(lastDayOfPrevMonth)
})
</script>

<style lang="scss" scoped>
.query-panel {
  background: var(--bg-card);
  padding: 20px;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-lg);
  margin-bottom: 20px;
  min-width: fit-content;
}

.query-form {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

:deep(.el-form-item) {
  margin-bottom: 0;
  flex-shrink: 0;
}

:deep(.el-date-editor) {
  width: 180px;
}

:deep(.el-select) {
  width: 220px;
}
</style>