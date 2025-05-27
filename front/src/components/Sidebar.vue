<template>
  <div class="sidebar-container">
    <!-- 遮罩层 (移动端) -->
    <div 
      v-if="isOpen && isMobile" 
      class="overlay"
      @click="closeSidebar"
    ></div>
    
    <!-- 侧边栏 -->
    <aside 
      :class="sidebarClasses"
      class="sidebar"
    >
      <!-- 侧边栏头部 -->
      <div class="sidebar-header">
        <slot name="header">
          <h2 class="sidebar-title">菜单</h2>
        </slot>
        
        <!-- 关闭按钮 (移动端) -->
        <button 
          v-if="isMobile"
          @click="closeSidebar"
          class="close-btn"
          aria-label="关闭侧边栏"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      
      <!-- 侧边栏内容 -->
      <div class="sidebar-content">
        <slot name="content">
          <nav class="sidebar-nav">
            <ul class="nav-list">
              <li v-for="item in menuItems" :key="item.id" class="nav-item">
                <a 
                  :href="item.href" 
                  :class="{ active: item.active }"
                  class="nav-link"
                  @click="handleNavClick(item)"
                >
                  <span v-if="item.icon" class="nav-icon" v-html="item.icon"></span>
                  <span class="nav-text">{{ item.text }}</span>
                </a>
              </li>
            </ul>
          </nav>
        </slot>
      </div>
      
      <!-- 侧边栏底部 -->
      <div class="sidebar-footer" v-if="$slots.footer">
        <slot name="footer"></slot>
      </div>
    </aside>
    
    <!-- 切换按钮 -->
    <button 
      v-if="showToggleButton"
      @click="toggleSidebar"
      class="toggle-btn"
      :class="{ 'sidebar-open': isOpen }"
      aria-label="切换侧边栏"
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

// 定义接口
interface MenuItem {
  id: string | number
  text: string
  href: string
  icon?: string
  active?: boolean
}

interface Props {
  modelValue?: boolean
  position?: 'left' | 'right'
  width?: string
  showToggleButton?: boolean
  persistent?: boolean
  menuItems?: MenuItem[]
  breakpoint?: number
}

// 定义 Props
const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  position: 'left',
  width: '280px',
  showToggleButton: true,
  persistent: false,
  breakpoint: 768,
  menuItems: () => [
    { id: 1, text: '首页', href: '#/', icon: '🏠', active: true },
    { id: 2, text: '产品', href: '#/products', icon: '📦' },
    { id: 3, text: '服务', href: '#/services', icon: '⚙️' },
    { id: 4, text: '关于', href: '#/about', icon: 'ℹ️' },
    { id: 5, text: '联系', href: '#/contact', icon: '📞' }
  ]
})

// 定义 Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'open': []
  'close': []
  'nav-click': [item: MenuItem]
}>()

// 响应式数据
const windowWidth = ref(window.innerWidth)
const isOpen = ref(props.modelValue)

// 计算属性
const isMobile = computed(() => windowWidth.value < props.breakpoint)

const sidebarClasses = computed(() => [
  `sidebar-${props.position}`,
  {
    'sidebar-open': isOpen.value,
    'sidebar-mobile': isMobile.value,
    'sidebar-desktop': !isMobile.value,
    'sidebar-persistent': props.persistent && !isMobile.value
  }
])

// 方法
const updateWindowWidth = () => {
  windowWidth.value = window.innerWidth
}

const toggleSidebar = () => {
  isOpen.value = !isOpen.value
}

const openSidebar = () => {
  isOpen.value = true
}

const closeSidebar = () => {
  isOpen.value = false
}

const handleNavClick = (item: MenuItem) => {
  emit('nav-click', item)
  
  // 移动端点击导航后自动关闭侧边栏
  if (isMobile.value) {
    closeSidebar()
  }
}

// 监听器
watch(() => props.modelValue, (newVal) => {
  isOpen.value = newVal
})

watch(isOpen, (newVal) => {
  emit('update:modelValue', newVal)
  if (newVal) {
    emit('open')
  } else {
    emit('close')
  }
})

