<template>
  <div class="dashboard-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>糖尿病视网膜病变 AI 诊断系统</h2>
          <el-button type="danger" @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <el-tabs v-model="activeTab" class="patient-tabs">
          <el-tab-pane label="上传诊断" name="upload">
            <upload-panel @upload-success="handleUploadSuccess" />
            <result-panel
              v-if="currentImage"
              :image-src="currentImage"
              :lesion-count="lesionCount"
              :boxes="lesionBoxes"
            />
          </el-tab-pane>
          <el-tab-pane label="我的报告" name="reports">
            <case-table :is-patient="true" />
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UploadPanel from '@/components/UploadPanel.vue'
import ResultPanel from '@/components/ResultPanel.vue'
import CaseTable from '@/components/CaseTable.vue'

const router = useRouter()
const activeTab = ref('upload')
const currentImage = ref(null)
const lesionCount = ref(0)
const lesionBoxes = ref([])

const handleUploadSuccess = (file) => {
  currentImage.value = URL.createObjectURL(file)
  // 模拟 AI 分析结果
  lesionCount.value = Math.floor(Math.random() * 5)
  lesionBoxes.value = Array(lesionCount.value).fill().map(() => ({
    x: Math.random() * 100,
    y: Math.random() * 100,
    width: Math.random() * 20 + 10,
    height: Math.random() * 20 + 10
  }))
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

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  padding: 0 20px;
}

.header-content {
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-main {
  background-color: #f5f7fa;
  padding: 20px;
}

h2 {
  margin: 0;
  color: #409EFF;
  font-size: 24px;
}

.patient-tabs {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
</style> 