import { App as AntApp } from 'antd'
import { startTransition, useCallback, useEffect, useState } from 'react'

import { fetchHealth, type HealthResponse } from '../services/api'
import { backendUnavailableMessage } from './utils'

type HealthEnvelope = {
  code: number
  data: { data: HealthResponse | null } | null
}

export function useHealth() {
  const { message } = AntApp.useApp()
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = (await fetchHealth()) as unknown as HealthEnvelope
      if (res?.code === 200) {
        startTransition(() => setHealth(res.data?.data ?? null))
      }
    } catch {
      void message.error(backendUnavailableMessage())
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    void load()
  }, [load])

  return { health, loading, reload: load }
}
