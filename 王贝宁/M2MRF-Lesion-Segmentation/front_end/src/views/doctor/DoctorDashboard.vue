<template>
  <div class="dashboard-container">
    <el-container>
      <!-- 左侧导航栏 -->
      <el-aside width="220px">
        <div class="logo-container">
          <h3>AI 诊断系统</h3>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          @select="handleSelect"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="dashboard">
            <el-icon><DataLine /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <el-sub-menu index="diagnosis">
            <template #title>
              <el-icon><Upload /></el-icon>
              <span>AI 诊断</span>
            </template>
            <el-menu-item index="diagnosis-new">上传图片诊断</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="reports">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>报告管理</span>
            </template>
            <el-menu-item index="reports-pending">待审核报告</el-menu-item>
            <el-menu-item index="reports-list">已审核报告</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧内容区 -->
      <el-container>
        <el-header>
          <div class="header-content">
            <div class="header-left">
              <h2>糖尿病视网膜病变 AI 诊断系统</h2>
            </div>
            <div class="header-right">
              <el-dropdown>
                <span class="user-info">
                  <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                  <span class="username">张医生</span>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>

        <el-main>
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  DataLine, 
  Upload,
  Document, 
  Setting 
} from '@element-plus/icons-vue'

const router = useRouter()
const activeMenu = ref('dashboard')

const handleSelect = (key) => {
  activeMenu.value = key
  // 根据菜单项跳转到对应路由
  switch (key) {
    case 'dashboard':
      router.push('/dashboard/doctor')
      break
    case 'diagnosis-new':
      router.push('/dashboard/doctor/diagnosis/new')
      break
    case 'diagnosis-history':
      router.push('/dashboard/doctor/diagnosis/history')
      break
    case 'reports-pending':
      router.push('/dashboard/doctor/reports/pending')
      break
    case 'reports-list':
      router.push('/dashboard/doctor/reports/list')
      break
    case 'settings':
      router.push('/dashboard/doctor/settings')
      break
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
  color: #fff;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3649;
}

.logo-container h3 {
  color: #fff;
  margin: 0;
  font-size: 18px;
}

.el-menu {
  border-right: none;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  padding: 0 20px;
  position: fixed;
  width: calc(100% - 220px);
  margin-left: 220px;
  z-index: 999;
}

.header-content {
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h2 {
  margin: 0;
  color: #409EFF;
  font-size: 24px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  color: #606266;
}

.el-main {
  background-color: #f5f7fa;
  padding: 20px;
  margin-top: 60px;
  margin-left: 220px;
  min-height: calc(100vh - 60px);
}

.el-menu-vertical {
  height: calc(100vh - 60px);
}

/* 路由切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 