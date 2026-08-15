<template>
  <div class="ai-report-tab">
    <div class="report-section">
      <h2 class="section-title">一、报警概况总结</h2>
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-value">{{ data.overview?.total_alarms || 0 }}</div>
          <div class="card-label">总报警次数</div>
        </div>
        <div class="overview-card">
          <div class="card-value" :class="handledRateClass">{{ (data.overview?.handled_rate || 0).toFixed(1) }}%</div>
          <div class="card-label">处理完成率</div>
        </div>
        <div class="overview-card">
          <div class="card-value" :class="trendClass">{{ data.overview?.trend_change || '--' }}</div>
          <div class="card-label">环比变化</div>
        </div>
        <div class="overview-card">
          <div class="card-value period-value">{{ data.overview?.period || '--' }}</div>
          <div class="card-label">统计周期</div>
        </div>
      </div>
    </div>

    <div class="report-section">
      <h2 class="section-title">二、设备报警规律分析</h2>
      <div class="device-analysis">
        <div class="analysis-item full-width">
          <h3 class="item-title">报警设备TOP排行（全部设备）</h3>
          <ul class="device-list">
            <li v-for="(device, index) in data.device_analysis?.top_devices" :key="index" class="device-item">
              <span class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
              <span class="name">{{ device.name }}</span>
              <span class="count">{{ device.alarm_count }}次</span>
            </li>
          </ul>
        </div>
        
        <div class="analysis-item">
          <h3 class="item-title">冰箱温度报警TOP排行</h3>
          <div v-if="data.type_analysis?.by_category?.fridge?.top_devices?.length">
            <ul class="device-list">
              <li v-for="(device, index) in data.type_analysis.by_category.fridge.top_devices" :key="index" class="device-item">
                <span class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
                <span class="name">{{ device.name }}</span>
                <span class="count">{{ device.alarm_count }}次</span>
              </li>
            </ul>
          </div>
          <p v-else class="no-data">暂无冰箱设备报警数据</p>
        </div>
        
        <div class="analysis-item">
          <h3 class="item-title">环境温湿度报警TOP排行</h3>
          <div v-if="data.type_analysis?.by_category?.environment?.top_devices?.length">
            <ul class="device-list">
              <li v-for="(device, index) in data.type_analysis.by_category.environment.top_devices" :key="index" class="device-item">
                <span class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
                <span class="name">{{ device.name }}</span>
                <span class="count">{{ device.alarm_count }}次</span>
              </li>
            </ul>
          </div>
          <p v-else class="no-data">暂无环境温湿度报警数据</p>
        </div>
        
        <div class="analysis-item full-width">
          <h3 class="item-title">报警规律分析</h3>
          <div class="pattern-cards">
            <div class="pattern-card">
              <div class="pattern-label">报警最多的时段</div>
              <div class="pattern-value">
                <span v-for="(hour, index) in data.device_analysis?.peak_hours" :key="index" class="pattern-tag">
                  {{ hour }}
                </span>
              </div>
            </div>
            <div class="pattern-card">
              <div class="pattern-label">报警最多的星期</div>
              <div class="pattern-value">
                <span v-for="(day, index) in data.device_analysis?.peak_days" :key="index" class="pattern-tag">
                  {{ day }}
                </span>
              </div>
            </div>
            <div class="pattern-card">
              <div class="pattern-label">报警最多的日期</div>
              <div class="pattern-value">
                <span v-for="(day, index) in data.device_analysis?.peak_month_days" :key="index" class="pattern-tag">
                  {{ day }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="report-section">
      <h2 class="section-title">三、报警类型深度分析</h2>
      <div class="type-analysis">
        <div class="type-chart">
          <div v-for="(item, index) in data.type_analysis?.distribution" :key="index" class="type-bar-item">
            <span class="type-label">{{ item.type }}</span>
            <div class="type-bar-wrapper">
              <div class="type-bar" :style="{ width: item.percentage + '%' }" :class="'bar-' + index"></div>
            </div>
            <span class="type-value">{{ item.percentage.toFixed(1) }}%</span>
          </div>
        </div>
        
        <div class="severity-stats">
          <h3 class="item-title">严重程度分布</h3>
          <div class="severity-tags">
            <span class="severity-tag high">高: {{ data.type_analysis?.severity_statistics?.高 || 0 }}</span>
            <span class="severity-tag medium">中: {{ data.type_analysis?.severity_statistics?.中 || 0 }}</span>
            <span class="severity-tag low">低: {{ data.type_analysis?.severity_statistics?.低 || 0 }}</span>
          </div>
          <p class="severity-note">
            <span class="note-label">说明：</span>
            <span class="note-text">高=报警次数前10%，中=报警次数10%-60%，低=报警次数60%以后</span>
          </p>
        </div>
      </div>
    </div>

    <div class="report-section">
      <h2 class="section-title">四、智能改善建议</h2>
      <div class="suggestions-list">
        <div 
          v-for="(suggestion, index) in data.suggestions" 
          :key="index" 
          class="suggestion-item"
          :class="'priority-' + suggestion.priority.toLowerCase()"
        >
          <div class="suggestion-header">
            <span class="priority-badge">{{ suggestion.priority }}优先级</span>
            <span class="suggestion-type">{{ suggestion.type }}</span>
          </div>
          <div class="suggestion-target">针对: {{ suggestion.target }}</div>
          <div class="suggestion-desc">{{ suggestion.description }}</div>
        </div>
      </div>
    </div>

    <div class="report-section">
      <h2 class="section-title">五、处理情况评估</h2>
      <div class="handling-evaluation">
        <div class="evaluation-summary">
          <div class="eval-item">
            <span class="eval-label">未处理报警:</span>
            <span class="eval-value unhandled">{{ data.handling_evaluation?.unhandled_count || 0 }}条</span>
          </div>
          <div class="eval-item">
            <span class="eval-label">平均响应时间:</span>
            <span class="eval-value">{{ data.handling_evaluation?.average_response_time || '--' }}</span>
          </div>
        </div>
        <p class="response-time-note">
          <span class="note-label">说明：</span>
          <span class="note-text">平均响应时间 = (处理完成时间 - 报警时间) 的平均值，单位：小时:分钟</span>
        </p>
        
        <div v-if="data.handling_evaluation?.unhandled_list?.length" class="unhandled-list">
          <h3 class="item-title">未处理报警清单（按设备聚合，TOP10）</h3>
          <table class="unhandled-table">
            <thead>
              <tr>
                <th>设备</th>
                <th>未处理次数</th>
                <th>最早报警时间</th>
                <th>最近报警时间</th>
                <th>类型</th>
                <th>严重程度</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in data.handling_evaluation.unhandled_list" :key="index">
                <td>{{ item.device }}</td>
                <td><span class="count-badge">{{ item.alarm_count || 1 }}</span></td>
                <td>{{ item.first_alarm_time || item.alarm_time || '--' }}</td>
                <td>{{ item.latest_alarm_time || item.alarm_time || '--' }}</td>
                <td>{{ item.type }}</td>
                <td><span class="severity-tag" :class="(item.severity || '高').toLowerCase()">{{ item.severity || '高' }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-if="data.handling_evaluation?.recommended_priority?.length" class="priority-list">
          <h3 class="item-title">建议处理优先级</h3>
          <div class="priority-items">
            <span v-for="(device, index) in data.handling_evaluation.recommended_priority" :key="index" class="priority-item">
              {{ index + 1 }}. {{ device }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="report-section">
      <div class="section-header">
        <h2 class="section-title">分析报告全文</h2>
        <div class="header-actions">
          <el-tag v-if="data.ai_powered" type="success" size="small" class="ai-badge">AI 大模型生成</el-tag>
          <el-tag v-else type="info" size="small" class="ai-badge">本地规则生成</el-tag>
          <el-tag v-if="data.quality_score" type="warning" size="small">质量评分: {{ data.quality_score }}/100</el-tag>
          <el-button type="primary" size="small" @click="copyReport">
            <el-icon name="copy" /> 复制报告
          </el-button>
        </div>
      </div>
      <div class="report-text">
        <template v-if="reportBody">{{ reportBody }}</template>
        <template v-else>--</template>
        <div v-if="reportDisclaimer" class="report-disclaimer">
          {{ reportDisclaimer }}
        </div>
      </div>
      
      <!-- 用户反馈区域 -->
      <div class="feedback-area" v-if="data.ai_powered">
        <div class="feedback-row">
          <span class="feedback-label">分析质量评价：</span>
          <el-rate v-model="feedbackRating" :texts="['很差','较差','一般','满意','优秀']" show-text :disabled="feedbackSubmitted" />
        </div>
        <el-input v-if="feedbackRating > 0 && !feedbackSubmitted" v-model="feedbackComment"
          type="textarea" :rows="2" placeholder="可选：哪里需要改进？" maxlength="200" show-word-limit
          class="feedback-input" />
        <el-button v-if="feedbackRating > 0 && !feedbackSubmitted" type="primary" size="small" @click="submitFeedback">
          提交反馈
        </el-button>
        <el-tag v-if="feedbackSubmitted" type="success" size="small">已提交，感谢反馈</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

// 用户反馈状态
const feedbackRating = ref(0)
const feedbackComment = ref('')
const feedbackSubmitted = ref(false)

async function submitFeedback() {
  try {
    await fetch('/api/v1/alarms/ai-feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rating: feedbackRating.value,
        comment: feedbackComment.value,
        quality_score: props.data.quality_score || 0,
        timestamp: new Date().toISOString()
      })
    })
    feedbackSubmitted.value = true
    ElMessage.success('感谢您的反馈')
  } catch (e) {
    ElMessage.error('反馈提交失败')
  }
}

