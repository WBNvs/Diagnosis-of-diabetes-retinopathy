<template>
  <div class="pending-reports">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">待审核报告</span>
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
            <el-tag type="warning">待审核</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button type="primary" link @click="handleReview(scope.row)">审核</el-button>
            <el-button type="warning" link @click="handleReject(scope.row)">退回</el-button>
            <el-button type="info" link @click="handleView(scope.row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 退回原因对话框 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="退回原因"
      width="30%"
    >
      <el-form :model="rejectForm">
        <el-form-item label="退回原因" :label-width="80">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入退回原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="rejectDialogVisible = false">取消</el-button>
          <el-button type="warning" @click="confirmReject">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDoctorDiagnosisHistory, confirmDiagnosis, deleteDiagnosis } from '@/api/diagnosis'

const router = useRouter()
const doctor_id = 1
const reportsList = ref([])
const loading = ref(false)
const rejectDialogVisible = ref(false)
const selectedReport = ref(null)

const rejectForm = ref({
  reason: ''
})

const handleReview = async (row) => {
  try {
    await confirmDiagnosis(row.diagnosis_id)
    ElMessage.success('审核成功')
    // 刷新列表
    await fetchPendingReports()
  } catch (error) {
    ElMessage.error('审核失败')
    console.error('审核失败:', error)
  }
}

const handleReject = (row) => {
  selectedReport.value = row
  rejectDialogVisible.value = true
}

const handleView = (row) => {
  router.push(`/dashboard/doctor/reports/${row.diagnosis_id}`)
}

const confirmReject = async () => {
  if (!rejectForm.value.reason) {
    ElMessage.warning('请输入退回原因')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      '确定要退回该报告吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteDiagnosis(selectedReport.value.diagnosis_id)
    ElMessage.success('报告已退回')
    // 刷新列表
    await fetchPendingReports()
    rejectDialogVisible.value = false
    rejectForm.value.reason = ''
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('退回失败')
      console.error('退回失败:', error)
    }
  }
}

const fetchPendingReports = async () => {
  if (!doctor_id) return
  loading.value = true
  try {
    // 只获取待审核
    reportsList.value = await getDoctorDiagnosisHistory(doctor_id, 'false')
  } catch (e) {
    console.error('获取待审核报告失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPendingReports()
})
</script>

<style scoped>
.pending-reports {
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 