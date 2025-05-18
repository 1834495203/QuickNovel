import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.ts'
import { showNotify, showNotifyResp } from './utils/notify'

const app = createApp(App)

// 注册全局通知方法
app.config.globalProperties.$notify = showNotify
app.config.globalProperties.$notifyResp = showNotifyResp

app.use(router).mount('#app')
