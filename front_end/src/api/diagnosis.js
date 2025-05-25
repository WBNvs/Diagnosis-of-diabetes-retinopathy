import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api', // 后端API的基础URL
  timeout: 30000, // 超时时间设置为30秒，因为图片处理可能需要较长时间
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

// 上传图片进行诊断
export const uploadImageForDiagnosis = async (imageFile) => {
  try {
    const formData = new FormData()
    formData.append('image', imageFile)
    
    const response = await api.post('/diagnosis/analyze', formData)
    return response.data
  } catch (error) {
    console.error('诊断请求失败:', error)
    throw error
  }
}

// 获取诊断历史
export const getDiagnosisHistory = async (params) => {
  try {
    const response = await api.get('/diagnosis/history', { params })
    return response.data
  } catch (error) {
    console.error('获取诊断历史失败:', error)
    throw error
  }
}

// 获取诊断报告详情
export const getDiagnosisReport = async (reportId) => {
  try {
    const response = await api.get(`/diagnosis/reports/${reportId}`)
    return response.data
  } catch (error) {
    console.error('获取诊断报告失败:', error)
    throw error
  }
} 