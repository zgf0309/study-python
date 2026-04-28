import type { APIRequestContext } from '@playwright/test'

export const API_BASE = process.env.E2E_API_BASE ?? 'http://127.0.0.1:8090/api'

export type ApiEnvelope<T = unknown> = {
  code: number
  data: { data: T; total?: number } & Record<string, unknown>
  message: string
}

/**
 * 统一 API 调用,自动拆开后端 { code, data: { data, ...extra }, message } 信封。
 * 失败时抛错,便于测试中 await 直接拿到结果。
 */
export async function api<T = unknown>(
  request: APIRequestContext,
  init: {
    method: 'GET' | 'POST' | 'PUT' | 'DELETE'
    path: string
    params?: Record<string, string | number>
    data?: Record<string, unknown>
  },
): Promise<{ envelope: ApiEnvelope<T>; payload: T; total?: number; status: number }> {
  const url = new URL(API_BASE + init.path)
  if (init.params) {
    for (const [k, v] of Object.entries(init.params)) url.searchParams.set(k, String(v))
  }
  const res = await request.fetch(url.toString(), {
    method: init.method,
    data: init.data,
    headers: { 'Content-Type': 'application/json' },
  })
  const status = res.status()
  const envelope = (await res.json()) as ApiEnvelope<T>
  return {
    envelope,
    payload: envelope?.data?.data as T,
    total: envelope?.data?.total as number | undefined,
    status,
  }
}

/** 生成测试唯一标识,避免与遗留数据冲突。 */
export function uniq(prefix: string): string {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`
}

/** 创建一个测试用户,返回完整记录。 */
export async function createUser(
  request: APIRequestContext,
  overrides: Partial<{ name: string; email: string; role: string }> = {},
) {
  const tag = uniq('u')
  const data = {
    name: overrides.name ?? `用户_${tag}`,
    email: overrides.email ?? `${tag}@example.com`,
    role: overrides.role ?? 'viewer',
  }
  const { payload } = await api<{ id: number; name: string; email: string; role: string }>(
    request,
    { method: 'POST', path: '/users', data },
  )
  return payload
}

/** 创建一个测试角色。 */
export async function createRole(
  request: APIRequestContext,
  overrides: Partial<{ name: string; description: string; sort: number; status: string }> = {},
) {
  const tag = uniq('r')
  const data = {
    name: overrides.name ?? `角色_${tag}`,
    description: overrides.description ?? '由 e2e 自动创建',
    sort: overrides.sort ?? 1,
    status: overrides.status ?? 'enabled',
  }
  const { payload } = await api<{ id: number; name: string }>(request, {
    method: 'POST',
    path: '/roles',
    data,
  })
  return payload
}

/** 创建一个测试菜单。 */
export async function createMenu(
  request: APIRequestContext,
  overrides: Partial<{ name: string; path: string; icon: string; sort: number; status: string }> = {},
) {
  const tag = uniq('m')
  const data = {
    name: overrides.name ?? `菜单_${tag}`,
    path: overrides.path ?? `/${tag}`,
    icon: overrides.icon ?? 'appstore',
    sort: overrides.sort ?? 1,
    status: overrides.status ?? 'enabled',
  }
  const { payload } = await api<{ id: number; name: string; path: string }>(request, {
    method: 'POST',
    path: '/menus',
    data,
  })
  return payload
}

/** 静默删除资源,失败也不抛出,用于 afterEach 清理。 */
export async function safeDelete(
  request: APIRequestContext,
  path: string,
): Promise<void> {
  try {
    await request.fetch(API_BASE + path, { method: 'DELETE' })
  } catch {
    // 忽略
  }
}
