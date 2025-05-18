<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  title: string
  message: string
  confirmText?: string
  cancelText?: string
}>()

const visible = ref(true)

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
  (e: 'close'): void
}>()

// 处理确认
const handleConfirm = () => {
  visible.value = false
  emit('confirm')
}

// 处理取消
const handleCancel = () => {
  visible.value = false
  emit('cancel')
}

// 动画结束后销毁
const handleClose = () => {
  if (!visible.value) {
    setTimeout(() => {
      emit('close')
    }, 300) // 与CSS动画时间一致
  }
}
</script>

<template>
  <transition name="dialog-fade" @after-leave="handleClose">
    <div v-if="visible" class="dialog-overlay">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ title }}</h3>
        </div>
        <div class="dialog-body">
          <p>{{ message }}</p>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-cancel" @click="handleCancel">
            {{ cancelText || '取消' }}
          </button>
          <button class="btn btn-confirm" @click="handleConfirm">
            {{ confirmText || '确认' }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
}

.dialog {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 400px;
  overflow: hidden;
}

.dialog-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.dialog-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.dialog-body {
  padding: 20px;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.dialog-footer {
  padding: 12px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  background: #f8f8f8;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.btn-confirm {
  background-color: #dc3545;
  color: white;
}

.btn-confirm:hover {
  background-color: #c81333;
}

/* 动画效果 */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog .dialog-enter-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.dialog .dialog-enter-from,
.dialog .dialog-leave-to {
  transform: scale(0.95);
  opacity: 0;
}

@media (max-width: 768px) {
  .dialog {
    max-width: calc(100% - 20px);
    margin: 0 10px;
  }

  .dialog-header h3 {
    font-size: 15px;
  }

  .dialog-body {
    font-size: 13px;
    padding: 15px;
  }

  .btn {
    padding: 6px 12px;
    font-size: 13px;
  }
}
</style>