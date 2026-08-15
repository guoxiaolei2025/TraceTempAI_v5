<template>
  <div class="trend-analysis-tab">
    <div class="charts-grid">
      <div class="chart-card">
        <h3 class="chart-title">报警类型占比</h3>
        <div ref="typeChart" class="chart-container"></div>
      </div>
      
      <div class="chart-card">
        <h3 class="chart-title">各设备报警分布</h3>
        <div ref="deviceChart" class="chart-container"></div>
      </div>
      
      <div class="chart-card wide">
        <h3 class="chart-title">24小时报警分布</h3>
        <div ref="hourChart" class="chart-container"></div>
      </div>
      
      <div class="chart-card">
        <h3 class="chart-title">星期报警分布</h3>
        <div ref="weekChart" class="chart-container"></div>
      </div>
      
      <div class="chart-card">
        <h3 class="chart-title">月度日期分布</h3>
        <div ref="monthChart" class="chart-container"></div>
      </div>
    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  alarmData: {
    type: Object,
    required: true
  }
})

const deviceChart = ref(null)
const typeChart = ref(null)
const hourChart = ref(null)
const weekChart = ref(null)
const monthChart = ref(null)

let deviceChartInstance = null
let typeChartInstance = null
let hourChartInstance = null
let weekChartInstance = null
let monthChartInstance = null

const colorMap = {
  '温度': '#0066cc',
  '湿度': '#66ccff',
  '其他': '#999999'
}

const legendOrder = ['温度', '湿度', '其他']

function initCharts() {
  const { devices = [], statistics = {} } = props.alarmData
  
  const deviceAlarmCount = {}
  const typeCount = { '温度': 0, '湿度': 0, '其他': 0 }
  const hourlyDistribution = {}
  const weeklyDistribution = {}
  const monthlyDistribution = {}
  
  for (let i = 0; i < 24; i++) {
    hourlyDistribution[i] = { '温度': 0, '湿度': 0, '其他': 0 }
  }
  
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  days.forEach(day => {
    weeklyDistribution[day] = { '温度': 0, '湿度': 0, '其他': 0 }
  })
  
  for (let i = 1; i <= 31; i++) {
    monthlyDistribution[i] = { '温度': 0, '湿度': 0, '其他': 0 }
  }
  
  devices.forEach(device => {
    const deviceSn = device.device_sn || device.device_name
    deviceAlarmCount[deviceSn] = (deviceAlarmCount[deviceSn] || 0) + device.alarms.length
    
    device.alarms.forEach(alarm => {
      const hasTemp = alarm.message?.includes('温度')
      const hasHumidity = alarm.message?.includes('湿度')
      
      if (hasTemp) {
        typeCount['温度']++
        const hour = new Date(alarm.alarmdate)?.getHours()
        if (hour >= 0 && hour < 24) {
          hourlyDistribution[hour]['温度']++
        }
        
        const dayIndex = new Date(alarm.alarmdate)?.getDay()
        if (dayIndex >= 0 && dayIndex < 7) {
          const dayName = days[(dayIndex + 6) % 7]
          weeklyDistribution[dayName]['温度']++
        }
        
        const dayOfMonth = new Date(alarm.alarmdate)?.getDate()
        if (dayOfMonth >= 1 && dayOfMonth <= 31) {
          monthlyDistribution[dayOfMonth]['温度']++
        }
      }
      
      if (hasHumidity) {
        typeCount['湿度']++
        const hour = new Date(alarm.alarmdate)?.getHours()
        if (hour >= 0 && hour < 24) {
          hourlyDistribution[hour]['湿度']++
        }
        
        const dayIndex = new Date(alarm.alarmdate)?.getDay()
        if (dayIndex >= 0 && dayIndex < 7) {
          const dayName = days[(dayIndex + 6) % 7]
          weeklyDistribution[dayName]['湿度']++
        }
        
        const dayOfMonth = new Date(alarm.alarmdate)?.getDate()
        if (dayOfMonth >= 1 && dayOfMonth <= 31) {
          monthlyDistribution[dayOfMonth]['湿度']++
        }
      }
      
      if (!hasTemp && !hasHumidity) {
        typeCount['其他']++
        const hour = new Date(alarm.alarmdate)?.getHours()
        if (hour >= 0 && hour < 24) {
          hourlyDistribution[hour]['其他']++
        }
        
        const dayIndex = new Date(alarm.alarmdate)?.getDay()
        if (dayIndex >= 0 && dayIndex < 7) {
          const dayName = days[(dayIndex + 6) % 7]
          weeklyDistribution[dayName]['其他']++
        }
        
        const dayOfMonth = new Date(alarm.alarmdate)?.getDate()
        if (dayOfMonth >= 1 && dayOfMonth <= 31) {
          monthlyDistribution[dayOfMonth]['其他']++
        }
      }
    })
  })
  
  initTypeChart(typeCount)
  initDeviceChart(deviceAlarmCount)
  initHourChart(hourlyDistribution)
  initWeekChart(weeklyDistribution)
  initMonthChart(monthlyDistribution)
}

function initTypeChart(typeCount) {
  if (!typeChart.value) return
  
  typeChartInstance = echarts.init(typeChart.value)
  const total = Object.values(typeCount).reduce((a, b) => a + b, 0) || 1
  
  typeChartInstance.setOption({
    tooltip: { 
      trigger: 'item', 
      formatter: '{b}: {c} ({d}%)' 
    },
    series: [{
      type: 'pie',
      radius: '70%',
      data: legendOrder
        .filter(type => typeCount[type] > 0)
        .map(type => ({ 
          value: typeCount[type], 
          name: type,
          itemStyle: { color: colorMap[type] }
        })),
      label: {
        formatter: '{b}\n{d}%'
      }
    }]
  })
}

