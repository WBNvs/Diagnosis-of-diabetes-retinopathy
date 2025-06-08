<template>
  <div class="diagnosis-history">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>诊断历史</span>
          <div class="header-operations">
            <el-input
              v-model="searchQuery"
              placeholder="搜索图片ID或诊断结果"
              style="width: 200px; margin-right: 16px"
            />
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 300px"
            />
          </div>
        </div>
      </template>

      <el-table :data="filteredDiagnosisList" style="width: 100%">
        <el-table-column prop="id" label="图片ID" width="120" />
        <el-table-column label="眼底图片" width="180">
          <template #default="{ row }">
            <el-image
              :src="row.imageUrl"
              :preview-src-list="[row.imageUrl]"
              fit="cover"
              style="width: 100px; height: 100px"
            />
          </template>
        </el-table-column>
        <el-table-column prop="diagnosisTime" label="诊断时间" width="180" />
        <el-table-column prop="lesionCount" label="病灶数量" width="100" />
        <el-table-column prop="aiDiagnosis" label="AI诊断结果" width="150">
          <template #default="{ row }">
            <el-tag :type="row.aiDiagnosis === '正常' ? 'success' : 'warning'">
              {{ row.aiDiagnosis }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="doctorReview" label="医生审核" width="150">
          <template #default="{ row }">
            <el-tag :type="getReviewStatusType(row.doctorReview)">
              {{ row.doctorReview }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reviewTime" label="审核时间" width="180" />
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              @click="viewReport(row)"
            >
              查看报告
            </el-button>
            <el-button
              v-if="row.doctorReview === '待审核'"
              type="primary"
              link
              @click="reviewReport(row)"
            >
              审核
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 搜索和筛选
const searchQuery = ref('')
const dateRange = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)

// 模拟诊断历史数据
const diagnosisList = ref([
  {
    id: 'IMG001',
    imageUrl: 'https://example.com/image1.jpg',
    diagnosisTime: '2025-05-28 10:55:01',
    lesionCount: 4,
    aiDiagnosis: '严重病变',
    doctorReview: '已确认',
    reviewTime: '025-05-28 10:55:01'
  }
])

// 根据搜索条件过滤数据
const filteredDiagnosisList = computed(() => {
  return diagnosisList.value.filter(item => {
    const matchesSearch = searchQuery.value === '' ||
      item.id.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      item.aiDiagnosis.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesDate = dateRange.value.length === 0 ||
      (new Date(item.diagnosisTime) >= dateRange.value[0] &&
       new Date(item.diagnosisTime) <= dateRange.value[1])
    
    return matchesSearch && matchesDate
  })
})

// 获取审核状态对应的标签类型
const getReviewStatusType = (status) => {
  switch (status) {
    case '已确认':
      return 'success'
    case '已修改':
      return 'warning'
    case '待审核':
      return 'info'
    default:
      return ''
  }
}

// 查看报告
const viewReport = (row) => {
  router.push(`/dashboard/doctor/reports/${row.id}`)
}

// 审核报告
const reviewReport = (row) => {
  router.push(`/dashboard/doctor/reports/${row.id}`)
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  // TODO: 重新加载数据
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  // TODO: 重新加载数据
}
</script>

<style scoped>
.diagnosis-history {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-operations {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-image) {
  border-radius: 4px;
  overflow: hidden;
}
</style> 