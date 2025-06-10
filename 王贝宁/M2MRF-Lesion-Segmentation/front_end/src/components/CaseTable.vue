<template>
  <el-card class="case-table">
    <template #header>
      <div class="card-header">
        <span>{{ isPatient ? '我的报告' : '历史病例' }}</span>
        <el-button v-if="!isPatient" type="primary" size="small">查看全部</el-button>
      </div>
    </template>
    <el-table :data="tableData" style="width: 100%" height="500" v-loading="loading">
      <el-table-column prop="report_date" label="诊断日期" width="120" />
      <el-table-column prop="doctor_name" label="诊断医生" width="120" />
      <el-table-column label="眼底图像" width="120">
        <template #default="scope">
          <el-image 
            :src="getImageUrl(scope.row.report_image)" 
            :preview-src-list="[getImageUrl(scope.row.report_image)]"
            fit="cover"
            style="width: 80px; height: 80px"
          />
        </template>
      </el-table-column>
      <el-table-column prop="lesion_count" label="病灶数量" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.lesion_count > 0 ? 'danger' : 'success'">
            {{ scope.row.lesion_count }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="审核状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_confirmed ? 'success' : 'warning'">
            {{ scope.row.is_confirmed ? '已审核' : '待审核' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPatientReports } from '@/api/diagnosis'

const router = useRouter()
const props = defineProps({
  isPatient: {
    type: Boolean,
    default: false
  }
})

const tableData = ref([])
const loading = ref(false)

// 获取图片URL
const getImageUrl = (path) => {
  if (!path) return ''
  // 如果path已经包含完整路径，直接返回
  if (path.startsWith('http')) return path
  // 将反斜杠转换为正斜杠，并确保路径格式正确
  const normalizedPath = path.replace(/\\/g, '/')
  return `http://localhost:5000/${normalizedPath}`
}

// 获取报告列表
const fetchReports = async () => {
  try {
    loading.value = true
    const token = JSON.parse(localStorage.getItem('token'))
    if (!token) {
      ElMessage.error('未登录')
      return
    }

    const data = await getPatientReports(token.patient_id)
    tableData.value = data.map(item => ({
      ...item,
      report_date: item.report_date.split('T')[0] // 格式化日期为 YYYY-MM-DD
    }))
  } catch (error) {
    ElMessage.error('获取报告列表失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 查看报告详情
const handleView = (row) => {
  if (!row.diagnosis_id) {
    ElMessage.error('报告ID不存在')
    return
  }
  router.push(`/dashboard/patient/reports/${row.diagnosis_id}`)
}

onMounted(() => {
  if (props.isPatient) {
    fetchReports()
  }
})
</script>

<style scoped>
.case-table {
  height: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-image {
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}
</style> 