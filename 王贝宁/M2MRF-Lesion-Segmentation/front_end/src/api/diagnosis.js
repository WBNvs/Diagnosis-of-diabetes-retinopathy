import axios from 'axios'

// 数据库API实例
export const dbApi = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/* ========== Auth ========== */
// 登录
export const login = async (username, password, role) => {
  const response = await dbApi.post('/auth/login', { username, password, role })
  return response.data
}

/* ========== Doctor ========== */
// 医生统计
export const getDoctorStats = async (doctor_id) => {
  const response = await dbApi.get('/doctor/stats', { params: { doctor_id } })
  return response.data
}

// 医生待处理病例
export const getDoctorPendingCases = async (doctor_id) => {
  const response = await dbApi.get('/doctor/pending_cases', { params: { doctor_id } })
  return response.data
}

// 医生今日已确认诊断
export const getDoctorRecentDiagnoses = async (doctor_id) => {
  const response = await dbApi.get('/doctor/recent', { params: { doctor_id } })
  return response.data
}

// 医生诊断历史
export const getDoctorDiagnosisHistory = async (doctor_id, confirmed = null) => {
  const params = { doctor_id }
  if (confirmed !== null) params.confirmed = confirmed
  const response = await dbApi.get('/doctor/history', { params })
  return response.data
}

/* ========== Patient ========== */
// 患者报告
export const getPatientReports = async (patient_id) => {
  const response = await dbApi.get('/patient/reports', { params: { patient_id } })
  return response.data
}

// 创建axios实例
const aiapi = axios.create({
  baseURL: 'http://localhost:6006', // 后端API的基础URL
  timeout: 30000, // 超时时间设置为30秒，因为图片处理可能需要较长时间
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

export const uploadImageForDiagnosis = async (imageFile) => {
  try {
    const formData = new FormData()
    formData.append('image', imageFile)
    
    const response = await aiapi.post('/diagnosis/analyze', formData)
    return response.data
  } catch (error) {
    console.error('诊断请求失败:', error)
    throw error
  }
}

// 上传图片进行诊断
export const uploadImageForSegmentation = async (imageFile) => {
  try {
    const formData = new FormData()
    formData.append('image', imageFile)
    
    const response = await aiapi.post('/segment', formData, {
      responseType: 'blob' // 关键
    })
    return response.data
  } catch (error) {
    console.error('诊断请求失败:', error)
    throw error
  }
}

// 获取诊断历史
export const getDiagnosisHistory = async (params) => {
  try {
    const response = await aiapi.get('/diagnosis/history', { params })
    return response.data
  } catch (error) {
    console.error('获取诊断历史失败:', error)
    throw error
  }
}

// 获取诊断报告详情
export const getDiagnosisReport = async (reportId) => {
  try {
    const response = await aiapi.get(`/diagnosis/reports/${reportId}`)
    return response.data
  } catch (error) {
    console.error('获取诊断报告失败:', error)
    throw error
  }
}

// 提交诊断报告
export const submitDiagnosis = async (diagnosisData) => {
  try {
    const response = await dbApi.post('/auth/submit_diagnosis', diagnosisData)
    return response.data
  } catch (error) {
    console.error('提交诊断报告失败:', error)
    throw error
  }
}

// 获取诊断报告详情
export const getDiagnosisDetail = async (diagnosisId) => {
  try {
    const response = await dbApi.get(`/auth/diagnosis/${diagnosisId}`)
    return response.data
  } catch (error) {
    console.error('获取诊断报告详情失败:', error)
    throw error
  }
}

// 修改诊断报告审核状态
export const confirmDiagnosis = async (diagnosisId) => {
  try {
    const response = await dbApi.put(`/auth/diagnosis/${diagnosisId}/confirm`)
    return response.data
  } catch (error) {
    console.error('修改审核状态失败:', error)
    throw error
  }
}

// 删除诊断报告
export const deleteDiagnosis = async (diagnosisId) => {
  try {
    const response = await dbApi.delete(`/auth/diagnosis/${diagnosisId}`)
    return response.data
  } catch (error) {
    console.error('退回诊断报告失败:', error)
    throw error
  }
} 