const trendClass = computed(() => {
  const trend = props.data.overview?.trend_change || ''
  // 报警量增加=红色（上升），减少=绿色（下降）
  if (trend.startsWith('-')) return 'trend-down'
  if (trend.startsWith('+')) return 'trend-up'
  if (trend.includes('下降') || trend.includes('减少')) return 'trend-down'
  if (trend.includes('上升') || trend.includes('增加') || trend === '新增') return 'trend-up'
  return ''
})

const handledRateClass = computed(() => {
  const rate = props.data.overview?.handled_rate || 0
  if (rate >= 80) return 'rate-high'
  if (rate >= 60) return 'rate-medium'
  return 'rate-low'
})

// 免责声明关键词：识别独立成行的声明段
const DISCLAIMER_KEYWORD = '该报告由AI自动生成'

// 免责声明段落（独立一行展示并加粗）
const reportDisclaimer = computed(() => {
  const text = props.data.analysis_text || ''
  const lines = text.split('\n')
  const idx = lines.findIndex(line => line.includes(DISCLAIMER_KEYWORD))
  if (idx === -1) return ''
  return lines.slice(idx).join('\n').trim()
})

// 报告正文（去掉免责声明段落）
const reportBody = computed(() => {
  const text = props.data.analysis_text || ''
  const disclaimer = reportDisclaimer.value
  if (!disclaimer) return text
  return text.replace(disclaimer, '').replace(/[\n\s]+$/, '')
})

