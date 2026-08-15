<template>
  <header class="app-header" :class="{ scrolled }">
    <div class="header-inner">
      <div class="header-left">
        <svg class="header-logo" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="32" height="32" rx="8" fill="url(#headerLogoGrad)"/>
          <path d="M10 22V14L16 10L22 14V22H18V17H14V22H10Z" fill="white" fill-opacity="0.95"/>
          <defs>
            <linearGradient id="headerLogoGrad" x1="0" y1="0" x2="32" y2="32">
              <stop stop-color="#1a73e8"/>
              <stop offset="1" stop-color="#4fc3f7"/>
            </linearGradient>
          </defs>
        </svg>
        <span class="header-brand">TraceTempAI</span>
      </div>
      <nav class="header-nav">
        <button
          class="nav-btn"
          :class="{ active: currentPage === 'welcome' }"
          @click="$emit('navigate', 'welcome')"
        >
          <el-icon :size="16"><HomeFilled /></el-icon>
          <span>首页</span>
        </button>
        <button
          class="nav-btn"
          :class="{ active: currentPage === 'analysis' }"
          @click="$emit('navigate', 'analysis')"
        >
          <el-icon :size="16"><DataAnalysis /></el-icon>
          <span>监控分析</span>
        </button>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { HomeFilled, DataAnalysis } from '@element-plus/icons-vue'

defineProps({
  currentPage: {
    type: String,
    default: 'welcome'
  }
})

defineEmits(['navigate'])

const scrolled = ref(false)

function onScroll() {
  scrolled.value = window.scrollY > 10
}

onMounted(() => window.addEventListener('scroll', onScroll))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<style lang="scss" scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 56px;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid transparent;
  transition: all 0.3s ease;

  &.scrolled {
    background: rgba(255, 255, 255, 0.94);
    border-bottom-color: #ebeef5;
    box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
  }
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-logo {
  width: 32px;
  height: 32px;
}

.header-brand {
  font-size: 17px;
  font-weight: 700;
  color: #1a1a2e;
  letter-spacing: -0.3px;
}

.header-nav {
  display: flex;
  gap: 4px;
}

.nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    color: #1a73e8;
    background: rgba(26, 115, 232, 0.06);
  }

  &.active {
    color: #1a73e8;
    background: rgba(26, 115, 232, 0.1);
    font-weight: 600;
  }
}
</style>
