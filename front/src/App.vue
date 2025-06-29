<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'


const sidebarOpen = ref(false)
const customMenuItems = ref([
  { id: 1, text: '首页', href: '/', icon: '🏠' },
  { id: 2, text: '角色信息', href: '/characters', icon: '👤' },
  { id: 3, text: '创建角色', href: '/character/create', icon: '➕' },
  { id: 4, text: '小说信息', href: '/novels', icon: '📖' },
  { id: 5, text: '创建小说', href: '/novel/create', icon: '➕' },
])

const route = useRoute()
</script>

<template>
    <el-drawer v-model="sidebarOpen" title="菜单" direction="ltr" size="280px">
      <el-menu :default-active="route.path" router @select="sidebarOpen = false">
        <el-menu-item v-for="item in customMenuItems" :key="item.id" :index="item.href">
          <span class="menu-icon" v-html="item.icon"></span>
          <span>{{ item.text }}</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>

  <el-container class="app-container">
    <el-header class="app-header">
      <el-button @click="sidebarOpen = !sidebarOpen" icon="Menu" circle />
      <span style="margin-left: 15px; font-size: 1.2em;">QuickNovel</span>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
}

.app-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.app-main {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.menu-icon {
  margin-right: 10px;
  font-size: 1.2rem;
  width: 24px;
  text-align: center;
}
</style>