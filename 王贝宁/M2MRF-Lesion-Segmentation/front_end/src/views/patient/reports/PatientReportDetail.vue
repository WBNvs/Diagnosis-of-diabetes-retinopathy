<template>
  <div class="report-detail">
    <el-card class="report-card">
      <template #header>
        <div class="card-header">
          <span>报告详情</span>
          <el-button type="primary" link @click="goBack">返回</el-button>
        </div>
      </template>

      <div class="report-content" v-loading="loading">
        <div class="image-section">
          <div class="image-container">
            <el-image
              :src="getImageUrl(reportData.report_image)"
              fit="contain"
              :preview-src-list="[getImageUrl(reportData.report_image)]"
            />
          </div>
          <div class="image-info">
            <p><strong>报告编号：</strong>{{ reportData.formatted_report_id }}</p>
            <p><strong>诊断日期：</strong>{{ reportData.report_date }}</p>
            <p><strong>诊断医生：</strong>{{ reportData.doctor_name }}</p>
            <p><strong>审核状态：</strong>
              <el-tag :type="reportData.is_confirmed ? 'success' : 'warning'">
                {{ reportData.is_confirmed ? '已审核' : '待审核' }}
              </el-tag>
            </p>
            <p><strong>病灶数量：</strong>
              <el-tag :type="reportData.lesion_count > 0 ? 'danger' : 'success'">
                {{ reportData.lesion_count }}
              </el-tag>
            </p>
          </div>
        </div>

        <div class="health-advice">
          <h3>AI健康建议</h3>
          <el-card class="advice-card">
            <div class="advice-content">
              <div class="advice-section">
                <h4>1. 立即就诊：</h4>
                <p>建议患者尽快前往眼科或内分泌科就诊，接受以下检查：</p>
                <ul>
                  <li>OCT（光学相干断层扫描）</li>
                  <li>眼底荧光造影（FFA）</li>
                  <li>血糖和HbA1c水平检测</li>
                </ul>
              </div>
              
              <div class="advice-section">
                <h4>2. 血糖控制：</h4>
                <p>若已知有糖尿病，应强化血糖、血压和血脂的控制，延缓病变进展。</p>
              </div>
              
              <div class="advice-section">
                <h4>3. 定期复查：</h4>
                <p>若已确诊糖网病，应每3~6个月做一次眼底检查。</p>
              </div>
              
              <div class="advice-section">
                <h4>4. 激光或注药治疗（如有必要）：</h4>
                <p>若发展为黄斑水肿或出血严重，可能需接受激光治疗或玻璃体腔注射抗VEGF药物。</p>
              </div>
            </div>
          </el-card>
        </div>

        <div class="lesion-section" v-if="reportData.lesion_count > 0">
          <h3>病灶信息</h3>
          <el-table :data="lesions" style="width: 100%">
            <el-table-column prop="lesion_type" label="病灶类型" width="120" />
            <el-table-column prop="confidence" label="置信度" width="120">
              <template #default="scope">
                {{ (scope.row.confidence * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="location" label="位置" />
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPatientReports } from '@/api/diagnosis'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const reportData = ref({})
const lesions = ref([])

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const normalizedPath = path.replace(/\\/g, '/')
  return `http://localhost:5000/${normalizedPath}`
}

// 获取报告详情
const fetchReportDetail = async () => {
  try {
    loading.value = true
    const token = JSON.parse(localStorage.getItem('token'))
    if (!token) {
      ElMessage.error('未登录')
      return
    }

    const data = await getPatientReports(token.patient_id)
    const report = data.find(item => item.diagnosis_id === parseInt(route.params.id))
    
    if (report) {
      // 格式化报告编号
      const date = report.report_date.split('T')[0].replace(/-/g, '')
      const reportId = report.diagnosis_id.toString().padStart(3, '0')
      const formattedReportId = `R${date}${reportId}`

      reportData.value = {
        ...report,
        report_date: report.report_date.split('T')[0],
        formatted_report_id: formattedReportId
      }
      // 如果有病灶数据，添加到lesions数组
      if (report.lesions) {
        lesions.value = report.lesions
      }
    } else {
      ElMessage.error('未找到报告')
      router.push('/dashboard/patient')
    }
  } catch (error) {
    ElMessage.error('获取报告详情失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/dashboard/patient')
}

onMounted(() => {
  fetchReportDetail()
})
</script>

<style scoped>
.report-detail {
  padding: 20px;
  height: 100%;
}

.report-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-content {
  height: calc(100% - 60px);
  overflow-y: auto;
}

.image-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.image-container {
  flex: 1;
  max-width: 60%;
}

.image-container .el-image {
  width: 100%;
  height: 400px;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
}

.image-info {
  flex: 1;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.image-info p {
  margin: 10px 0;
  font-size: 16px;
}

.health-advice {
  margin: 20px 0;
}

.health-advice h3 {
  margin-bottom: 15px;
  color: #303133;
}

.advice-card {
  background-color: #f5f7fa;
  padding: 20px;
}

.advice-card p {
  color: #909399;
  font-style: italic;
}

.lesion-section {
  margin-top: 20px;
}

.lesion-section h3 {
  margin-bottom: 15px;
  color: #303133;
}

.no-lesion {
  margin-top: 40px;
}

.advice-content {
  padding: 10px;
}

.advice-section {
  margin-bottom: 20px;
}

.advice-section:last-child {
  margin-bottom: 0;
}

.advice-section h4 {
  color: #409EFF;
  margin-bottom: 10px;
  font-size: 16px;
}

.advice-section p {
  margin: 8px 0;
  line-height: 1.6;
}

.advice-section ul {
  margin: 8px 0;
  padding-left: 20px;
}

.advice-section li {
  margin: 5px 0;
  line-height: 1.6;
}
</style> 