function initDeviceChart(deviceAlarmCount) {
  if (!deviceChart.value) return
  
  deviceChartInstance = echarts.init(deviceChart.value)
  const deviceKeys = Object.keys(deviceAlarmCount).slice(0, 10)
  const deviceValues = deviceKeys.map(k => deviceAlarmCount[k])
  
  deviceChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '10%', right: '4%', bottom: '12%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: deviceKeys.map(k => k.length > 12 ? k.substring(0, 12) + '...' : k),
      axisLabel: { rotate: 30, fontSize: 10 },
      name: '设备编号',
      nameLocation: 'middle',
      nameGap: 55
    },
    yAxis: { type: 'value', name: '报警次数', nameLocation: 'middle', nameGap: 50 },
    series: [{
      type: 'bar',
      data: deviceValues,
      itemStyle: { color: '#409EFF' }
    }]
  })
}

function initHourChart(hourlyDistribution) {
  if (!hourChart.value) return
  
  hourChartInstance = echarts.init(hourChart.value)
  
  const hours = Array.from({ length: 24 }, (_, i) => `${i}时`)
  const series = legendOrder.map(type => ({
    name: type,
    type: 'bar',
    stack: 'total',
    emphasis: { focus: 'series' },
    itemStyle: { color: colorMap[type] },
    data: Array.from({ length: 24 }, (_, i) => hourlyDistribution[i][type])
  }))
  
  hourChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: function(params) {
        let result = `${params[0].axisValue}<br/>`
        let total = 0
        params.forEach(param => {
          total += param.value
          result += `${param.marker} ${param.seriesName}: ${param.value}<br/>`
        })
        result += `总计: ${total}`
        return result
      }
    },
    legend: {
      data: legendOrder,
      top: 0
    },
    grid: { left: '5%', right: '4%', bottom: '15%', top: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: hours,
      name: '时段',
      nameLocation: 'middle',
      nameGap: 40
    },
    yAxis: { type: 'value', name: '报警次数', nameLocation: 'middle', nameGap: 50 },
    series: series
  })
}

function initWeekChart(weeklyDistribution) {
  if (!weekChart.value) return
  
  weekChartInstance = echarts.init(weekChart.value)
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  
  const series = legendOrder.map(type => ({
    name: type,
    type: 'bar',
    stack: 'total',
    emphasis: { focus: 'series' },
    itemStyle: { color: colorMap[type] },
    data: days.map(day => weeklyDistribution[day][type])
  }))
  
  weekChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: function(params) {
        let result = `${params[0].axisValue}<br/>`
        let total = 0
        params.forEach(param => {
          total += param.value
          result += `${param.marker} ${param.seriesName}: ${param.value}<br/>`
        })
        result += `总计: ${total}`
        return result
      }
    },
    legend: {
      data: legendOrder,
      top: 0
    },
    grid: { left: '10%', right: '4%', bottom: '15%', top: 40, containLabel: true },
    xAxis: { 
      type: 'category', 
      data: days,
      name: '星期',
      nameLocation: 'middle',
      nameGap: 40
    },
    yAxis: { type: 'value', name: '报警次数', nameLocation: 'middle', nameGap: 50 },
    series: series
  })
}

function initMonthChart(monthlyDistribution) {
  if (!monthChart.value) return
  
  monthChartInstance = echarts.init(monthChart.value)
  const days = Array.from({ length: 31 }, (_, i) => i + 1)
  
  const series = legendOrder.map(type => ({
    name: type,
    type: 'bar',
    stack: 'total',
    emphasis: { focus: 'series' },
    itemStyle: { color: colorMap[type] },
    data: days.map(day => monthlyDistribution[day][type])
  }))
  
  monthChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: function(params) {
        let result = `${params[0].axisValue}日<br/>`
        let total = 0
        params.forEach(param => {
          total += param.value
          result += `${param.marker} ${param.seriesName}: ${param.value}<br/>`
        })
        result += `总计: ${total}`
        return result
      }
    },
    legend: {
      data: legendOrder,
      top: 0
    },
    grid: { left: '10%', right: '4%', bottom: '15%', top: 40, containLabel: true },
    xAxis: { 
      type: 'category', 
      data: days.map(d => `${d}日`),
      axisLabel: { fontSize: 9 },
      name: '日期',
      nameLocation: 'middle',
      nameGap: 40
    },
    yAxis: { type: 'value', name: '报警次数', nameLocation: 'middle', nameGap: 50 },
    series: series
  })
}

function handleResize() {
  deviceChartInstance?.resize()
  typeChartInstance?.resize()
  hourChartInstance?.resize()
  weekChartInstance?.resize()
  monthChartInstance?.resize()
}

function disposeCharts() {
  deviceChartInstance?.dispose()
  typeChartInstance?.dispose()
  hourChartInstance?.dispose()
  weekChartInstance?.dispose()
  monthChartInstance?.dispose()
  deviceChartInstance = null
  typeChartInstance = null
  hourChartInstance = null
  weekChartInstance = null
  monthChartInstance = null
}

function reinitCharts() {
  disposeCharts()
  setTimeout(() => {
    initCharts()
  }, 100)
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})

watch(() => props.alarmData, () => {
  reinitCharts()
}, { deep: true })
</script>

<style lang="scss" scoped>
.trend-analysis-tab {
  padding: 20px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-card {
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  padding: 20px;
  box-shadow: var(--shadow-lg);
  
  &.wide {
    grid-column: span 2;
  }
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.chart-container {
  height: 280px;
}

.export-section {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card.wide {
    grid-column: span 1;
  }
}
</style>