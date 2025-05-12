<template>
  <div class="report-detail">
    <el-card class="report-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack">返回</el-button>
            <span class="title">诊断报告详情</span>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="handlePrint">打印报告</el-button>
          </div>
        </div>
      </template>

      <div class="report-content">
        <!-- 基本信息 -->
        <div class="section">
          <h3>基本信息</h3>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="报告编号">{{ reportInfo.reportId }}</el-descriptions-item>
            <el-descriptions-item label="患者姓名">{{ reportInfo.patientName }}</el-descriptions-item>
            <el-descriptions-item label="患者ID">{{ reportInfo.patientId }}</el-descriptions-item>
            <el-descriptions-item label="检查日期">{{ reportInfo.checkDate }}</el-descriptions-item>
            <el-descriptions-item label="诊断时间">{{ reportInfo.diagnosisTime }}</el-descriptions-item>
            <el-descriptions-item label="诊断医生">{{ reportInfo.doctor }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 眼底图像 -->
        <div class="section">
          <h3>眼底图像</h3>
          <div class="image-container">
            <img :src="reportInfo.imageUrl" class="fundus-image" />
            <div class="image-markers">
              <div v-for="(marker, index) in reportInfo.lesions" :key="index" class="marker">
                <el-tag :type="marker.severity === 'high' ? 'danger' : 'warning'">
                  {{ marker.description }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 诊断结果 -->
        <div class="section">
          <h3>诊断结果</h3>
          <el-alert
            :title="reportInfo.diagnosisResult.title"
            :type="reportInfo.diagnosisResult.type"
            :description="reportInfo.diagnosisResult.description"
            show-icon
          />
        </div>

        <!-- 病灶详情 -->
        <div class="section">
          <h3>病灶详情</h3>
          <el-table :data="reportInfo.lesions" style="width: 100%">
            <el-table-column prop="type" label="病灶类型" width="150" />
            <el-table-column prop="location" label="位置" width="150" />
            <el-table-column prop="severity" label="严重程度" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.severity === 'high' ? 'danger' : 'warning'">
                  {{ scope.row.severity === 'high' ? '严重' : '中等' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" />
          </el-table>
        </div>

        <!-- 医生建议 -->
        <div class="section">
          <h3>医生建议</h3>
          <div class="suggestion-content">
            {{ reportInfo.suggestion }}
          </div>
        </div>

        <!-- 审核信息 -->
        <div class="section" v-if="reportInfo.status !== '待审核'">
          <h3>审核信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="审核状态">
              <el-tag :type="getStatusType(reportInfo.status)">
                {{ reportInfo.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="审核医生">{{ reportInfo.reviewer }}</el-descriptions-item>
            <el-descriptions-item label="审核时间">{{ reportInfo.reviewTime }}</el-descriptions-item>
            <el-descriptions-item label="审核意见" :span="2">
              {{ reportInfo.reviewComment }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

// 模拟数据
const reportInfo = ref({
  reportId: 'R20240320001',
  patientName: '张三',
  patientId: 'P001',
  checkDate: '2024-03-20',
  diagnosisTime: '2024-03-20 14:30:00',
  doctor: '李医生',
  imageUrl: 'https://example.com/fundus-image.jpg',
  diagnosisResult: {
    title: '检测到异常',
    type: 'warning',
    description: '发现2处微血管瘤，建议进一步检查'
  },
  lesions: [
    {
      type: '微血管瘤',
      location: '左眼上方',
      severity: 'high',
      description: '直径约0.5mm，边界清晰'
    },
    {
      type: '微血管瘤',
      location: '右眼下方',
      severity: 'medium',
      description: '直径约0.3mm，边界模糊'
    }
  ],
  suggestion: '建议患者定期复查，控制血糖水平，保持健康的生活方式。',
  status: '已审核',
  reviewer: '张医生',
  reviewTime: '2024-03-20 15:30:00',
  reviewComment: '诊断结果准确，建议合理。'
})

const getStatusType = (status) => {
  const statusMap = {
    '待审核': 'warning',
    '已审核': 'success',
    '已退回': 'danger'
  }
  return statusMap[status] || 'info'
}

const handleBack = () => {
  router.back()
}

const handlePrint = () => {
  ElMessage.success('正在生成打印文件...')
}

onMounted(() => {
  // 根据路由参数获取报告详情
  const reportId = route.params.id
  console.log('Loading report:', reportId)
})
</script>

<style scoped>
.report-detail {
  padding: 20px;
}

.report-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left .title {
  font-size: 18px;
  font-weight: bold;
}

.section {
  margin-bottom: 30px;
}

.section h3 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #303133;
}

.image-container {
  position: relative;
  text-align: center;
}

.fundus-image {
  max-width: 100%;
  max-height: 500px;
  border-radius: 4px;
}

.image-markers {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.suggestion-content {
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  line-height: 1.6;
  color: #606266;
}
</style> 