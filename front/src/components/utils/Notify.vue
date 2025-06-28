<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps<{
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration: number
}>()

const emit = defineEmits<{
  close: []
  heightChange: [height: number]
}>()

const visible = ref(false)
const notifyRef = ref<HTMLElement>()

// 动画控制
onMounted(async () => {
  visible.value = true
  
  // 等待DOM更新后获取实际高度
  await nextTick()
  if (notifyRef.value) {
    const height = notifyRef.value.offsetHeight
    emit('heightChange', height)
  }
  
  // 自动关闭
  setTimeout(() => {
    visible.value = false
  }, props.duration)
})

// 通知关闭后销毁组件
watch(visible, (newVal) => {
  if (!newVal) {
    // 等待动画完成后再销毁
    setTimeout(() => {
      emit('close')
    }, 300) // 与 CSS 动画时间一致
  }
})
</script>

<template>
  <transition name="fade">
    <div 
      v-if="visible" 
      ref="notifyRef"
      class="notify" 
      :class="[type]"
    >
      <span class="icon">
        <svg v-if="type === 'success'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 16.2l-3.5-3.5 1.4-1.4L9 13.4l8.1-8.1 1.4 1.4L9 16.2z"/>
        </svg>
        <svg v-if="type === 'error'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
        </svg>
        <svg v-if="type === 'warning'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
        </svg>
        <svg v-if="type === 'info'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
        </svg>
      </span>
      <span class="message">{{ message }}</span>
    </div>
  </transition>
</template>

<style scoped>
.notify {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  font-size: 14px;
  color: #fff;
  min-height: 30px; /* 确保最小高度一致 */
  word-wrap: break-word;
}

.success {
  background-color: #28a745;
}

.error {
  background-color: #dc3545;
}

.warning {
  background-color: #ffc107;
  color: #333;
}

.info {
  background-color: #17a2b8;
}

.icon {
  margin-right: 10px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.icon svg {
  width: 20px;
  height: 20px;
}

.message {
  flex: 1;
  line-height: 1.5;
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

@media (max-width: 768px) {
  .notify {
    max-width: calc(100vw - 40px);
    font-size: 13px;
    padding: 10px 15px;
    min-height: 40px;
  }

  .icon svg {
    width: 18px;
    height: 18px;
  }
}</style>