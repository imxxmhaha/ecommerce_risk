import axios from 'axios'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'ecommerce_risk_token'

const request: any = axios.create({
  baseURL: '',
  timeout: 15000
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body.code !== 'undefined') {
      if (body.code !== 0) {
        ElMessage.error(body.message || '请求失败')
        if (body.code === 40101) {
          localStorage.removeItem(TOKEN_KEY)
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }
        return Promise.reject(body)
      }
      return body.data
    }
    return body
  },
  (error) => {
    ElMessage.error(error?.message || '网络异常')
    if (error?.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default request
