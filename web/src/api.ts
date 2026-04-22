import axios from 'axios'

export interface HealthResponse {
  service: string
  status: string
  database: string
  frontend_to_backend: string
  backend_to_database: string
}

export interface UserRecord {
  id: number
  name: string
  email: string
  role: string
  created_at: string
}

export interface CreateUserPayload {
  id: number
  name: string
  email: string
  role: string
}

export interface MenusRecord {
  user_id: number | null
  id: number
  name: string
  path: string
  icon?: string
  sort?: number
  status?: string
  created_at: string
}

export interface CreateMenusPayload {
  user_id?: number | null
  id?: number
  path?: string
  name?: string
  status?: boolean
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

export async function fetchHealth() {
  const response = await apiClient.get<HealthResponse>('/health')
  return response.data
}

export async function fetchUsers() {
  const response = await apiClient.get<UserRecord[]>('/users')
  return response.data
}

export async function createUser(payload: CreateUserPayload) {
  const response = await apiClient.post<UserRecord>('/users', payload)
  return response.data
}

export async function updateUser(payload: CreateUserPayload) {
  const response = await apiClient.put<UserRecord>(`/users`, payload)
  return response.data
}

export async function deleteUser(payload: CreateUserPayload) {
  const response = await apiClient.delete<UserRecord>(`/users/${payload.id}`)
  return response.data
}

export async function fetchMenus(payload: CreateMenusPayload) {
  const response = await apiClient.get<MenusRecord[]>('/menus', { params: payload })
  return response.data
}

export async function createMenus(payload: CreateMenusPayload) {
  const response = await apiClient.post<MenusRecord>('/menus', payload)
  return response.data
}

export async function updateMenus(payload: CreateMenusPayload) {
  const response = await apiClient.put<MenusRecord>(`/menus`, payload)
  return response.data
}

export async function deleteMenus(payload: Pick<MenusRecord, 'id'>) {
  const response = await apiClient.delete<MenusRecord>(`/menus/${payload.id}`)
  return response.data
}
