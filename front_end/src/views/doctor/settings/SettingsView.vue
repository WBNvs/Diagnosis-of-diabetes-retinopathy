<template>
  <div class="settings-view">
    <el-row :gutter="20">
      <!-- 个人信息设置 -->
      <el-col :span="12">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
            </div>
          </template>
          <el-form
            ref="profileForm"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
          >
            <el-form-item label="头像">
              <el-upload
                class="avatar-uploader"
                action="#"
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
              >
                <img v-if="profileForm.avatar" :src="profileForm.avatar" class="avatar" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>
            <el-form-item label="姓名" prop="name">
              <el-input v-model="profileForm.name" />
            </el-form-item>
            <el-form-item label="工号" prop="employeeId">
              <el-input v-model="profileForm.employeeId" disabled />
            </el-form-item>
            <el-form-item label="职称" prop="title">
              <el-input v-model="profileForm.title" />
            </el-form-item>
            <el-form-item label="科室" prop="department">
              <el-input v-model="profileForm.department" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleProfileSubmit">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 系统偏好设置 -->
      <el-col :span="12">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span>系统偏好</span>
            </div>
          </template>
          <el-form
            ref="preferenceForm"
            :model="preferenceForm"
            label-width="120px"
          >
            <el-form-item label="主题色">
              <el-color-picker v-model="preferenceForm.theme" />
            </el-form-item>
            <el-form-item label="表格密度">
              <el-radio-group v-model="preferenceForm.tableSize">
                <el-radio label="large">宽松</el-radio>
                <el-radio label="default">默认</el-radio>
                <el-radio label="small">紧凑</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="诊断报告模板">
              <el-select v-model="preferenceForm.reportTemplate" placeholder="请选择">
                <el-option label="标准模板" value="standard" />
                <el-option label="详细模板" value="detailed" />
                <el-option label="简洁模板" value="simple" />
              </el-select>
            </el-form-item>
            <el-form-item label="自动保存">
              <el-switch v-model="preferenceForm.autoSave" />
            </el-form-item>
            <el-form-item label="保存间隔">
              <el-input-number
                v-model="preferenceForm.saveInterval"
                :min="1"
                :max="30"
                :disabled="!preferenceForm.autoSave"
              />
              <span class="unit">分钟</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handlePreferenceSubmit">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 修改密码 -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span>修改密码</span>
            </div>
          </template>
          <el-form
            ref="passwordForm"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input
                v-model="passwordForm.currentPassword"
                type="password"
                show-password
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handlePasswordSubmit">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 个人信息表单
const profileForm = ref({
  avatar: '',
  name: '张医生',
  employeeId: 'D20240320001',
  title: '主治医师',
  department: '眼科',
  email: 'doctor@example.com',
  phone: '13800138000'
})

const profileRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入职称', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请输入科室', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

// 系统偏好表单
const preferenceForm = ref({
  theme: '#409EFF',
  tableSize: 'default',
  reportTemplate: 'standard',
  autoSave: true,
  saveInterval: 5
})

// 修改密码表单
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else {
    if (passwordForm.value.confirmPassword !== '') {
      if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
        callback(new Error('两次输入密码不一致'))
      }
    }
    callback()
  }
}

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
}

// 头像上传
const beforeAvatarUpload = (file) => {
  const isJPG = file.type === 'image/jpeg'
  const isPNG = file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG && !isPNG) {
    ElMessage.error('上传头像图片只能是 JPG 或 PNG 格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
    return false
  }
  
  // 模拟上传
  const reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onload = () => {
    profileForm.value.avatar = reader.result
  }
  return false
}

// 提交处理
const handleProfileSubmit = () => {
  ElMessage.success('个人信息修改成功')
}

const handlePreferenceSubmit = () => {
  ElMessage.success('系统偏好设置已保存')
}

const handlePasswordSubmit = () => {
  ElMessage.success('密码修改成功')
}
</script>

<style scoped>
.settings-view {
  padding: 20px;
}

.settings-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-uploader {
  text-align: center;
}

.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
}

.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  text-align: center;
  border-radius: 50%;
  line-height: 100px;
}

.unit {
  margin-left: 10px;
  color: #909399;
}
</style> 