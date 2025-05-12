<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>糖尿病视网膜病变 AI 诊断系统</h2>
      </template>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="密码">
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="role">
          <el-radio-group v-model="loginForm.role">
            <el-radio label="doctor">医生</el-radio>
            <el-radio label="patient">患者</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" style="width: 100%">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loginFormRef = ref(null)

const loginForm = reactive({
  username: '',
  password: '',
  role: 'doctor'
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const handleLogin = () => {
  loginFormRef.value.validate((valid) => {
    if (valid) {
      // 模拟登录请求
      const response = {
        token: 'demo-token',
        role: loginForm.role
      }
      
      // 存储登录信息
      localStorage.setItem('token', response.token)
      localStorage.setItem('role', response.role)
      
      console.log('登录信息已存储:', {
        token: localStorage.getItem('token'),
        role: localStorage.getItem('role')
      })
      
      ElMessage.success('登录成功')
      // 修改跳转逻辑
      if (response.role === 'doctor') {
        console.log('准备跳转到医生仪表盘')
        router.push('/dashboard/doctor').catch(err => {
          console.error('路由跳转失败:', err)
        })
      } else {
        console.log('准备跳转到患者仪表盘')
        router.push('/dashboard/patient').catch(err => {
          console.error('路由跳转失败:', err)
        })
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
}

.login-card :deep(.el-card__header) {
  text-align: center;
}

h2 {
  margin: 0;
  color: #409EFF;
  font-size: 24px;
}

.el-radio-group {
  width: 100%;
  display: flex;
  justify-content: space-around;
}
</style> 