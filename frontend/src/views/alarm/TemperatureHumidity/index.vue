<template>
  <div class="temperature-humidity-container">
    <div class="page-header">
      <h1 class="page-title">温湿度智能监控分析</h1>
      <div class="header-actions">
        <div v-if="store.pollingActive" class="polling-indicator">
          <span class="polling-dot"></span>
          <span>自动刷新中</span>
        </div>
        <el-dropdown
          v-if="store.alarmData && store.loadingStage === 'done'"
          @command="handleExportAll"
          trigger="click"
        >
          <el-button type="primary" :icon="Download">
            导出全部数据
            <el-icon class="el-icon--right">
              <ArrowDown />
            </el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="json">导出报警数据 (JSON)</el-dropdown-item>
              <el-dropdown-item command="excel">导出图表数据 (Excel)</el-dropdown-item>
              <el-dropdown-item command="ai_txt" v-if="store.analysisResult">
                导出AI分析 (TXT)
              </el-dropdown-item>
              <el-dropdown-item command="ai_word" v-if="store.analysisResult">
                导出AI分析 (Word)
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <QueryPanel @query="handleQuery" />

    <StatusAlert 
      :handled-count="store.handledCount" 
      :unhandled-count="store.unhandledCount" 
    />

    <el-tabs v-model="activeTab" class="main-tabs">
      <el-tab-pane label="数据趋势统计" name="trend-analysis">
        <!-- Skeleton loading -->
        <div v-if="store.loadingStage === 'fetching'" class="skeleton-container">
          <div class="skeleton-card">
            <div class="skeleton-line w-60 skeleton-animate"></div>
            <div class="skeleton-line w-40 skeleton-animate"></div>
            <div class="skeleton-line w-50 skeleton-animate"></div>
          </div>
          <div class="skeleton-grid">
            <div class="skeleton-card skeleton-chart skeleton-animate"></div>
            <div class="skeleton-card skeleton-chart skeleton-animate"></div>
          </div>
          <div class="skeleton-grid">
            <div class="skeleton-card skeleton-chart skeleton-animate"></div>
            <div class="skeleton-card skeleton-chart skeleton-animate"></div>
          </div>
        </div>
        <Transition name="content-fade" mode="out-in">
          <TrendAnalysisTab
            v-if="store.alarmData && store.loadingStage === 'done'"
            key="trend"
            :alarm-data="store.alarmData"
            :show-export="true"
            @export="handleExport"
          />
          <div v-else-if="!store.alarmData && store.loadingStage !== 'fetching'" key="empty" class="empty-state">
            <el-icon :size="48" color="#c0c4cc"><DataLine /></el-icon>
            <p>请先查询数据</p>
          </div>
        </Transition>
      </el-tab-pane>
      <el-tab-pane label="AI深度分析" name="ai-analysis">
        <Transition name="content-fade" mode="out-in">
          <AiReportTab
            v-if="store.analysisResult"
            key="ai"
            :data="store.analysisResult"
          />
          <div v-else key="empty-ai" class="empty-state">
            <el-icon :size="48" color="#c0c4cc"><Cpu /></el-icon>
            <p>请先查询数据并进行AI深度分析</p>
            <el-button
              v-if="store.alarmData"
              type="primary"
              @click="handleAnalyze"
              :loading="store.isLoading"
            >
              执行AI分析
            </el-button>
          </div>
        </Transition>
      </el-tab-pane>
    </el-tabs>

    <ReportPanel 
      :alarm-data="store.alarmData"
      @generate="handleGenerateReport"
    />

    <TaskList 
      :tasks="store.taskList" 
      :elapsed-timers="store.elapsedTimers"
      @refresh="handleRefreshTask"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Download, ArrowDown, DataLine, Cpu } from '@element-plus/icons-vue'
import { useTemperatureHumidityStore } from '@/store/temperature-humidity'
import QueryPanel from './components/QueryPanel.vue'
import StatusAlert from './components/StatusAlert.vue'
import TrendAnalysisTab from './components/TrendAnalysisTab.vue'
import AiReportTab from './components/AiReportTab.vue'
import ReportPanel from './components/ReportPanel.vue'
import TaskList from './components/TaskList.vue'

const store = useTemperatureHumidityStore()
const activeTab = ref('trend-analysis')

async function handleQuery(params) {
  store.queryParams.startDate = params.startDate
  store.queryParams.endDate = params.endDate
  store.queryParams.deptId = params.deptId
  store.loadingStage = 'fetching'
  await store.fetchAlarmData()
  store.loadingStage = 'done'
  activeTab.value = 'trend-analysis'
}

async function handleAnalyze() {
  store.loadingStage = 'fetching'
  await store.analyzeAlarm()
  store.loadingStage = 'done'
  activeTab.value = 'ai-analysis'
}

async function handleGenerateReport(reportType) {
  await store.generateReport(reportType)
  store.startSmartPolling()
}

async function handleRefreshTask() {
  await store.fetchTaskList()
}

async function handleExportAll(command) {
  switch (command) {
    case 'json':
      await store.exportData('json')
      break
    case 'excel':
      await store.exportData('excel')
      break
    case 'ai_txt':
      await store.exportData('ai_txt')
      break
    case 'ai_word':
      await store.exportData('ai_word')
      break
  }
}

async function handleExport() {
  await store.exportData('excel')
}

onMounted(async () => {
  await store.fetchTaskList()
  const hasPendingOrProcessing = store.taskList.some(t => 
    t.status === '待处理' || t.status === '处理中'
  )
  if (hasPendingOrProcessing) {
    store.startSmartPolling()
  }
})

onUnmounted(() => {
  store.stopPolling()
  store.clearElapsedTimers()
})
</script>

<style lang="scss" scoped>
.temperature-humidity-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.polling-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--primary-color);
  padding: 4px 12px;
  background: rgba(26, 115, 232, 0.06);
  border-radius: 20px;
}

.polling-dot {
  width: 6px;
  height: 6px;
  background: var(--primary-color);
  border-radius: 50%;
  animation: blink 1s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.main-tabs {
  margin: 20px 0;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.main-tabs :deep(.el-tabs__header) {
  padding-left: 28px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.empty-state p {
  color: var(--text-muted);
  margin: 0 0 16px 0;
}

/* Skeleton loading styles */
.skeleton-container {
  padding: 20px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.skeleton-card {
  background: #f0f2f5;
  border-radius: var(--radius-sm);
  padding: 20px;
  margin-bottom: 16px;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.skeleton-chart {
  height: 280px;
}

.skeleton-line {
  height: 16px;
  background: #e4e7ed;
  border-radius: 4px;
  margin-bottom: 12px;
}

.w-60 { width: 60%; }
.w-50 { width: 50%; }
.w-40 { width: 40%; }

.skeleton-animate {
  background: linear-gradient(90deg, #f0f2f5 25%, #e4e7ed 50%, #f0f2f5 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Content fade transition */
.content-fade-enter-active,
.content-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.content-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.content-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
