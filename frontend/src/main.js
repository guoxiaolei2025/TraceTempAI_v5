import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

// 全局兜底：Element Plus 的 popper/定位组件在页面切换、DOM 已移除的瞬间
// 偶发触发 getBoundingClientRect 空引用错误（无副作用），此处忽略避免影响交互
app.config.errorHandler = (err, _instance, _info) => {
  const msg = err && err.message ? err.message : String(err)
  if (msg.includes('getBoundingClientRect')) {
    // 已知的无害错误，忽略
    return
  }
  console.error('[Vue Error]', msg, _info)
}

app.use(pinia)
app.use(ElementPlus)
app.mount('#app')
