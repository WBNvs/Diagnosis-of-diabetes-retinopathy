<template>
  <div class="reports-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">诊断报告列表</span>
          </div>
          <div class="header-right">
            <el-input
              v-model="searchQuery"
              placeholder="搜索患者姓名/ID"
              class="search-input"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><search /></el-icon>
              </template>
            </el-input>
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="handleSearch">
              <el-option label="全部" value="" />
              <el-option label="待审核" value="pending" />
              <el-option label="已审核" value="reviewed" />
              <el-option label="已退回" value="rejected" />
            </el-select>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleSearch"
            />
          </div>
        </div>
      </template>

      <el-table
        :data="filteredReports"
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="reportId" label="报告编号" width="120" />
        <el-table-column prop="patientName" label="患者姓名" width="120" />
        <el-table-column prop="patientId" label="患者ID" width="120" />
        <el-table-column prop="checkDate" label="检查日期" width="120" />
        <el-table-column prop="diagnosisTime" label="诊断时间" width="180" />
        <el-table-column prop="lesionCount" label="病灶数量" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.lesionCount > 0 ? 'danger' : 'success'">
              {{ scope.row.lesionCount }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="doctor" label="诊断医生" width="120" />
        <el-table-column prop="reviewer" label="审核医生" width="120" />
        <el-table-column label="操作" fixed="right" width="250">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
            <el-button 
              v-if="scope.row.status === '待审核'"
              type="success" 
              link 
              @click="handleReview(scope.row)"
            >审核</el-button>
            <el-button 
              v-if="scope.row.status === '待审核'"
              type="warning" 
              link 
              @click="handleReject(scope.row)"
            >退回</el-button>
            <el-button type="info" link @click="handlePrint(scope.row)">打印</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)
const rejectDialogVisible = ref(false)
const selectedReport = ref(null)

const rejectForm = ref({
  reason: ''
})

// 模拟数据
const reportsList = ref([
  {
    reportId: 'R20240320001',
    patientName: '张三',
    patientId: 'P001',
    checkDate: '2024-03-20',
    diagnosisTime: '2024-03-20 14:30:00',
    lesionCount: 2,
    status: '待审核',
    doctor: '李医生',
    reviewer: '-'
  },
  {
    reportId: 'R20240320002',
    patientName: '李四',
    patientId: 'P002',
    checkDate: '2024-03-20',
    diagnosisTime: '2024-03-20 13:45:00',
    lesionCount: 0,
    status: '已审核',
    doctor: '王医生',
    reviewer: '张医生'
  },
  {
    reportId: 'R20240319001',
    patientName: '王五',
    patientId: 'P003',
    checkDate: '2024-03-19',
    diagnosisTime: '2024-03-19 11:20:00',
    lesionCount: 3,
    status: '已退回',
    doctor: '张医生',
    reviewer: '李医生'
  }
])

const filteredReports = computed(() => {
  return reportsList.value.filter(item => {
    const matchQuery = !searchQuery.value || 
      item.patientName.includes(searchQuery.value) ||
      item.patientId.includes(searchQuery.value)
    
    const matchStatus = !statusFilter.value || 
      getStatusValue(item.status) === statusFilter.value
    
    const matchDate = !dateRange.value.length || 
      (item.checkDate >= dateRange.value[0] && 
       item.checkDate <= dateRange.value[1])
    
    return matchQuery && matchStatus && matchDate
  })
})

const getStatusType = (status) => {
  const statusMap = {
    '待审核': 'warning',
    '已审核': 'success',
    '已退回': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusValue = (status) => {
  const statusMap = {
    '待审核': 'pending',
    '已审核': 'reviewed',
    '已退回': 'rejected'
  }
  return statusMap[status] || ''
}

const handleView = (row) => {
  router.push(`/dashboard/doctor/reports/${row.reportId}`)
}

const handleReview = (row) => {
  router.push(`/dashboard/doctor/reports/review/${row.reportId}`)
}

const handleReject = (row) => {
  selectedReport.value = row
  rejectDialogVisible.value = true
}

const confirmReject = () => {
  if (!rejectForm.value.reason) {
    ElMessage.warning('请输入退回原因')
    return
  }
  
  // 模拟退回操作
  const index = reportsList.value.findIndex(item => item.reportId === selectedReport.value.reportId)
  if (index !== -1) {
    reportsList.value[index].status = '已退回'
    ElMessage.success('报告已退回')
  }
  
  rejectDialogVisible.value = false
  rejectForm.value.reason = ''
}

const handlePrint = (row) => {
  // 实现打印功能
  ElMessage.success('正在生成打印文件...')
}

const handleSearch = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 500)
}

const handleSizeChange = (val) => {
  pageSize.value = val
  handleSearch()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  handleSearch()
}
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

.header-right {
  display: flex;
  gap: 16px;
}

.search-input {
  width: 200px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 