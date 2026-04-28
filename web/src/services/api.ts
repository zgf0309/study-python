import request from '../utils/request'

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
  role_ids: number[]
  created_at: string
}

export interface CreateUserPayload {
  id?: number
  name: string
  email: string
  role: string
}

export interface MenusRecord {
  id: number
  name: string
  path: string
  icon?: string
  sort?: number
  status?: string
  created_at: string
}

export interface CreateMenusPayload {
  id?: number
  path?: string
  name?: string
  icon?: string
  sort?: number
  status?: boolean | 'enabled' | 'disabled'
}


export interface RolesRecord {
  id: number
  name: string
  description?: string
  sort?: number
  user_ids: number[]
  status?: string
  created_at: string
}

export interface CreateRolesPayload {
  id?: number
  name?: string
  description?: string
  sort?: number
  status?: boolean | 'enabled' | 'disabled'
}

export async function fetchHealth() {
  return request<HealthResponse>({
    method: 'GET',
    url: '/health',
  })
}

export async function fetchUsers(payload: CreateUserPayload) {
  return request<UserRecord[]>({
    method: 'GET',
    url: '/users',
    params: payload,
  })
}

export async function createUser(payload: CreateUserPayload) {
  return request<UserRecord>({
    method: 'POST',
    url: '/users',
    data: payload,
  })
}

export async function updateUser(payload: CreateUserPayload) {
  return request<UserRecord>({
    method: 'PUT',
    url: '/users',
    data: payload,
  })
}

export async function deleteUser(payload: CreateUserPayload) {
  return request<UserRecord>({
    method: 'DELETE',
    url: `/users/${payload.id}`,
  })
}

export async function getRelationRoles(payload: any) {
  return request<RolesRecord[]>({
    method: 'GET',
    url: `/users/relation-roles`,
    params: payload,
  })
}

export async function userRelationRoles(payload: any) {
  return request<any>({
    method: 'POST',
    url: '/users/relation-roles',
    data: payload,
  })
}

export async function fetchMenus(payload: CreateMenusPayload) {
  return request<MenusRecord[]>({
    method: 'GET',
    url: '/menus',
    params: payload,
  })
}

export async function createMenus(payload: CreateMenusPayload) {
  return request<MenusRecord>({
    method: 'POST',
    url: '/menus',
    data: payload,
  })
}

export async function updateMenus(payload: CreateMenusPayload) {
  return request<MenusRecord>({
    method: 'PUT',
    url: '/menus',
    data: payload,
  })
}

export async function deleteMenus(payload: Pick<MenusRecord, 'id'>) {
  return request<MenusRecord>({
    method: 'DELETE',
    url: `/menus/${payload.id}`,
  })
}

export async function fetchRoles(payload: CreateRolesPayload) {
  return request<RolesRecord[]>({
    method: 'GET',
    url: '/roles',
    params: payload,
  })
}

export async function createRoles(payload: CreateRolesPayload) {
  return request<RolesRecord>({
    method: 'POST',
    url: '/roles',
    data: payload,
  })
}

export async function updateRoles(payload: CreateRolesPayload) {
  return request<RolesRecord>({
    method: 'PUT',
    url: '/roles',
    data: payload,
  })
}

export async function deleteRoles(payload: Pick<RolesRecord, 'id'>) {
  return request<RolesRecord>({
    method: 'DELETE',
    url: `/roles/${payload.id}`,
  })
}

export async function roleRelationMenus(payload: any) {
  return request<any>({
    method: 'POST',
    url: '/roles/relation-menus',
    data: payload,
  })
}

export async function getRelationMenus(payload: any) {
  return request<MenusRecord[]>({
    method: 'GET',
    url: '/roles/relation-menus',
    params: payload,
  })
}