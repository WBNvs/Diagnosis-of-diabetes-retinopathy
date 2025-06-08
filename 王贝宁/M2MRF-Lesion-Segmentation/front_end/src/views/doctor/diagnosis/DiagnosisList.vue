<template>
  <div class="diagnosis-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">诊断记录列表</span>
            <el-button type="primary" @click="handleNewDiagnosis">新建诊断</el-button>
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
        :data="filteredDiagnosisList"
        style="width: 100%"
        v-loading="loading"
      >
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
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">查看</el-button>
            <el-button type="success" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
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

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="30%"
    >
      <span>确定要删除这条诊断记录吗？此操作不可恢复。</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const searchQuery = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)
const deleteDialogVisible = ref(false)
const selectedRecord = ref(null)

// 模拟数据
const diagnosisList = ref([
  {
    patientName: '张三',
    patientId: 'P001',
    checkDate: '2024-03-20',
    diagnosisTime: '2024-03-20 14:30:00',
    lesionCount: 2,
    status: '已完成',
    doctor: '李医生'
  },
  {
    patientName: '李四',
    patientId: 'P002',
    checkDate: '2024-03-20',
    diagnosisTime: '2024-03-20 13:45:00',
    lesionCount: 0,
    status: '待审核',
    doctor: '王医生'
  },
  {
    patientName: '王五',
    patientId: 'P003',
    checkDate: '2024-03-19',
    diagnosisTime: '2024-03-19 11:20:00',
    lesionCount: 3,
    status: '待处理',
    doctor: '张医生'
  }
])

const filteredDiagnosisList = computed(() => {
  return diagnosisList.value.filter(item => {
    const matchQuery = !searchQuery.value || 
      item.patientName.includes(searchQuery.value) ||
      item.patientId.includes(searchQuery.value)
    
    const matchDate = !dateRange.value.length || 
      (item.checkDate >= dateRange.value[0] && 
       item.checkDate <= dateRange.value[1])
    
    return matchQuery && matchDate
  })
})

const getStatusType = (status) => {
  const statusMap = {
    '已完成': 'success',
    '待审核': 'warning',
    '待处理': 'danger'
  }
  return statusMap[status] || 'info'
}

const handleNewDiagnosis = () => {
  router.push('/dashboard/doctor/diagnosis/new')
}

const handleView = (row) => {
  router.push(`/dashboard/doctor/reports/${row.patientId}`)
}

const handleEdit = (row) => {
  router.push(`/dashboard/doctor/diagnosis/edit/${row.patientId}`)
}

const handleDelete = (row) => {
  selectedRecord.value = row
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  // 模拟删除操作
  const index = diagnosisList.value.findIndex(item => item.patientId === selectedRecord.value.patientId)
  if (index !== -1) {
    diagnosisList.value.splice(index, 1)
    ElMessage.success('删除成功')
  }
  deleteDialogVisible.value = false
}

const handleSearch = () => {
  // 实现搜索逻辑
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
.diagnosis-list {
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