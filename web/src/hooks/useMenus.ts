import { App as AntApp } from 'antd'
import { startTransition, useCallback, useEffect, useState } from 'react'

import {
  createMenus,
  deleteMenus,
  fetchMenus,
  updateMenus,
  type CreateMenusPayload,
  type MenusRecord,
} from '../services/api'
import { backendUnavailableMessage, dedupeRecordsById, unwrapList } from './utils'

function normalizeStatus(status: CreateMenusPayload['status']): 'enabled' | 'disabled' | undefined {
  if (status === true) return 'enabled'
  if (status === false) return 'disabled'
  return status
}

export type MenuListParams = {
  name: string
  page: number
  page_size: number
}

const DEFAULT_PARAMS: MenuListParams = { name: '', page: 1, page_size: 5 }

export function useMenus() {
  const { message } = AntApp.useApp()
  const [menus, setMenus] = useState<MenusRecord[]>([])
  const [allMenus, setAllMenus] = useState<MenusRecord[]>([])
  const [total, setTotal] = useState(0)
  const [params, setParams] = useState<MenuListParams>(DEFAULT_PARAMS)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchMenus(params as unknown as CreateMenusPayload)
      const result = unwrapList<MenusRecord>(res)
      startTransition(() => {
        setMenus(result ? dedupeRecordsById(result.items) : [])
        setTotal(result?.total ?? 0)
      })
    } catch {
      void message.error(backendUnavailableMessage())
    } finally {
      setLoading(false)
    }
  }, [params, message])

  // 加载全量菜单（不分页），供“为角色配置菜单”面板使用。
  const loadAll = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchMenus({ page: 0 } as unknown as CreateMenusPayload)
      const result = unwrapList<MenusRecord>(res)
      startTransition(() => {
        setAllMenus(result ? dedupeRecordsById(result.items) : [])
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
    async (values: CreateMenusPayload) => {
      const payload: CreateMenusPayload = { ...values, status: normalizeStatus(values.status) }
      const isUpdate = !!payload.id
      setSubmitting(true)
      try {
        if (isUpdate) {
          await updateMenus(payload)
        } else {
          await createMenus(payload)
        }
        await load()
        void message.success(isUpdate ? '菜单已更新本地数据库。' : '菜单已写入本地数据库。')
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
    async (menu: MenusRecord) => {
      try {
        await deleteMenus(menu)
        await load()
        void message.success('菜单已删除。')
      } catch {
        void message.error('删除失败，请检查后端和数据库连接。')
      }
    },
    [load, message],
  )

  return {
    menus,
    allMenus,
    total,
    params,
    setParams,
    loading,
    submitting,
    load,
    loadAll,
    submit,
    remove,
  }
}
