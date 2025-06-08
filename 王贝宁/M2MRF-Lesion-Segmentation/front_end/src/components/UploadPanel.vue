<template>
  <el-card class="upload-panel">
    <template #header>
      <div class="card-header">
        <span>上传眼底图像</span>
      </div>
    </template>
    <el-upload
      class="upload-area"
      drag
      action="#"
      :auto-upload="false"
      :on-change="handleFileChange"
      :before-upload="beforeUpload"
      accept="image/jpeg,image/jpg"
      :show-file-list="false"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 jpg 格式的眼底图像，文件大小不超过 10MB
        </div>
      </template>
    </el-upload>
  </el-card>
</template>

<script setup>
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { uploadImageForDiagnosis } from '@/api/diagnosis'

const emit = defineEmits(['upload-success', 'upload-error'])

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

// 处理文件选择
const handleFileChange = async (file) => {
  if (!file) return
  
  try {
    // 显示上传中提示
    ElMessage.info('正在上传图片...')
    
    // 调用API上传图片
    const result = await uploadImageForDiagnosis(file.raw)
    
    // 上传成功
    ElMessage.success('图片上传成功')
    emit('upload-success', {
      file: file.raw,
      result: result
    })
  } catch (error) {
    // 上传失败
    ElMessage.error('图片上传失败：' + (error.message || '未知错误'))
    emit('upload-error', error)
  }
}
</script>

<style scoped>
.upload-panel {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-area {
  width: 100%;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 7px;
}

:deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
}
</style> 