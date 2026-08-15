<template>
  <div class="app-container">
    <AppHeader
      v-if="currentPage === 'analysis'"
      :current-page="currentPage"
      @navigate="handleNavigate"
    />
    <Transition name="page-fade" mode="out-in">
      <WelcomePage
        v-if="currentPage === 'welcome'"
        key="welcome"
        @enter="handleNavigate('analysis')"
      />
      <TemperatureHumidity
        v-else
        key="analysis"
      />
    </Transition>

    <!-- 访问令牌验证弹窗（后端启用认证时展示） -->
    <el-dialog
      v-model="showAuthDialog"
      title="访问验证"
      width="420px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
      align-center
    >
      <div class="auth-tip">
        系统已启用访问令牌保护，请输入管理员分发的访问令牌后继续使用。
      </div>
      <el-input
        v-model="tokenInput"
        type="password"
        placeholder="请输入访问令牌"
        show-password
        autocomplete="off"
        @keyup.enter="handleSaveToken"
      />
      <template #footer>
        <el-button
          type="primary"
          :loading="authLoading"
          class="auth-submit-btn"
          @click="handleSaveToken"
        >
          确认进入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, provide, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import AppHeader from './components/AppHeader.vue'
import WelcomePage from './views/WelcomePage.vue'
import TemperatureHumidity from './views/alarm/TemperatureHumidity/index.vue'
import { temperatureHumidityAPI } from './api/temperature-humidity.js'

const currentPage = ref('welcome')
provide('currentPage', currentPage)

const showAuthDialog = ref(false)
const tokenInput = ref('')
const authLoading = ref(false)

function handleNavigate(page) {
  currentPage.value = page
}

function openAuthDialog() {
  showAuthDialog.value = true
}

async function handleSaveToken() {
  const token = tokenInput.value.trim()
  if (!token) {
    ElMessage.warning('请输入访问令牌')
    return
  }
  authLoading.value = true
  try {
    // 保存令牌并用探测接口校验有效性
    localStorage.setItem('token', token)
    await temperatureHumidityAPI.checkAuth()
    showAuthDialog.value = false
    tokenInput.value = ''
    ElMessage.success('验证通过')
  } catch (e) {
    localStorage.removeItem('token')
    if (e.response && e.response.status === 401) {
      ElMessage.error('访问令牌无效，请检查后重试')
    } else {
      // 网络异常等场景：不阻塞进入，交由后续请求的 401 处理
      showAuthDialog.value = false
      ElMessage.warning('验证服务暂不可用，请稍后重试')
    }
  } finally {
    authLoading.value = false
  }
}

function handleAuthRequired() {
  localStorage.removeItem('token')
  openAuthDialog()
}

onMounted(async () => {
  // 后端配置了访问令牌时（checkAuth 返回 401），弹出令牌输入面板
  window.addEventListener('auth:required', handleAuthRequired)
  try {
    await temperatureHumidityAPI.checkAuth()
  } catch (e) {
    if (e.response && e.response.status === 401) {
      openAuthDialog()
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('auth:required', handleAuthRequired)
})
</script>

<style>
:root {
  --primary-color: #1a73e8;
  --primary-light: #4fc3f7;
  --text-primary: #303133;
  --text-secondary: #606266;
  --text-muted: #909399;
  --bg-page: #f5f7fa;
  --bg-card: #ffffff;
  --bg-subtle: #f9fafb;
  --border-color: #ebeef5;
  --border-light: #e4e7ed;
  --shadow-sm: 0 2px 12px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 2px 12px rgba(0, 0, 0, 0.1);
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-round: 50px;
  --color-danger: #f56c6c;
  --color-success: #67c23a;
  --color-warning: #e6a23c;
  --color-info: #409EFF;
  --bg-success-light: #f0f9ff;
  --bg-warning-light: #fffbeb;
  --bg-danger-light: #fef0f0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-color: var(--bg-page);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  min-height: 100vh;
}

/* 访问令牌验证弹窗 */
.auth-tip {
  margin-bottom: 16px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-subtle);
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.auth-submit-btn {
  width: 100%;
}

/* Page transition */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
</style>
