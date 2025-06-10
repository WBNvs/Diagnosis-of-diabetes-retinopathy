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
            <el-descriptions-item label="报告编号">{{ reportInfo.report_id }}</el-descriptions-item>
            <el-descriptions-item label="患者姓名">{{ reportInfo.patient_name }}</el-descriptions-item>
            <el-descriptions-item label="患者ID">{{ reportInfo.patient_id }}</el-descriptions-item>
            <el-descriptions-item label="检查日期">{{ reportInfo.check_date }}</el-descriptions-item>
            <el-descriptions-item label="诊断时间">{{ reportInfo.check_time }}</el-descriptions-item>
            <el-descriptions-item label="审核状态">
              <el-tag :type="getStatusType(reportInfo.status)">
                {{ reportInfo.status }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 眼底图像 -->
        <div class="section">
          <h3>眼底图像</h3>
          <div class="image-container">
            <img :src="getImageUrl(reportInfo.image_path)" class="fundus-image" />
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

        <!-- 审核信息 -->
        <div class="section" v-if="reportInfo.status === '已审核'">
          <h3>审核信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="审核医生ID">{{ reportInfo.doctor_id }}</el-descriptions-item>
            <el-descriptions-item label="审核医生">{{ reportInfo.doctor_name }}</el-descriptions-item>
            <el-descriptions-item label="健康建议" :span="2">
              {{ reportInfo.health_advice || '暂无健康建议' }}
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
import { getDiagnosisDetail } from '@/api/diagnosis'

const router = useRouter()
const route = useRoute()

// 报告信息
const reportInfo = ref({
  report_id: '',
  patient_name: '',
  patient_id: '',
  doctor_name: '',
  doctor_id: '',
  check_date: '',
  check_time: '',
  status: '',
  image_path: '',
  diagnosisResult: {
    title: '检测到异常',
    type: 'warning',
    description: '发现4种病灶，建议加急检查'
  },
  reviewerId: '',
  reviewerName: '',
  healthAdvice: ''
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

// 获取报告详情
const fetchReportDetail = async (diagnosisId) => {
  try {
    const data = await getDiagnosisDetail(diagnosisId)
    reportInfo.value = {
      ...data,
      diagnosisResult: {
        title: '检测到异常',
        type: 'warning',
        description: '发现4种病灶，建议加急检查'
      }
    }
  } catch (error) {
    ElMessage.error('获取报告详情失败')
    console.error('获取报告详情失败:', error)
  }
}

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return ''
  // 如果path已经包含完整路径，直接返回
  if (path.startsWith('http')) return path
  // 将反斜杠转换为正斜杠，并确保路径格式正确
  const normalizedPath = path.replace(/\\/g, '/')
  return `http://localhost:5000/${normalizedPath}`
}

onMounted(() => {
  // 根据路由参数获取报告详情
  const diagnosisId = route.params.id
  if (diagnosisId) {
    fetchReportDetail(diagnosisId)
  }
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