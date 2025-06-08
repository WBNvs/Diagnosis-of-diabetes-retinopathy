<template>
  <div class="dashboard-view">
    <el-row :gutter="20" class="overview-row">
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-title">今日诊断</div>
          <div class="overview-value">{{ stats.todayDiagnosis }}</div>
          <el-tag type="success" size="small">实时</el-tag>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-title">待审核报告</div>
          <div class="overview-value">{{ stats.pendingReports }}</div>
          <el-tag type="warning" size="small">待审核</el-tag>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-title">异常病例</div>
          <div class="overview-value">{{ stats.abnormalCases }}</div>
          <el-tag type="danger" size="small">需关注</el-tag>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="overview-title">本月诊断</div>
          <div class="overview-value">{{ stats.monthDiagnosis }}</div>
          <el-tag type="info" size="small">月度</el-tag>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="main-row">
      <el-col :span="16">
        <el-card class="main-card">
          <template #header>
            <span>待处理病例</span>
            <el-link class="view-all" type="primary" @click="goToPending">查看全部</el-link>
          </template>
          <el-table :data="pendingCases" style="width: 100%">
            <el-table-column prop="patientName" label="患者姓名" width="120" />
            <el-table-column prop="caseId" label="病例ID" width="120" />
            <el-table-column prop="diagnosisTime" label="诊断时间" width="180" />
            <el-table-column prop="lesionCount" label="病灶数量" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-link type="primary" @click="viewReport(row)">查看</el-link>
                <el-link type="success" @click="processCase(row)">处理</el-link>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="main-card">
          <template #header>
            <span>最近诊断记录</span>
            <el-link class="view-all" type="primary" @click="goToHistory">查看全部</el-link>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(item, idx) in recentRecords"
              :key="idx"
              :timestamp="item.time"
              :type="item.type"
            >
              {{ item.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 顶部统计数据
const stats = ref({
  todayDiagnosis: 0,
  pendingReports: 0,
  abnormalCases: 0,
  monthDiagnosis: 0
})

// 待处理病例（只与AI诊断和报告审核相关）
const pendingCases = ref([
  
])

// 最近诊断记录
const recentRecords = ref([
  
])

// 状态标签类型
const getStatusType = (status) => {
  switch (status) {
    case '待审核':
      return 'warning'
    case '待确认':
      return 'info'
    case '待处理':
      return 'danger'
    default:
      return 'default'
  }
}

// 跳转操作
const viewReport = (row) => {
  router.push(`/dashboard/doctor/reports/${row.caseId}`)
}
const processCase = (row) => {
  router.push(`/dashboard/doctor/reports/${row.caseId}`)
}
const goToPending = () => {
  router.push('/dashboard/doctor/reports/pending')
}
const goToHistory = () => {
  router.push('/dashboard/doctor/diagnosis/history')
}
</script>

<style scoped>
.dashboard-view {
  padding: 20px;
  background: #f7fafc;
}

.overview-row {
  margin-bottom: 20px;
}

.overview-card {
  text-align: center;
  min-height: 110px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.overview-title {
  font-size: 16px;
  color: #666;
  margin-bottom: 8px;
}

.overview-value {
  font-size: 32px;
  font-weight: bold;
  color: #222;
  margin-bottom: 8px;
}

.main-row {
  margin-bottom: 20px;
}

.main-card {
  min-height: 350px;
}

.view-all {
  float: right;
  font-size: 14px;
}
</style> 