// 通用响应/集合工具，供各领域 Hook 复用。

export type ApiEnvelope<T> = {
  code: number
  message: string
  data: { data: T; total?: number } | null
}

const BACKEND_UNAVAILABLE = '无法连接本地后端，请先启动 service 项目。'

export function backendUnavailableMessage() {
  return BACKEND_UNAVAILABLE
}

export function dedupeRecordsById<T extends { id: number }>(records: T[]): T[] {
  const recordsById = new Map<number, T>()
  for (const record of records) {
    recordsById.set(record.id, record)
  }
  return Array.from(recordsById.values())
}

// 从 envelope 中安全取出列表载荷与可选 total。
export function unwrapList<T>(payload: unknown): { items: T[]; total: number } | null {
  const envelope = payload as ApiEnvelope<T[]> | undefined
  if (!envelope || envelope.code !== 200) {
    return null
  }
  const items = envelope.data?.data ?? []
  const total = envelope.data?.total ?? 0
  return { items, total }
}
