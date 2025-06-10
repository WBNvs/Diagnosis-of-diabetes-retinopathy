<template>
  <div class="settings-view">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>修改密码</span>
        </div>
      </template>
      
      <div class="form-container">
        <div class="input-group">
          <span class="label">当前密码：</span>
          <input 
            v-model="oldPassword" 
            type="text" 
            placeholder="请输入当前密码"
            class="input-field"
          />
        </div>
        
        <div class="input-group">
          <span class="label">新密码：</span>
          <input 
            v-model="newPassword" 
            type="text" 
            placeholder="请输入新密码"
            class="input-field"
          />
        </div>
        
        <div class="input-group">
          <span class="label">确认密码：</span>
          <input 
            v-model="confirmPassword" 
            type="text" 
            placeholder="请再次输入新密码"
            class="input-field"
          />
        </div>
        
        <div class="button-group">
          <el-button type="primary" @click="handleSubmit">确认修改</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const handleSubmit = () => {
  if (!oldPassword.value || !newPassword.value || !confirmPassword.value) {
    ElMessage.warning('请填写所有密码字段')
    return
  }
  
  if (newPassword.value !== confirmPassword.value) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  ElMessage.success('密码修改成功')
}
</script>

<style scoped>
.settings-view {
  padding: 20px;
}

.settings-card {
  max-width: 500px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.form-container {
  padding: 20px 0;
}

.input-group {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.label {
  width: 100px;
  text-align: right;
  margin-right: 10px;
}

.input-field {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
  color: #606266;
  transition: border-color 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: #409eff;
}

.button-group {
  margin-top: 30px;
  text-align: center;
}
</style>