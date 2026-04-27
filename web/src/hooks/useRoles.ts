import { App as AntApp } from 'antd'
import { startTransition, useCallback, useEffect, useState } from 'react'
import type { Key } from 'react'

import {
  createRoles,
  deleteRoles,
  fetchRoles,
  roleRelationMenus,
  updateRoles,
  type CreateRolesPayload,
  type RolesRecord,
} from '../services/api'
import { backendUnavailableMessage, dedupeRecordsById, unwrapList } from './utils'

type StatusBoolean = boolean | 'enabled' | 'disabled' | undefined

function normalizeStatus(status: StatusBoolean): 'enabled' | 'disabled' | undefined {
  if (status === true) return 'enabled'
  if (status === false) return 'disabled'
  return status
}

export type RoleListParams = {
  name: string
  page: number
  page_size: number
}

const DEFAULT_PARAMS: RoleListParams = { name: '', page: 1, page_size: 5 }

export function useRoles() {
  const { message } = AntApp.useApp()
  const [roles, setRoles] = useState<RolesRecord[]>([])
  const [allRoles, setAllRoles] = useState<RolesRecord[]>([])
  const [total, setTotal] = useState(0)
  const [params, setParams] = useState<RoleListParams>(DEFAULT_PARAMS)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchRoles(params as unknown as CreateRolesPayload)
      const result = unwrapList<RolesRecord>(res)
      startTransition(() => {
        setRoles(result ? dedupeRecordsById(result.items) : [])
        setTotal(result?.total ?? 0)
      })
    } catch {
      void message.error(backendUnavailableMessage())
    } finally {
      setLoading(false)
    }
  }, [params, message])

  // 加载全量角色（不分页），供“为用户配置角色”面板使用。
  const loadAll = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchRoles({ page: 0 } as unknown as CreateRolesPayload)
      const result = unwrapList<RolesRecord>(res)
      startTransition(() => {
        setAllRoles(result ? dedupeRecordsById(result.items) : [])
      })
    } catch {
      void message.error(backendUnavailableMessage())
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    void load()
  }, [load])

  const submit = useCallback(
    async (values: CreateRolesPayload) => {
      const payload: CreateRolesPayload = { ...values, status: normalizeStatus(values.status) }
      const isUpdate = !!payload.id
      setSubmitting(true)
      try {
        if (isUpdate) {
          await updateRoles(payload)
        } else {
          await createRoles(payload)
        }
        await load()
        void message.success(isUpdate ? '角色已更新本地数据库。' : '角色已写入本地数据库。')
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
    async (role: RolesRecord) => {
      try {
        await deleteRoles(role)
        await load()
        void message.success('角色已删除!')
      } catch {
        void message.error('操作失败，请检查后端和数据库连接。')
      }
    },
    [load, message],
  )

  const relateMenus = useCallback(
    async (roleId: number, menuIds: Key[]) => {
      try {
        await roleRelationMenus({ id: roleId, menu_ids: menuIds })
        await load()
        void message.success('角色权限已更新。')
      } catch {
        void message.error('更新失败，请检查后端和数据库连接。')
      }
    },
    [load, message],
  )

  return {
    roles,
    allRoles,
    total,
    params,
    setParams,
    loading,
    submitting,
    load,
    loadAll,
    submit,
    remove,
    relateMenus,
  }
}
