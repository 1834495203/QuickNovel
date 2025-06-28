// notify.ts
import { createApp, h } from 'vue'
import Notify from '../components/utils/Notify.vue'
import type { ResponseModel } from '../entity/ResponseEntity'

interface NotifyOptions {
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

interface NotifyInstance {
  id: string
  app: any
  mountNode: HTMLElement
  height: number
  top: number
}

// 全局通知管理器
class NotifyManager {
  private instances: NotifyInstance[] = []
  private baseTop = 20 // 基础顶部距离
  private gap = 10 // 通知之间的间距

  add(options: NotifyOptions): string {
    const { type, message, duration = 2000 } = options
    
    // 生成唯一ID
    const id = `notify-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    // 创建挂载点
    const mountNode = document.createElement('div')
    mountNode.style.position = 'fixed'
    mountNode.style.zIndex = '2000'
    document.body.appendChild(mountNode)

    // 计算新通知的位置
    const top = this.calculateTop()
    mountNode.style.top = `${top}px`
    mountNode.style.right = '20px'

    // 创建组件实例
    const app = createApp({
      render() {
        return h(Notify, {
          type,
          message,
          duration,
          onClose: () => {
            notifyManager.remove(id)
          },
          onHeightChange: (height: number) => {
            notifyManager.updateHeight(id, height)
          }
        })
      }
    })

    // 挂载组件
    app.mount(mountNode)

    // 添加到实例列表
    const instance: NotifyInstance = {
      id,
      app,
      mountNode,
      height: 60, // 默认高度，会在组件渲染后更新
      top
    }
    
    this.instances.push(instance)
    
    return id
  }

  remove(id: string) {
    const index = this.instances.findIndex(instance => instance.id === id)
    if (index > -1) {
      const instance = this.instances[index]
      
      // 销毁组件和挂载点
      instance.app.unmount()
      instance.mountNode.remove()
      
      // 从列表中移除
      this.instances.splice(index, 1)
      
      // 重新计算剩余通知的位置
      this.repositionAll()
    }
  }

  updateHeight(id: string, height: number) {
    const instance = this.instances.find(instance => instance.id === id)
    if (instance && instance.height !== height) {
      instance.height = height
      this.repositionAll()
    }
  }

  private calculateTop(): number {
    if (this.instances.length === 0) {
      return this.baseTop
    }
    
    const lastInstance = this.instances[this.instances.length - 1]
    return lastInstance.top + lastInstance.height + this.gap
  }

  private repositionAll() {
    let currentTop = this.baseTop
    
    this.instances.forEach(instance => {
      instance.top = currentTop
      instance.mountNode.style.top = `${currentTop}px`
      instance.mountNode.style.transition = 'top 0.3s ease'
      currentTop += instance.height + this.gap
    })
  }
}

// 全局通知管理器实例
const notifyManager = new NotifyManager()

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

export function showNotify(options: NotifyOptions): string {
  return notifyManager.add(options)
}

// 导出管理器实例，用于手动控制
export { notifyManager }