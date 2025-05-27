<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed, ref } from 'vue'
import Sidebar from './components/Sidebar.vue'


const route = useRoute()
const sidebarOpen = ref(false)
const customMenuItems = ref([
  { id: 1, text: '首页', href: '/', icon: '🏠' },
  { id: 2, text: '角色信息', href: '/characters', icon: '👤' },
  { id: 3, text: '创建角色', href: '/character/create', icon: '➕' },
  { id: 4, text: '聊天', href: '/chatting', icon: '💬' }
])

// 计算面包屑路径
const breadcrumbs = computed(() => {
  const matched = route.matched
  const crumbs: any[] = []
  matched.forEach((r, index) => {
    if (r.name && r.path !== '') {
      crumbs.push({
        name: r.name,
        path: r.path,
        isLast: index === matched.length - 1
      })
    }
  })
  return crumbs
})
</script>

<template>
    <Sidebar 
      v-model="sidebarOpen"
      :menu-items="customMenuItems"></Sidebar>

  <div id="app">
    <!-- 面包屑导航 -->
    <nav class="breadcrumbs">
      <span v-for="(crumb, index) in breadcrumbs" :key="crumb.path">
        <span v-if="index > 0"> / </span>
        <router-link
          v-if="!crumb.isLast"
          :to="crumb.path"
          class="breadcrumb-link"
        >
          {{ crumb.name }}
        </router-link>
        <span v-else class="breadcrumb-current">{{ crumb.name }}</span>
      </span>
    </nav>

    <!-- 内容区域 -->
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
#app {
  max-width: 1200px;
  margin: 0 auto;
}

.top-nav {
  background-color: #f8f9fa;
  padding: 10px 20px;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-buttons {
  display: flex;
  gap: 10px;
}

.nav-buttons button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.nav-buttons button:hover {
  background-color: #0056b3;
}

.nav-buttons button.active {
  background-color: #0056b3;
  font-weight: bold;
}

.breadcrumbs {
  padding: 10px 20px;
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
}

.breadcrumb-link {
  color: #007bff;
  text-decoration: none;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.breadcrumb-current {
  color: #333;
  font-weight: bold;
}

.content {
  padding: 20px;
}

@media (max-width: 768px) {
  .nav-buttons {
    flex-wrap: wrap;
    gap: 8px;
  }

  .nav-buttons button {
    padding: 6px 12px;
    font-size: 0.9em;
  }

  .breadcrumbs {
    font-size: 0.9em;
    padding: 8px 15px;
  }
}
</style>