function copyReport() {
  const text = props.data.analysis_text || ''
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('报告已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}
</script>

<style lang="scss" scoped>
.ai-report-tab {
  padding: 20px;
}

.report-section {
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-lg);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--color-info);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-badge {
  font-weight: 500;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.overview-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: var(--bg-page);
  border-radius: var(--radius-sm);
  padding: 16px;
  text-align: center;
}

.card-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  
  &.trend-up {
    color: var(--color-danger);
  }
  
  &.trend-down {
    color: var(--color-success);
  }
  
  &.rate-high {
    color: var(--color-success);
  }
  
  &.rate-medium {
    color: var(--color-warning);
  }
  
  &.rate-low {
    color: var(--color-danger);
  }

  &.period-value {
    font-size: 16px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.4;
  }
}

.card-label {
  font-size: 14px;
  color: var(--text-muted);
}

.device-analysis {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.analysis-item {
  background: var(--bg-subtle);
  border-radius: var(--radius-sm);
  padding: 16px;
  
  &.full-width {
    grid-column: 1 / -1;
  }
}

.item-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
}

.fridge-summary {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.fridge-count {
  font-weight: 600;
  font-size: 16px;
}

.device-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.device-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--border-light);
  
  &:last-child {
    border-bottom: none;
  }
}

.rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: var(--text-muted);
  
  &.rank-1 { background: var(--color-danger); }
  &.rank-2 { background: var(--color-warning); }
  &.rank-3 { background: var(--color-success); }
}

