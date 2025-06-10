<template>
  <div class="new-diagnosis">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>AI 辅助诊断</span>
        </div>
      </template>

      <div class="upload-section">
        <el-upload
          class="upload-area"
          drag
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleFileChange"
          :before-upload="beforeUpload"
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
        <!-- 添加病人信息输入区域 -->
        <div v-if="segmentedImgUrl" class="patient-info-section">
          <el-form :model="patientForm" :rules="rules" ref="patientFormRef" label-width="100px">
            <el-form-item label="病人姓名" prop="patientName">
              <el-input v-model="patientForm.patientName" placeholder="请输入病人姓名"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSubmitDiagnosis" :loading="submitting">
                提交诊断
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <div v-if="currentImage" class="diagnosis-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="image-preview">
              <el-image
                :src="currentImage.url"
                fit="contain"
                :preview-src-list="[currentImage.url]"
              />
              <div v-if="lesionBoxes.length > 0" class="lesion-overlay">
                <div
                  v-for="(box, index) in lesionBoxes"
                  :key="index"
                  class="lesion-box"
                  :style="{
                    left: box.x + '%',
                    top: box.y + '%',
                    width: box.width + '%',
                    height: box.height + '%'
                  }"
                >
                  <span class="lesion-label">{{ index + 1 }}</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="diagnosis-result">
              <h3>AI 诊断结果</h3>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="病灶数量">
                  {{ lesionCount }}
                </el-descriptions-item>
                <el-descriptions-item label="AI 诊断">
                  <el-tag :type="getDiagnosisType(aiDiagnosis)">
                    {{ aiDiagnosis }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="置信度">
                  {{ confidence }}%
                </el-descriptions-item>
              </el-descriptions>

              <div class="lesion-list" v-if="lesionBoxes.length > 0">
                <h4>病灶详情</h4>
                <el-table :data="lesionDetails" style="width: 100%">
                  <el-table-column prop="id" label="编号" width="80" />
                  <el-table-column prop="type" label="类型" width="120" />
                  <el-table-column prop="confidence" label="置信度" width="100">
                    <template #default="{ row }">
                      {{ row.confidence }}%
                    </template>
                  </el-table-column>
                  <el-table-column prop="description" label="描述" />
                </el-table>
              </div>

              <div class="action-buttons">
                <el-button type="primary" @click="startDiagnosis" :loading="diagnosing">
                  开始诊断
                </el-button>
                <el-button @click="resetDiagnosis">重置</el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { uploadImageForSegmentation, submitDiagnosis as submitDiagnosisApi } from '@/api/diagnosis'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const patientFormRef = ref(null)
const submitting = ref(false)

// 当前图片
const currentImage = ref(null)
// 诊断状态
const diagnosing = ref(false)
// 病灶数量
const lesionCount = ref(0)
// AI 诊断结果
const aiDiagnosis = ref('')
// 置信度
const confidence = ref(0)
// 病灶框
const lesionBoxes = ref([])
// 病灶详情
const lesionDetails = ref([])

// 病人信息表单
const patientForm = ref({
  patientName: ''
})

// 表单验证规则
const rules = {
  patientName: [
    { required: true, message: '请输入病人姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ]
}

// 上传前验证
const beforeUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/jpg'
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isJPG) {
    ElMessage.error('只能上传 JPG 格式的图片！')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB！')
    return false
  }
  return true
}

const segmentedImgUrl = ref('')

const handleFileChange = async (file) => {
  if (!file) return
  try {
    ElMessage.info('正在上传图片并分割...')
    const blob = await uploadImageForSegmentation(file.raw)
    segmentedImgUrl.value = URL.createObjectURL(blob)
    ElMessage.success('分割完成')
  } catch (error) {
    ElMessage.error('分割失败：' + (error.message || '未知错误'))
  }
}

// 开始诊断
const startDiagnosis = async () => {
  if (!currentImage.value) {
    ElMessage.warning('请先上传图片')
    return
  }

  diagnosing.value = true

  try {
    // TODO: 调用后端 API 进行诊断
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 模拟诊断结果
    lesionCount.value = 3
    aiDiagnosis.value = '轻度病变'
    confidence.value = 95
    lesionBoxes.value = [
      { x: 20, y: 30, width: 10, height: 10 },
      { x: 50, y: 40, width: 8, height: 8 },
      { x: 70, y: 60, width: 12, height: 12 }
    ]
    lesionDetails.value = [
      { id: 1, type: '微动脉瘤', confidence: 98, description: '位于视网膜上方' },
      { id: 2, type: '出血点', confidence: 95, description: '位于视网膜下方' },
      { id: 3, type: '硬性渗出', confidence: 92, description: '位于视网膜中央' }
    ]

    ElMessage.success('诊断完成')
  } catch (error) {
    ElMessage.error('诊断失败：' + error.message)
  } finally {
    diagnosing.value = false
  }
}

// 重置诊断
const resetDiagnosis = () => {
  lesionCount.value = 0
  aiDiagnosis.value = ''
  confidence.value = 0
  lesionBoxes.value = []
  lesionDetails.value = []
}

// 获取诊断结果对应的标签类型
const getDiagnosisType = (diagnosis) => {
  switch (diagnosis) {
    case '正常':
      return 'success'
    case '轻度病变':
      return 'warning'
    case '中度病变':
      return 'danger'
    default:
      return 'info'
  }
}

// 提交诊断
const handleSubmitDiagnosis = async () => {
  if (!patientFormRef.value) return
  
  await patientFormRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.warning('请填写完整的病人信息')
      return
    }

    if (!segmentedImgUrl.value) {
      ElMessage.warning('请先上传并分割图片')
      return
    }

    submitting.value = true
    try {
      // 获取token中的医生ID
      const tokenStr = localStorage.getItem('token')
      if (!tokenStr) {
        throw new Error('未登录')
      }
      const token = JSON.parse(tokenStr)
      const doctor_id = token.doctor_id

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
        patient_id: 1, // 临时使用固定值，实际应该根据病人姓名查询或创建
        doctor_id: doctor_id,
        image_path: imageData, // base64编码的图片数据
        confirmed: false
      }
      
      // 调用API提交诊断
      const result = await submitDiagnosisApi(diagnosisData)
      ElMessage.success('诊断结果已保存')
      
      // 重置表单和图片
      patientForm.value.patientName = ''
      segmentedImgUrl.value = ''
      currentImage.value = null
      
      // 跳转到未审核报告页面
      router.push('/dashboard/doctor/reports/pending')
    } catch (error) {
      console.error('保存诊断结果失败:', error)
      ElMessage.error('保存诊断结果失败：' + (error.response?.data?.error || error.message))
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.new-diagnosis {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-section {
  margin-bottom: 20px;
}

.upload-area {
  width: 100%;
}

.diagnosis-section {
  margin-top: 20px;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 400px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.lesion-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.lesion-box {
  position: absolute;
  border: 2px solid #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
}

.lesion-label {
  position: absolute;
  top: -20px;
  left: -20px;
  width: 20px;
  height: 20px;
  background-color: #f56c6c;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.diagnosis-result {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.lesion-list {
  margin-top: 20px;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-descriptions) {
  margin-top: 20px;
}

.patient-info-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style> 