import { createApp, h } from 'vue'
import ConfirmDialog from '../components/utils/ConfirmDialog.vue'

interface ConfirmOptions {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
}

export function showConfirm(options: ConfirmOptions): Promise<boolean> {
  return new Promise((resolve) => {
    const { title, message, confirmText, cancelText } = options

    // 创建挂载点
    const mountNode = document.createElement('div')
    document.body.appendChild(mountNode)

    // 创建组件实例
    const app = createApp({
      render() {
        return h(ConfirmDialog, {
          title,
          message,
          confirmText,
          cancelText,
          onConfirm: () => {
            resolve(true)
          },
          onCancel: () => {
            resolve(false)
          },
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
  })
}