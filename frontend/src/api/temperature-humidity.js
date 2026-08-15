import axios from 'axios'

const baseURL = '/api'

const service = axios.create({
  baseURL,
  timeout: 120000
})

service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 触发访问令牌校验事件（App.vue 监听后弹出令牌输入面板）
function emitAuthRequired() {
  window.dispatchEvent(new CustomEvent('auth:required'))
}

service.interceptors.response.use(
  response => {
    const contentType = response.headers['content-type'] || ''
    if (contentType.includes('application/json')) {
      const res = response.data
      if (res.code !== 0) {
        console.error('API Error:', res.message)
        return Promise.reject(new Error(res.message || 'Error'))
      }
      return res.data
    }
    return response
  },
  error => {
    const status = error.response && error.response.status
    if (status === 401) {
      // 访问令牌缺失或失效：清除本地令牌并提示重新输入
      localStorage.removeItem('token')
      emitAuthRequired()
    } else {
      console.error('API Request Error:', error)
      if (error.code === 'ECONNABORTED') {
        console.error('请求超时，请稍后重试')
      } else if (!error.response) {
        console.error('网络连接失败，请检查网络')
      }
    }
    return Promise.reject(error)
  }
)

export const temperatureHumidityAPI = {
  /**
   * 认证探测：后端配置了访问令牌时返回 401，未配置时返回 200。
   * 用于前端判断是否需要展示令牌输入面板（与后端 APP_ACCESS_TOKEN 联动）。
   */
  checkAuth() {
    return service.get('/')
  },

  getDepartments() {
    return service.get('/departments')
  },

  getAlarmData(params) {
    const apiParams = {
      start_date: params.startDate,
      end_date: params.endDate,
      dept_id: params.deptId
    }
    return service.get('/alarms/temperature-humidity', { params: apiParams })
  },
  
  analyzeAlarm(data) {
    return service.post('/alarms/analyze', data)
  },
  
  generateReport(data) {
    return service.post('/reports/generate', data)
  },
  
  getTaskList() {
    return service.get('/reports/tasks')
  },
  
  getTaskStatus(taskId) {
    return service.get(`/reports/tasks/${taskId}`)
  },
  
  downloadReport(fileId) {
    return service.get(`/reports/download/${encodeURIComponent(fileId)}`, { responseType: 'blob' })
  },

  sanitizeFilename(name) {
    return name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5_.-]/g, '_')
  },

  exportData(format, data) {
    let endpoint = '/alarms/export'
    if (format === 'excel') {
      endpoint = '/alarms/export-excel'
    } else if (format === 'ai_txt') {
      endpoint = '/alarms/export-ai-txt'
    } else if (format === 'ai_word') {
      endpoint = '/alarms/export-ai-word'
    } else {
      endpoint = '/alarms/export'
    }

    const defaultFilenames = {
      'excel': 'alarm_charts.xlsx',
      'ai_txt': 'ai_analysis.txt',
      'ai_word': 'ai_analysis.docx',
      'json': 'export.json'
    }
    const defaultFilename = defaultFilenames[format] || 'export.bin'

    return service.post(endpoint, data, {
      responseType: 'blob'
    }).then(httpResponse => {
      const responseData = httpResponse.data || httpResponse
      const headers = httpResponse.headers || {}

      let filename = defaultFilename
      const contentDisposition = headers['content-disposition']
      if (contentDisposition) {
        // 优先解析 filename*=utf-8'' 格式（RFC 5987）
        const filenameStarMatch = contentDisposition.match(/filename\*\s*=\s*utf-8''([^;]+)/i)
        if (filenameStarMatch && filenameStarMatch[1]) {
          filename = this.sanitizeFilename(decodeURIComponent(filenameStarMatch[1].trim()))
        } else {
          // 如果没有 filename*，尝试解析 filename
          const match = contentDisposition.match(/filename[^;]*=\s*([^;]+)/i)
          if (match && match[1]) {
            filename = this.sanitizeFilename(decodeURIComponent(match[1].trim()))
          }
        }
      }

      const blob = responseData instanceof Blob ? responseData : new Blob([responseData])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.setAttribute('download', filename)
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)

      return { success: true, filename }
    }).catch(error => {
      console.error('导出失败:', error)
      throw error
    })
  }
}

export default service
