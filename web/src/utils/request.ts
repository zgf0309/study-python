import axios from 'axios'
import type { AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'

type ApiEnvelope<T> = {
  code: number
  data: T
  message: string
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

function isApiEnvelope<T>(payload: unknown): payload is ApiEnvelope<T> {
  if (!payload || typeof payload !== 'object') {
    return false
  }

  return 'code' in payload && 'data' in payload && 'message' in payload
}

function getStatusFallbackMessage(status?: number) {
  if (status === 401) {
    return '登录状态已失效，请重新登录。'
  }

  if (status === 403) {
    return '没有权限执行当前操作。'
  }

  if (status === 500) {
    return '服务器内部错误，请稍后重试。'
  }

  return '请求失败，请稍后重试。'
}

function getErrorMessage(error: AxiosError<{ message?: string }>) {
  const status = error.response?.status
  const backendMessage = error.response?.data?.message

  if (status === 401 || status === 403 || status === 500) {
    return backendMessage || getStatusFallbackMessage(status)
  }

  return backendMessage || error.message || getStatusFallbackMessage(status)
}

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  config.headers.set('Accept', 'application/json')

  if (config.data !== undefined && !config.headers.get('Content-Type')) {
    config.headers.set('Content-Type', 'application/json')
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ message?: string }>) => {
    return Promise.reject(new Error(getErrorMessage(error)))
  },
)

async function request<T>(config: AxiosRequestConfig) {
  const response = await apiClient.request<ApiEnvelope<T> | T>(config)
  console.log('response====>', response)
  const payload = response.data
  console.log('response.data====>', response.data)
  if (!isApiEnvelope<T>(payload)) {
    return payload as T
  }

  if (payload.code !== 200) {
    throw new Error(payload.message || getStatusFallbackMessage(payload.code))
  }

  return payload
}

export default request