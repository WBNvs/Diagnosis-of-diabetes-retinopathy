<template>
  <div class="reports-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">已审核报告</span>
          </div>
        </div>
      </template>

      <el-table
        :data="reportsList"
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="diagnosis_id" label="报告编号" width="120" />
        <el-table-column prop="patient_name" label="患者姓名" width="120" />
        <el-table-column prop="diagnose_date" label="诊断时间" width="180" />
        <el-table-column prop="lesion_count" label="病灶数量" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.lesion_count > 0 ? 'danger' : 'success'">
              {{ scope.row.lesion_count }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confirmed" label="状态" width="100">
          <template #default="scope">
            <el-tag type="success">已审核</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
            <el-button type="info" link @click="handlePrint(scope.row)">打印</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDoctorDiagnosisHistory } from '@/api/diagnosis'

const router = useRouter()
const doctor_id = 1
const reportsList = ref([])
const loading = ref(false)

const handleView = (row) => {
  router.push(`/dashboard/doctor/reports/${row.diagnosis_id}`)
}

const handlePrint = (row) => {
  // 实现打印功能
  ElMessage.success('正在生成打印文件...')
}

const fetchReviewedReports = async () => {
  if (!doctor_id) return
  loading.value = true
  try {
    // 只获取已审核
    reportsList.value = await getDoctorDiagnosisHistory(doctor_id, 'true')
  } catch (e) {
    console.error('获取已审核报告失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchReviewedReports()
})
</script>

<style scoped>
.reports-list {
  padding: 20px;
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
</style> 