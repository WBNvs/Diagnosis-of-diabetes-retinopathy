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
            <el-upload
              class="upload-area"
              drag
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="(file) => handleFileChange(file.raw)"
              accept="image/jpeg,image/jpg"
            >
              <el-icon class="el-icon--upload"><Upload /></el-icon>
              <div class="el-upload__text">
                将眼底图片拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持.jpg格式的眼底图片，大小不超过10MB
                </div>
              </template>
            </el-upload>

            <!-- 分割结果图片预览 -->
            <el-image
              v-if="segmentedImgUrl"
              :src="segmentedImgUrl"
              fit="contain"
              style="margin-top: 20px; max-width: 100%; max-height: 400px;"
            />
            <div
              v-if="segmentedImgUrl"
              style="margin-top: 10px; color: #f56c6c; font-size: 14px; text-align: center;"
            >
              本图片是AI分割结果，仅供参考，需等待医生审核
            </div>
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
import { uploadImageForSegmentation } from '@/api/diagnosis'
import { ElMessage } from 'element-plus'

const router = useRouter()
const activeTab = ref('upload')
const currentImage = ref(null)
const lesionCount = ref(0)
const lesionBoxes = ref([])
const segmentedImgUrl = ref('')
const uploading = ref(false)

const handleFileChange = async (file) => {
  if (!file) return
  try {
    uploading.value = true
    ElMessage.info('正在上传图片并分割...')
    const blob = await uploadImageForSegmentation(file)
    segmentedImgUrl.value = URL.createObjectURL(blob)
    ElMessage.success('分割完成')
  } catch (error) {
    ElMessage.error('分割失败：' + (error.message || '未知错误'))
  } finally {
    uploading.value = false
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