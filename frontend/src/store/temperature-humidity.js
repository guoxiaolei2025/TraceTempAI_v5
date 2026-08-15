import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { temperatureHumidityAPI } from '../api/temperature-humidity'

export const useTemperatureHumidityStore = defineStore('temperatureHumidity', () => {
  const queryParams = ref({
    startDate: '',
    endDate: '',
    deptId: undefined
  })
  
  const alarmData = ref(null)
  const analysisResult = ref(null)
  const taskList = ref([])
  const isLoading = ref(false)
  const loadingStage = ref('idle') // 'idle' | 'fetching' | 'charting' | 'done'
  const pollingActive = ref(false)

  // Smart polling state
  let pollTimer = null
  let pollCount = 0
  
  // Elapsed timers for task progress display
  const elapsedTimers = ref(new Map())
  let elapsedTimerHandle = null
  
  const handledCount = computed(() => alarmData.value?.handled_count || 0)
  const unhandledCount = computed(() => alarmData.value?.unhandled_count || 0)
  const totalAlarms = computed(() => alarmData.value?.total || 0)
  
  const hasUnhandledAlarms = computed(() => unhandledCount.value > 0)

  async function fetchAlarmData() {
    isLoading.value = true
    loadingStage.value = 'fetching'
    try {
      alarmData.value = await temperatureHumidityAPI.getAlarmData(queryParams.value)
      analysisResult.value = null
      loadingStage.value = 'charting'
      // Small delay for skeleton to be visible before data renders
      await new Promise(r => setTimeout(r, 200))
      return alarmData.value
    } catch (error) {
      console.error('获取报警数据失败:', error)
      loadingStage.value = 'done'
      throw error
    } finally {
      isLoading.value = false
      loadingStage.value = 'done'
    }
  }

  async function analyzeAlarm() {
    if (!alarmData.value) return
    isLoading.value = true
    loadingStage.value = 'fetching'
    try {
      const chartData = generateChartData()
      analysisResult.value = await temperatureHumidityAPI.analyzeAlarm({
        start_date: queryParams.value.startDate,
        end_date: queryParams.value.endDate,
        dept_id: queryParams.value.deptId,
        alarm_data: {
          total_alarms: totalAlarms.value,
          handled_count: handledCount.value,
          unhandled_count: unhandledCount.value,
          temperature_alarms: alarmData.value.statistics?.temperature_alarms || 0,
          humidity_alarms: alarmData.value.statistics?.humidity_alarms || 0,
          device_alarm_count: chartData.deviceAlarmCount,
          hourly_distribution: chartData.hourlyDistribution,
          weekly_distribution: chartData.weeklyDistribution,
          type_distribution: chartData.typeDistribution,
          devices: alarmData.value.devices
        }
      })
      return analysisResult.value
    } catch (error) {
      console.error('AI分析失败:', error)
      throw error
    } finally {
      isLoading.value = false
      loadingStage.value = 'done'
    }
  }

  async function generateReport(reportType) {
    if (!alarmData.value) return
    isLoading.value = true
    try {
      const result = await temperatureHumidityAPI.generateReport({
        report_type: reportType,
        start_date: queryParams.value.startDate,
        end_date: queryParams.value.endDate,
        dept_id: queryParams.value.deptId
      })
      await fetchTaskList()
      startElapsedTimers()
      return result
    } catch (error) {
      console.error('生成报告失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTaskList() {
    try {
      const prevTaskList = [...taskList.value]
      taskList.value = await temperatureHumidityAPI.getTaskList()
      
      // Track newly appearing tasks
      const prevIds = new Set(prevTaskList.map(t => t.task_id))
      taskList.value.forEach(t => {
        if (!prevIds.has(t.task_id)) {
          startElapsedTimer(t.task_id)
        }
      })
      
      // Stop timers for completed/failed tasks
      taskList.value.forEach(t => {
        if ((t.status === '已完成' || t.status === '失败') && elapsedTimers.value.has(t.task_id)) {
          // Keep the final value for display
        }
      })
      
      return taskList.value
    } catch (error) {
      console.error('获取任务列表失败:', error)
      throw error
    }
  }

  async function refreshTask(taskId) {
    try {
      const task = await temperatureHumidityAPI.getTaskStatus(taskId)
      const index = taskList.value.findIndex(t => t.task_id === taskId)
      if (index !== -1) {
        taskList.value[index] = task
      }
      return task
    } catch (error) {
      console.error('刷新任务状态失败:', error)
      throw error
    }
  }

  // Smart polling with adaptive interval
  function startSmartPolling() {
    if (pollTimer) return
    pollCount = 0
    pollingActive.value = true
    scheduleNextPoll()
  }

  function scheduleNextPoll() {
    pollTimer = setTimeout(async () => {
      await fetchTaskList()
      
      const hasPendingOrProcessing = taskList.value.some(t => 
        t.status === '待处理' || t.status === '处理中'
      )
      
      if (!hasPendingOrProcessing) {
        stopPolling()
        pollingActive.value = false
        return
      }
      
      pollCount++
      const delay = getPollDelay(pollCount)
      scheduleNextPoll()
    }, getPollDelay(pollCount))
  }

  function getPollDelay(count) {
    if (count < 10) return 2000    // First 10 polls: 2s
    if (count < 30) return 5000    // Next 20 polls: 5s
    return 15000                    // After 2.5min+: 15s
  }

  function stopPolling() {
    if (pollTimer) {
      clearTimeout(pollTimer)
      pollTimer = null
    }
    pollingActive.value = false
  }

  // Elapsed time tracking
  function startElapsedTimers() {
    taskList.value.forEach(t => {
      if (t.status === '处理中' || t.status === '待处理') {
        startElapsedTimer(t.task_id)
      }
    })
  }

  function startElapsedTimer(taskId) {
    if (!elapsedTimers.value.has(taskId)) {
      elapsedTimers.value.set(taskId, 0)
    }
  }

  function clearElapsedTimers() {
    elapsedTimers.value.clear()
    if (elapsedTimerHandle) {
      clearInterval(elapsedTimerHandle)
      elapsedTimerHandle = null
    }
  }

  // Start the global elapsed timer increment
  if (typeof window !== 'undefined') {
    elapsedTimerHandle = setInterval(() => {
      const tasks = taskList.value
      if (!tasks || tasks.length === 0) return
      
      const newMap = new Map(elapsedTimers.value)
      let hasChanges = false
      
      tasks.forEach(t => {
        if (t.status === '处理中' && newMap.has(t.task_id)) {
          newMap.set(t.task_id, (newMap.get(t.task_id) || 0) + 1)
          hasChanges = true
        }
      })
      
      if (hasChanges) {
        elapsedTimers.value = newMap
      }
    }, 1000)
  }

  async function exportData(format = 'json') {
    if (!alarmData.value && !analysisResult.value) return
    isLoading.value = true
    try {
      let result
      if (format === 'json') {
        result = await temperatureHumidityAPI.exportData('json', {
          alarm_data: alarmData.value,
          analysis_result: analysisResult.value,
          date_range: {
            start: queryParams.value.startDate,
            end: queryParams.value.endDate
          }
        })
      } else if (format === 'excel') {
        result = await temperatureHumidityAPI.exportData('excel', {
          alarm_data: alarmData.value,
          date_range: {
            start: queryParams.value.startDate,
            end: queryParams.value.endDate
          }
        })
      } else if (format === 'ai_txt' || format === 'ai_word') {
        result = await temperatureHumidityAPI.exportData(format, {
          analysis_data: analysisResult.value
        })
      }
      
      if (result.success) {
        import('element-plus').then(({ ElMessage }) => {
          ElMessage.success('数据导出成功，文件已下载')
        })
      }
    } catch (error) {
      console.error('导出数据失败:', error)
      import('element-plus').then(({ ElMessage }) => {
        ElMessage.error('导出数据失败，请稍后重试')
      })
      throw error
    } finally {
      isLoading.value = false
    }
  }

  function generateChartData() {
    const devices = alarmData.value?.devices || []
    const deviceAlarmCount = {}
    const typeCount = { '温度': 0, '湿度': 0, '温湿度': 0, '未知': 0 }
    const hourlyDistribution = Array(24).fill(0)
    const weeklyDistribution = { '周一': 0, '周二': 0, '周三': 0, '周四': 0, '周五': 0, '周六': 0, '周日': 0 }

    devices.forEach(device => {
      device.alarms.forEach(alarm => {
        const key = `${device.device_name}【${device.device_sn}】`
        deviceAlarmCount[key] = (deviceAlarmCount[key] || 0) + 1
        
        const hasTemp = alarm.message?.includes('温度')
        const hasHumidity = alarm.message?.includes('湿度')
        let type = '未知'
        if (hasTemp && hasHumidity) type = '温湿度'
        else if (hasTemp) type = '温度'
        else if (hasHumidity) type = '湿度'
        typeCount[type]++
        
        const hour = new Date(alarm.alarmdate)?.getHours()
        if (hour >= 0 && hour < 24) {
          hourlyDistribution[hour]++
        }
        
        const day = new Date(alarm.alarmdate)?.getDay()
        const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        if (day >= 0 && day < 7) {
          weeklyDistribution[days[day]]++
        }
      })
    })

    return { deviceAlarmCount, typeCount, hourlyDistribution, weeklyDistribution, typeDistribution: typeCount }
  }

  return {
    queryParams,
    alarmData,
    analysisResult,
    taskList,
    isLoading,
    loadingStage,
    pollingActive,
    elapsedTimers,
    handledCount,
    unhandledCount,
    totalAlarms,
    hasUnhandledAlarms,
    fetchAlarmData,
    analyzeAlarm,
    generateReport,
    fetchTaskList,
    refreshTask,
    exportData,
    generateChartData,
    startSmartPolling,
    stopPolling,
    clearElapsedTimers
  }
})
