import { createApp, h } from 'vue'
import Notify from '../components/Notify.vue'
import type { ResponseModel } from '../entity/ResponseEntity'

interface NotifyOptions {
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

export function showNotifyResp(resp: ResponseModel) {
  console.log(resp)
  if (resp.code === 200) {
    showNotify({
      type: 'success',
      message: resp.message,
      duration: 2000
    })
  } else {
    showNotify({
      type: 'warning',
      message: resp.message,
      duration: 2000
    })
  }
}

export function showNotify(options: NotifyOptions) {
  const { type, message, duration = 2000 } = options

  // 创建挂载点
  const mountNode = document.createElement('div')
  document.body.appendChild(mountNode)

  // 创建组件实例
  const app = createApp({
    render() {
      return h(Notify, {
        type,
        message,
        duration,
        onClose: () => {
          // 销毁组件和挂载点
          app.unmount()
          mountNode.remove()
        }
      })
    }
  })

  // 挂载组件
  app.mount(mountNode)
}