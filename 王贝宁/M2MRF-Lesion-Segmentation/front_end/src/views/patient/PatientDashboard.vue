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
        <router-view v-if="$route.name === 'PatientReportDetail'"></router-view>
        <div v-else class="main-content">
          <div class="menu-tabs">
            <div 
              class="menu-item" 
              :class="{ active: activeTab === 'upload' }"
              @click="activeTab = 'upload'"
            >
              <el-icon><Upload /></el-icon>
              <span>上传诊断</span>
            </div>
            <div 
              class="menu-item" 
              :class="{ active: activeTab === 'reports' }"
              @click="activeTab = 'reports'"
            >
              <el-icon><Document /></el-icon>
              <span>我的报告</span>
            </div>
          </div>

          <div class="content-area">
            <div v-if="activeTab === 'upload'" class="upload-section">
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

              <!-- 添加医生信息输入区域 -->
              <div v-if="segmentedImgUrl" class="doctor-info-section">
                <el-form :model="doctorForm" :rules="rules" ref="doctorFormRef" label-width="100px">
                  <el-form-item label="医生姓名" prop="doctorName">
                    <el-input v-model="doctorForm.doctorName" placeholder="请输入医生姓名"></el-input>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="handleSubmit" :loading="submitting">
                      提交诊断
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </div>
            <div v-else-if="activeTab === 'reports'" class="reports-section">
              <case-table :is-patient="true" :key="tableKey" />
            </div>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Upload, Document } from '@element-plus/icons-vue'
import UploadPanel from '@/components/UploadPanel.vue'
import ResultPanel from '@/components/ResultPanel.vue'
import CaseTable from '@/components/CaseTable.vue'
import { uploadImageForSegmentation, submitDiagnosis } from '@/api/diagnosis'
import { ElMessage } from 'element-plus'

const router = useRouter()
const activeTab = ref('upload')
const currentImage = ref(null)
const lesionCount = ref(0)
const lesionBoxes = ref([])
const segmentedImgUrl = ref('')
const uploading = ref(false)
const submitting = ref(false)
const doctorFormRef = ref(null)
const tableKey = ref(0)

// 医生信息表单
const doctorForm = ref({
  doctorName: ''
})

// 表单验证规则
const rules = {
  doctorName: [
    { required: true, message: '请输入医生姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ]
}

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

// 提交诊断
const handleSubmit = async () => {
  if (!doctorFormRef.value) return
  
  await doctorFormRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.warning('请填写医生姓名')
      return
    }

    if (!segmentedImgUrl.value) {
      ElMessage.warning('请先上传并分割图片')
      return
    }

    submitting.value = true
    try {
      // 获取token中的患者ID
      const tokenStr = localStorage.getItem('token')
      if (!tokenStr) {
        throw new Error('未登录')
      }
      const token = JSON.parse(tokenStr)
      const patient_id = token.patient_id

      // 将图片转换为base64
      const response = await fetch(segmentedImgUrl.value)
      const blob = await response.blob()
      const reader = new FileReader()
      const base64Promise = new Promise((resolve, reject) => {
        reader.onload = () => resolve(reader.result)
        reader.onerror = reject
        reader.readAsDataURL(blob)
      })
      const imageData = await base64Promise

      // 准备诊断数据
      const diagnosisData = {
        patient_id: patient_id,
        doctor_id: 1, // 添加默认的doctor_id
        image_path: imageData, // base64编码的图片数据
        confirmed: false
      }
      
      // 调用API提交诊断
      await submitDiagnosis(diagnosisData)
      ElMessage.success('诊断申请已提交')
      
      // 重置表单和图片
      doctorForm.value.doctorName = ''
      segmentedImgUrl.value = ''
      
      // 刷新表格数据
      tableKey.value++
      
      // 切换到报告列表页面
      activeTab.value = 'reports'
    } catch (error) {
      console.error('提交诊断失败:', error)
      ElMessage.error('提交诊断失败：' + (error.response?.data?.error || error.message))
    } finally {
      submitting.value = false
    }
  })
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

.main-content {
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  overflow: hidden;
}

.menu-tabs {
  display: flex;
  background-color: #304156;
  padding: 0;
  margin: 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 50px;
  color: #bfcbd9;
  cursor: pointer;
  transition: all 0.3s;
}

.menu-item:hover {
  color: #fff;
  background-color: #263445;
}

.menu-item.active {
  color: #409EFF;
  background-color: #fff;
}

.menu-item .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

.content-area {
  padding: 20px;
  flex: 1;
}

.upload-section {
  max-width: 800px;
  margin: 0 auto;
}

.doctor-info-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.upload-area {
  width: 100%;
}

.el-upload {
  width: 100%;
}

.el-upload-dragger {
  width: 100%;
  height: 300px;
}

.el-icon--upload {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 16px;
}

.el-upload__text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

.el-upload__text em {
  color: #409EFF;
  font-style: normal;
}

.el-upload__tip {
  font-size: 14px;
  color: #909399;
}
</style> 