// 监听屏幕尺寸变化，桌面端自动打开侧边栏
watch(isMobile, (newVal, oldVal) => {
  if (oldVal && !newVal && props.persistent) {
    // 从移动端切换到桌面端
    openSidebar()
  } else if (!oldVal && newVal) {
    // 从桌面端切换到移动端
    closeSidebar()
  }
})

// 生命周期
onMounted(() => {
  window.addEventListener('resize', updateWindowWidth)
  
  // 桌面端且持久化模式下默认打开
  if (!isMobile.value && props.persistent) {
    openSidebar()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWindowWidth)
})

// 暴露方法给父组件
defineExpose({
  open: openSidebar,
  close: closeSidebar,
  toggle: toggleSidebar,
  isOpen: computed(() => isOpen.value),
  isMobile: computed(() => isMobile.value)
})
</script>

<style scoped>
.sidebar-container {
  position: relative;
}

/* 遮罩层 */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 998;
  transition: opacity 0.3s ease;
}

/* 侧边栏主体 */
.sidebar {
  position: fixed;
  top: 0;
  bottom: 0;
  width: v-bind(width);
  background-color: #ffffff;
  border-right: 1px solid #e5e7eb;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 999;
  transition: transform 0.3s ease;
}

/* 左侧侧边栏 */
.sidebar-left {
  left: 0;
  transform: translateX(-100%);
}

.sidebar-left.sidebar-open {
  transform: translateX(0);
}

/* 右侧侧边栏 */
.sidebar-right {
  right: 0;
  border-right: none;
  border-left: 1px solid #e5e7eb;
  transform: translateX(100%);
}

.sidebar-right.sidebar-open {
  transform: translateX(0);
}

/* 桌面端持久化模式 */
.sidebar-persistent {
  position: relative;
  transform: none !important;
  box-shadow: none;
  border-right: 1px solid #e5e7eb;
}

/* 侧边栏头部 */
.sidebar-header {
  padding: 1.5rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f9fafb;
}

.sidebar-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  color: #6b7280;
  border-radius: 0.375rem;
  transition: background-color 0.2s ease;
}

.close-btn:hover {
  background-color: #e5e7eb;
  color: #374151;
}

/* 侧边栏内容 */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

/* 导航样式 */
.sidebar-nav {
  padding: 0 1rem;
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin-bottom: 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: #6b7280;
  text-decoration: none;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.nav-link.active {
  background-color: #3b82f6;
  color: white;
}

.nav-icon {
  margin-right: 0.75rem;
  font-size: 1.25rem;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-text {
  font-weight: 500;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

/* 切换按钮 */
.toggle-btn {
  position: fixed;
  top: 1rem;
  left: 1rem;
  z-index: 1000;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem;
  cursor: pointer;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background-color: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
}

.toggle-btn.sidebar-open {
  transform: translateX(calc(v-bind(width) - 1rem));
}

/* 右侧切换按钮位置调整 */
.sidebar-right ~ .toggle-btn {
  left: auto;
  right: 1rem;
}

.sidebar-right ~ .toggle-btn.sidebar-open {
  transform: translateX(calc(-1 * v-bind(width) + 1rem));
}

/* 响应式样式 */
@media (max-width: 768px) {
  .sidebar {
    width: 85vw;
    max-width: 320px;
  }
  
  .toggle-btn.sidebar-open {
    transform: none;
  }
  
  .sidebar-right ~ .toggle-btn.sidebar-open {
    transform: none;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .sidebar {
    background-color: #1f2937;
    border-color: #374151;
  }
  
  .sidebar-header {
    background-color: #111827;
    border-color: #374151;
  }
  
  .sidebar-title {
    color: #f9fafb;
  }
  
  .close-btn {
    color: #9ca3af;
  }
  
  .close-btn:hover {
    background-color: #374151;
    color: #f9fafb;
  }
  
  .nav-link {
    color: #9ca3af;
  }
  
  .nav-link:hover {
    background-color: #374151;
    color: #f9fafb;
  }
  
  .sidebar-footer {
    background-color: #111827;
    border-color: #374151;
  }
}
</style>