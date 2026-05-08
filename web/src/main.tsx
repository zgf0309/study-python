import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import type { Root } from 'react-dom/client'
import { App as AntApp, ConfigProvider, unstableSetRender } from 'antd'
import './index.css'
import App from './App.tsx'

type AntdRenderContainer = (Element | DocumentFragment) & {
  _reactRoot?: Root
}

// Ant Design v5 在 React 19 下需要显式接入 createRoot，避免运行时兼容性警告。
unstableSetRender((node, container) => {
  const renderContainer = container as AntdRenderContainer
  renderContainer._reactRoot ??= createRoot(container)
  renderContainer._reactRoot.render(node)

  return async () => {
    renderContainer._reactRoot?.unmount()
    renderContainer._reactRoot = undefined
  }
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#0057ff',
          colorInfo: '#0057ff',
          borderRadius: 18,
          fontFamily: 'Manrope, Segoe UI, sans-serif',
        },
      }}
    >
      <AntApp>
        <App />
      </AntApp>
    </ConfigProvider>
  </StrictMode>,
)
