<template>
  <el-card class="case-table">
    <template #header>
      <div class="card-header">
        <span>{{ isPatient ? '我的报告' : '历史病例' }}</span>
        <el-button type="primary" size="small">查看全部</el-button>
      </div>
    </template>
    <el-table :data="tableData" style="width: 100%" height="500">
      <el-table-column prop="date" label="日期" width="100" />
      <el-table-column v-if="!isPatient" prop="patientName" label="患者姓名" width="100" />
      <el-table-column v-if="!isPatient" prop="patientId" label="患者ID" width="100" />
      <el-table-column prop="lesionCount" label="病灶数量" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.lesionCount > 0 ? 'danger' : 'success'">
            {{ scope.row.lesionCount }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default>
          <el-button type="primary" link>查看</el-button>
          <el-button type="success" link>下载报告</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
defineProps({
  isPatient: {
    type: Boolean,
    default: false
  }
})

const tableData = [
  {
    date: '2024-03-20',
    patientName: '张三',
    patientId: 'P001',
    lesionCount: 2
  },
  {
    date: '2024-03-19',
    patientName: '李四',
    patientId: 'P002',
    lesionCount: 0
  },
  {
    date: '2024-03-18',
    patientName: '王五',
    patientId: 'P003',
    lesionCount: 3
  },
  {
    date: '2024-03-17',
    patientName: '赵六',
    patientId: 'P004',
    lesionCount: 1
  },
  {
    date: '2024-03-16',
    patientName: '钱七',
    patientId: 'P005',
    lesionCount: 0
  }
]
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
</style> 