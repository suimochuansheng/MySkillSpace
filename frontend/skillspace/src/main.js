import '@/styles/components.css'
import '@/styles/global.css'
import '@/styles/variables.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { vPermission, vPermDisable } from '@/directives/permission'

const app = createApp(App)
const pinia = createPinia()

// 注册Pinia状态管理
app.use(pinia)

// 注册Element Plus
app.use(ElementPlus)

// 注册路由
app.use(router)

// 注册权限指令
app.directive('permission', vPermission)
app.directive('permDisable', vPermDisable)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
