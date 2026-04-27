import { App as AntApp } from 'antd'
import { startTransition, useCallback, useEffect, useState } from 'react'
import type { Key } from 'react'

import {
  createUser,
  deleteUser,
  fetchUsers,
  updateUser,
  userRelationRoles,
  type CreateUserPayload,
  type UserRecord,
} from '../services/api'
import { backendUnavailableMessage, dedupeRecordsById, unwrapList } from './utils'

export type UserListParams = {
  name: string
  page: number
  page_size: number
}

const DEFAULT_PARAMS: UserListParams = { name: '', page: 1, page_size: 5 }

export function useUsers() {
  const { message } = AntApp.useApp()
  const [users, setUsers] = useState<UserRecord[]>([])
  const [total, setTotal] = useState(0)
  const [params, setParams] = useState<UserListParams>(DEFAULT_PARAMS)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchUsers(params as unknown as CreateUserPayload)
      const result = unwrapList<UserRecord>(res)
      startTransition(() => {
        setUsers(result ? dedupeRecordsById(result.items) : [])
        setTotal(result?.total ?? 0)
      })
    } catch {
      void message.error(backendUnavailableMessage())
    } finally {
      setLoading(false)
    }
  }, [params, message])

  useEffect(() => {
    void load()
  }, [load])

  const submit = useCallback(
    async (values: CreateUserPayload) => {
      const isUpdate = !!values.id
      setSubmitting(true)
      try {
        if (isUpdate) {
          await updateUser(values)
        } else {
          await createUser(values)
        }
        await load()
        void message.success(isUpdate ? '用户已更新本地数据库。' : '用户已写入本地数据库。')
        return true
      } catch {
        void message.error(isUpdate ? '更新失败，请检查后端和数据库连接。' : '写入失败，请检查后端和数据库连接。')
        return false
      } finally {
        setSubmitting(false)
      }
    },
    [load, message],
  )

  const remove = useCallback(
    async (user: UserRecord) => {
      try {
        await deleteUser(user)
        await load()
        void message.success('用户已删除。')
      } catch {
        void message.error('删除失败，请检查后端和数据库连接。')
      }
    },
    [load, message],
  )

  const relateRoles = useCallback(
    async (userId: number, roleIds: Key[]) => {
      try {
        await userRelationRoles({ id: userId, role_ids: roleIds })
        await load()
        void message.success('用户权限已更新。')
      } catch {
        void message.error('更新失败，请检查后端和数据库连接。')
      }
    },
    [load, message],
  )

  return {
    users,
    total,
    params,
    setParams,
    loading,
    submitting,
    load,
    submit,
    remove,
    relateRoles,
  }
}
