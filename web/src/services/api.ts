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

export interface ModelConfigRecord {
  id: number
  name: string
  base_url: string
  model_name: string
  provider: string
  is_default: boolean
  status: string
  created_at: string
}

export type ChatRole = 'system' | 'user' | 'assistant'

export interface ChatMessagePayload {
  role: ChatRole
  content: string
}

export interface EmbeddingsResponse {
  object?: string
  model?: string
  data?: Array<{
    object?: string
    index?: number
    embedding?: number[]
  }>
  usage?: {
    prompt_tokens?: number
    total_tokens?: number
  }
}

export interface ChunkEmbeddingsResponse {
  model?: string
  chunk_size: number
  chunk_overlap: number
  total_chunks: number
  chunks: Array<{
    index: number
    content: string
    start: number
    end: number
    length: number
    embedding: number[]
    embedding_dim: number
  }>
  usage?: {
    prompt_tokens?: number
    total_tokens?: number
  }
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

export async function fetchModels() {
  return request<ModelConfigRecord[]>({
    method: 'GET',
    url: '/models',
  })
}

export async function createEmbeddings(payload: { model_id?: number; input: string | string[] }) {
  return request<EmbeddingsResponse>({
    method: 'POST',
    url: '/embeddings',
    data: payload,
  })
}

export async function createChunkEmbeddings(payload: {
  model_id?: number
  text: string
  chunk_size?: number
  chunk_overlap?: number
}) {
  return request<ChunkEmbeddingsResponse>({
    method: 'POST',
    url: '/embeddings/chunks',
    data: payload,
  })
}

function getApiBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL || '/api'
}

export async function streamChat(
  payload: {
    model_id?: number
    messages: ChatMessagePayload[]
    temperature?: number
    max_tokens?: number
  },
  handlers: {
    onDelta: (content: string) => void
    onError?: (message: string) => void
    signal?: AbortSignal
  },
) {
  const response = await fetch(`${getApiBaseUrl()}/chat/stream`, {
    method: 'POST',
    headers: {
      Accept: 'text/event-stream',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
    signal: handlers.signal,
  })

  if (!response.ok || !response.body) {
    throw new Error('模型流式接口调用失败。')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''

    for (const event of events) {
      const line = event
        .split('\n')
        .find((item) => item.startsWith('data:'))
        ?.replace(/^data:\s?/, '')
      if (!line || line === '[DONE]') continue

      try {
        const chunk = JSON.parse(line)
        const errorMessage = chunk?.error?.message
        if (errorMessage) {
          handlers.onError?.(String(errorMessage))
          continue
        }
        const content = chunk?.choices?.[0]?.delta?.content
        if (content) handlers.onDelta(String(content))
      } catch {
        // 忽略非 JSON 调试行，保持流式会话不中断。
      }
    }
  }
}
