<template>
  <router-view v-if="$route.path === '/login'" />
  <el-container v-else class="app-shell">
    <el-aside width="220px" class="aside">
      <div class="brand">电商风控系统</div>
      <el-menu router :default-active="$route.path" class="menu">
        <el-menu-item v-for="menu in authStore.menus" :key="menu.menu_code" :index="menu.route_path">
          {{ menu.menu_name }}
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>实时风险控制平台</span>
        <div class="user-box">
          <span class="user">{{ authStore.user?.real_name }} {{ authStore.user?.username }}</span>
          <el-button size="small" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { authStore } from './stores/auth'

const router = useRouter()

function logout() {
  authStore.logout()
  router.replace('/login')
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.aside {
  border-right: 1px solid #e5e7eb;
  background: #fff;
}

.brand {
  height: 56px;
  padding: 0 18px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 17px;
  font-weight: 700;
  line-height: 56px;
}

.menu {
  border-right: 0;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}

.user {
  color: #6b7280;
  font-size: 14px;
}

.user-box {
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>
