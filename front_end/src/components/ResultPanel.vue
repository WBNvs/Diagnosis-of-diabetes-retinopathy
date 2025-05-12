<template>
  <el-card class="result-panel">
    <template #header>
      <div class="card-header">
        <span>诊断结果</span>
      </div>
    </template>
    <div class="result-content">
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="image-preview">
            <img :src="imageSrc" alt="眼底图像预览" />
            <div class="lesion-boxes">
              <div
                v-for="(box, index) in boxes"
                :key="index"
                class="lesion-box"
                :style="{
                  left: box.x + '%',
                  top: box.y + '%',
                  width: box.width + '%',
                  height: box.height + '%'
                }"
              ></div>
            </div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="diagnosis-info">
            <h3>诊断信息</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="病灶数量">
                <el-tag :type="lesionCount > 0 ? 'danger' : 'success'">
                  {{ lesionCount }} 个
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="诊断时间">
                {{ new Date().toLocaleString() }}
              </el-descriptions-item>
              <el-descriptions-item label="建议">
                <p v-if="lesionCount === 0">
                  未发现明显病变，建议定期复查。
                </p>
                <p v-else>
                  发现 {{ lesionCount }} 处病变，建议及时就医。
                </p>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-col>
      </el-row>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  imageSrc: {
    type: String,
    required: true
  },
  lesionCount: {
    type: Number,
    default: 0
  },
  boxes: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.result-panel {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-content {
  padding: 10px 0;
}

.image-preview {
  width: 100%;
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.image-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.lesion-boxes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.lesion-box {
  position: absolute;
  border: 2px solid #f56c6c;
  background-color: rgba(245, 108, 108, 0.2);
}

.diagnosis-info {
  height: 100%;
}

.diagnosis-info h3 {
  margin-bottom: 20px;
  color: #303133;
}
</style> 