.name {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.count {
  font-size: 13px;
  color: var(--text-muted);
}

.critical-devices {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.critical-tag {
  background: var(--bg-warning-light);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xs);
  padding: 4px 12px;
  font-size: 13px;
  color: #d46b08;
}

.no-data {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.pattern-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.pattern-card {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  padding: 16px;
  text-align: center;
}

.pattern-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.pattern-value {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.pattern-tag {
  background: var(--bg-success-light);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xs);
  padding: 6px 12px;
  font-size: 13px;
  color: var(--primary-color);
}

.type-analysis {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.type-bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.type-label {
  width: 60px;
  font-size: 13px;
  color: var(--text-secondary);
}

.type-bar-wrapper {
  flex: 1;
  height: 20px;
  background: var(--bg-page);
  border-radius: 10px;
  overflow: hidden;
}

.type-bar {
  height: 100%;
  border-radius: 10px;
  transition: width 0.3s;
  
  &.bar-0 { background: var(--primary-color); }
  &.bar-1 { background: var(--primary-light); }
  &.bar-2 { background: #3399ff; }
  &.bar-3 { background: #999999; }
}

.type-value {
  width: 60px;
  font-size: 13px;
  color: var(--text-secondary);
  text-align: right;
}

.severity-tags {
  display: flex;
  gap: 12px;
}

.severity-tag {
  padding: 6px 16px;
  border-radius: var(--radius-xs);
  font-size: 13px;
  
  &.high { background: var(--bg-danger-light); color: #dc2626; border: 1px solid #fecaca; }
  &.medium { background: var(--bg-warning-light); color: #d97706; border: 1px solid #fde68a; }
  &.low { background: #ecfdf5; color: #059669; border: 1px solid #86efac; }
}

.severity-note,
.response-time-note {
  margin: 12px 0 20px 0;
  font-size: 12px;
  color: var(--text-muted);
  
  .note-label {
    font-weight: 500;
  }
  
  .note-text {
    color: var(--text-muted);
  }
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  background: var(--bg-subtle);
  border-radius: var(--radius-sm);
  padding: 16px;
  border-left: 4px solid var(--text-muted);
  
  &.priority-高 { border-left-color: var(--color-danger); }
  &.priority-中 { border-left-color: var(--color-warning); }
  &.priority-低 { border-left-color: var(--color-success); }
}

.suggestion-header {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.priority-badge {
  background: #fff;
  border: 1px solid;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
  
  .priority-高 & { border-color: var(--color-danger); color: var(--color-danger); }
  .priority-中 & { border-color: var(--color-warning); color: var(--color-warning); }
  .priority-低 & { border-color: var(--color-success); color: var(--color-success); }
}

.suggestion-type {
  font-size: 13px;
  color: var(--text-secondary);
}

.suggestion-target {
  font-size: 13px;
  color: var(--color-info);
  margin-bottom: 8px;
}

.suggestion-desc {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
}

.handling-evaluation {
  background: var(--bg-subtle);
  border-radius: var(--radius-sm);
  padding: 16px;
}

.evaluation-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px dashed var(--border-light);
}

.eval-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.eval-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.eval-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  
  &.unhandled {
    color: var(--color-danger);
  }
}

.unhandled-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin-bottom: 16px;
}

.unhandled-table th,
.unhandled-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
}

.unhandled-table th {
  background: #fff;
  font-weight: 600;
  color: var(--text-secondary);
}

.count-badge {
  display: inline-block;
  min-width: 28px;
  padding: 2px 10px;
  border-radius: 12px;
  background: #fef0e6;
  color: var(--color-danger);
  font-weight: 600;
  font-size: 13px;
  text-align: center;
}

.priority-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.priority-item {
  font-size: 14px;
  color: var(--text-primary);
  padding: 8px 12px;
  background: #fff;
  border-radius: 4px;
}

.report-text {
  padding: 16px;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 500px;
  overflow-y: auto;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #dcdfe6;
    border-radius: 3px;
  }

  .report-disclaimer {
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px dashed var(--border-light);
    font-weight: 600;
    color: var(--text-secondary);
  }
}

@media (max-width: 768px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .device-analysis {
    grid-template-columns: 1fr;
  }
  
  .type-analysis {
    grid-template-columns: 1fr;
  }
}

.feedback-area {
  margin-top: 16px;
  padding: 12px 16px;
  background: var(--bg-subtle);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.feedback-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.feedback-label {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.feedback-input {
  margin: 8px 0;
}
</style>
