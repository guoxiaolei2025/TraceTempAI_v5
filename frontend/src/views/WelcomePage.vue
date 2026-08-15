<template>
  <div class="welcome-page">
    <div class="welcome-content">
      <div class="brand-section">
        <div class="logo-icon">
          <img src="/logo_369.png" alt="369云管平台" class="logo-img" />
        </div>
        <h1 class="brand-title">温湿度智能监控分析系统</h1>
        <p class="brand-desc">AI驱动的温湿度趋势分析与报告生成平台</p>
      </div>

      <div class="cta-section">
        <button class="enter-btn" @click="$emit('enter')">
          <span>进入系统</span>
          <svg class="arrow-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"/>
          </svg>
        </button>
      </div>

      <div class="feature-grid">
        <div class="feature-card" v-for="feature in features" :key="feature.title">
          <div class="feature-icon" :style="{ background: feature.color }">
            <el-icon :size="24">
              <component :is="feature.icon" />
            </el-icon>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.desc }}</p>
        </div>
      </div>

      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-value">{{ apiCount }}+</span>
          <span class="stat-label">API 接口</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">5</span>
          <span class="stat-label">分析图表</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">4</span>
          <span class="stat-label">导出格式</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">AI</span>
          <span class="stat-label">智能驱动</span>
        </div>
      </div>

    </div>

    <footer class="welcome-footer">
      <p class="footer-copyright">温湿度智能监控分析系统©2026 Created by TraceTempAI</p>
      <p class="footer-declare">
        声明：该系统为演示版本，数据来源于
        <a href="https://cloud.369clouds.com/home" target="_blank" rel="noopener noreferrer">369云管平台API<svg class="link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17L17 7"/><path d="M8 7h9v9"/></svg></a>
        ，后续系统功能将整合到369云管平台。
      </p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  TrendCharts,
  Cpu,
  Document,
  Upload
} from '@element-plus/icons-vue'
import { temperatureHumidityAPI } from '@/api/temperature-humidity'

defineEmits(['enter'])

const apiCount = ref(33)

const features = [
  {
    icon: TrendCharts,
    title: '数据趋势分析',
    desc: '5种可视化图表，从报警类型、设备、小时、星期、月度多维度展示温湿度趋势',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    icon: Cpu,
    title: 'AI 深度分析',
    desc: '基于大模型结合风险评估模型，智能分析报警根因、识别风险并给出改善建议',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    icon: Document,
    title: '报告自动生成',
    desc: '自动生成温湿度监控月度回顾表和环境失控纠正报告，解放数据统计和报告撰写的重复性劳动',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    icon: Upload,
    title: '多格式导出',
    desc: '支持JSON、Excel、TXT、Word四种格式导出，满足不同场景数据使用需求',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
  }
]

onMounted(async () => {
  try {
    const data = await temperatureHumidityAPI.getDepartments()
    if (data && Array.isArray(data)) {
      apiCount.value = data.length
    }
  } catch {
    // 使用默认值
  }
})
</script>

<style lang="scss" scoped>
.welcome-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, #e8f4fd 0%, #f0f4ff 30%, #f5f7fa 60%, #fefefe 100%);
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;

  &::before {
    content: '';
    position: absolute;
    top: -20%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(26, 115, 232, 0.06) 0%, transparent 70%);
    border-radius: 50%;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -15%;
    left: -5%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(79, 195, 247, 0.05) 0%, transparent 70%);
    border-radius: 50%;
  }
}

.welcome-content {
  text-align: center;
  position: relative;
  z-index: 1;
  padding: 40px 24px 120px;
  animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.brand-section {
  margin-bottom: 40px;
}

.logo-icon {
  width: 76px;
  height: 76px;
  margin: 0 auto 24px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 8px;
  animation: float 3s ease-in-out infinite;
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 12px;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #1a73e8, #4fc3f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-desc {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.cta-section {
  margin-bottom: 56px;
}

.enter-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 40px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #1a73e8, #4fc3f7);
  border: none;
  border-radius: 50px;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(26, 115, 232, 0.35);
  transition: all 0.3s ease;
  animation: pulse 2s ease-in-out infinite;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 28px rgba(26, 115, 232, 0.45);
  }

  &:active {
    transform: translateY(0);
  }

  .arrow-icon {
    width: 18px;
    height: 18px;
    transition: transform 0.3s ease;
  }

  &:hover .arrow-icon {
    transform: translateX(4px);
  }
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 4px 20px rgba(26, 115, 232, 0.35); }
  50% { box-shadow: 0 4px 32px rgba(26, 115, 232, 0.55); }
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  max-width: 880px;
  margin: 0 auto 48px;
}

.feature-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 28px 20px 24px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: default;

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  }
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #fff;

  .el-icon {
    font-size: 24px;
  }
}

.feature-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.feature-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
  margin: 0;
}

.stats-bar {
  display: inline-flex;
  align-items: center;
  gap: 0;
  padding: 20px 40px;
  background: var(--bg-card);
  border-radius: var(--radius-round);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.05);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 28px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--primary-color);
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

.stat-divider {
  width: 1px;
  height: 36px;
  background: var(--border-color);
}

.welcome-footer {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  padding: 20px 24px;
  text-align: center;
  font-size: 12px;
  line-height: 1.8;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  border-top: 1px solid rgba(235, 238, 245, 0.8);

  .footer-copyright {
    margin: 0 0 6px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .footer-declare {
    margin: 0;
    font-size: 11px;
    color: var(--text-secondary);

    a {
      color: var(--primary-color);
      text-decoration: none;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 2px;

      .link-icon {
        width: 11px;
        height: 11px;
        flex-shrink: 0;
      }

      &:hover {
        text-decoration: underline;
      }
    }
  }
}

@media (max-width: 900px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
    padding: 0 20px;
  }

  .stats-bar {
    flex-wrap: wrap;
    justify-content: center;
    border-radius: 20px;
    margin: 0 20px;
  }

  .stat-divider:nth-child(6) {
    display: none;
  }

  .welcome-footer {
    padding: 16px 16px;
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .welcome-content {
    padding: 32px 16px 140px;
  }

  .logo-icon {
    width: 64px;
    height: 64px;
    margin-bottom: 18px;
  }

  .brand-title {
    font-size: 26px;
  }

  .brand-desc {
    font-size: 14px;
    line-height: 1.6;
    padding: 0 8px;
  }

  .cta-section {
    margin-bottom: 40px;
  }

  .enter-btn {
    padding: 12px 32px;
    font-size: 15px;
  }

  .feature-grid {
    grid-template-columns: 1fr;
    gap: 14px;
    margin-bottom: 36px;
  }

  .feature-card {
    padding: 20px 16px 18px;
  }

  .stats-bar {
    padding: 16px 8px;
    border-radius: 16px;
    margin: 0 8px;
  }

  .stat-item {
    padding: 0 16px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-divider {
    height: 32px;
  }

  .welcome-footer {
    padding: 14px 12px;
    font-size: 10px;
  }

  .footer-declare {
    font-size: 10px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .welcome-content,
  .enter-btn,
  .logo-icon {
    animation: none;
  }

  .enter-btn,
  .enter-btn:hover {
    transition: none;
    transform: none;
  }
}
</style>
