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
          accept="image/*"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">
            将眼底图片拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 jpg、png 格式的眼底图片
            </div>
          </template>
        </el-upload>
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

// 处理文件选择
const handleFileChange = (file) => {
  if (!file) return
  
  // 检查文件类型
  const isImage = file.raw.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('请上传图片文件')
    return
  }

  // 创建预览URL
  const url = URL.createObjectURL(file.raw)
  currentImage.value = {
    file: file.raw,
    url
  }

  // 重置诊断结果
  resetDiagnosis()
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
</style> 