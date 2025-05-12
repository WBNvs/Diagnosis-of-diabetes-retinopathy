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
      accept="image/*"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 jpg/png 格式的眼底图像
        </div>
      </template>
    </el-upload>
  </el-card>
</template>

<script setup>
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['upload-success'])

const handleFileChange = (file) => {
  if (file) {
    ElMessage.success('文件上传成功')
    emit('upload-success', file.raw)
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