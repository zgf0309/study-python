import { useEffect, useState } from 'react'
import { Col, Form, Layout, Row, Tabs } from 'antd'
import type { TabsProps } from 'antd'

import './App.css'
import { HealthOverview } from './components/HealthOverview'
import { MenuEditorCard } from './components/MenuEditorCard'
import { MenuSettingsCard } from './components/MenuSettingsCard'
import { MenuTableCard } from './components/MenuTableCard'
import { ModelTableCard } from './components/ModelTableCard'
import { RoleEditorCard } from './components/RoleEditorCard'
import { RoleSettingsCard } from './components/RoleSettingsCard'
import { RoleTableCard } from './components/RoleTableCard'
import { UserEditorCard } from './components/UserEditorCard'
import { UserTableCard } from './components/UserTableCard'

import { useHealth } from './hooks/useHealth'
import { useMenus } from './hooks/useMenus'
import { useRoles } from './hooks/useRoles'
import { useUsers } from './hooks/useUsers'
import type {
  CreateMenusPayload,
  CreateRolesPayload,
  CreateUserPayload,
  MenusRecord,
  RolesRecord,
  UserRecord,
} from './services/api'

type TabKey = 'user' | 'role' | 'menu' | 'model'
type SidePanel = 'form' | 'settings'
type FormMode = 'create' | 'edit'

function App() {
  const [userForm] = Form.useForm<CreateUserPayload>()
  const [roleForm] = Form.useForm<CreateRolesPayload>()
  const [menuForm] = Form.useForm<CreateMenusPayload>()

  const [tabKey, setTabKey] = useState<TabKey>('user')
  const [sidePanel, setSidePanel] = useState<SidePanel>('form')
  const [formMode, setFormMode] = useState<FormMode>('create')
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null)

  const health = useHealth()
  const users = useUsers()
  const roles = useRoles()
  const menus = useMenus()

  // 切换 tab 时重置侧栏并按需加载对应数据。
  useEffect(() => {
    setFormMode('create')
    setSidePanel('form')
    if (tabKey === 'role') void roles.load()
    if (tabKey === 'menu') void menus.load()
  }, [tabKey])

  // 进入“为用户配置角色”时，加载全量角色列表并重置表单。
  useEffect(() => {
    if (sidePanel !== 'settings' || selectedUserId === null) return
    resetForm()
    void roles.loadAll()
  }, [sidePanel, selectedUserId])

  // 进入“为角色配置菜单”时，加载全量菜单列表并重置表单。
  useEffect(() => {
    if (sidePanel !== 'settings' || selectedRoleId === null) return
    resetForm()
    void menus.loadAll()
  }, [sidePanel, selectedRoleId])

  function resetForm() {
    if (tabKey === 'user') {
      userForm.resetFields()
      userForm.setFieldsValue({ role: 'viewer' })
    } else if (tabKey === 'role') {
      roleForm.resetFields()
      roleForm.setFieldsValue({ status: true })
    } else if (tabKey === 'menu') {
      menuForm.resetFields()
      menuForm.setFieldsValue({ status: true })
    }
  }

  function openCreatePanel() {
    setSidePanel('form')
    setFormMode('create')
    resetForm()
  }

  function openEditUserPanel(user: UserRecord) {
    setSidePanel('form')
    setFormMode('edit')
    userForm.setFieldsValue({
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role,
    })
  }

  function openEditRolePanel(role: RolesRecord) {
    setSidePanel('form')
    setFormMode('edit')
    roleForm.setFieldsValue({
      id: role.id,
      name: role.name,
      description: role.description,
      sort: role.sort,
      status: role.status === 'enabled',
    })
  }

  function openEditMenuPanel(menu: MenusRecord) {
    setSidePanel('form')
    setFormMode('edit')
    menuForm.setFieldsValue({
      id: menu.id,
      name: menu.name,
      path: menu.path,
      icon: menu.icon,
      sort: menu.sort,
      status: menu.status === 'enabled',
    })
  }

  function openRoleSettings(user: UserRecord) {
    setSelectedUserId(user.id)
    setSidePanel('settings')
  }

  function openMenuSettings(role: RolesRecord) {
    setSelectedRoleId(role.id)
    setSidePanel('settings')
  }

  async function handleUserSubmit(values: CreateUserPayload) {
    if (await users.submit(values)) openCreatePanel()
  }

  async function handleRoleSubmit(values: CreateRolesPayload) {
    if (await roles.submit(values)) openCreatePanel()
  }

  async function handleMenuSubmit(values: CreateMenusPayload) {
    if (await menus.submit(values)) openCreatePanel()
  }

  async function handleSettingSubmit(keys: React.Key[]) {
    if (tabKey === 'user' && selectedUserId !== null) {
      await users.relateRoles(selectedUserId, keys ?? [])
    } else if (tabKey === 'role' && selectedRoleId !== null) {
      await roles.relateMenus(selectedRoleId, keys ?? [])
    }
  }

  const tabItems: TabsProps['items'] = [
    {
      label: '用户',
      key: 'user',
      children: (
        <UserTableCard
          search={users.params}
          onSearch={users.setParams}
          total={users.total}
          users={users.users}
          loading={users.loading}
          onConfigureMenus={openRoleSettings}
          onEdit={openEditUserPanel}
          onDelete={users.remove}
        />
      ),
    },
    {
      label: '角色',
      key: 'role',
      children: (
        <RoleTableCard
          search={roles.params}
          onSearch={roles.setParams}
          total={roles.total}
          roles={roles.roles}
          loading={roles.loading}
          onConfigureMenus={openMenuSettings}
          onEdit={openEditRolePanel}
          onDelete={roles.remove}
        />
      ),
    },
    {
      label: '菜单',
      key: 'menu',
      children: (
        <MenuTableCard
          search={menus.params}
          onSearch={menus.setParams}
          total={menus.total}
          menus={menus.menus}
          loading={menus.loading}
          onEdit={openEditMenuPanel}
          onDelete={menus.remove}
        />
      ),
    },
    {
      label: '模型',
      key: 'model',
      children: <ModelTableCard />,
    },
  ]

  function renderEditorPanel() {
    if (tabKey === 'user') {
      return (
        <UserEditorCard
          mode={formMode}
          form={userForm}
          submitting={users.submitting}
          onSubmit={handleUserSubmit}
          onCancelEdit={openCreatePanel}
        />
      )
    }
    if (tabKey === 'role') {
      return (
        <RoleEditorCard
          mode={formMode}
          form={roleForm}
          submitting={roles.submitting}
          onSubmit={handleRoleSubmit}
          onCancelEdit={openCreatePanel}
        />
      )
    }
    if (tabKey === 'model') return null
    return (
      <MenuEditorCard
        mode={formMode}
        form={menuForm}
        submitting={menus.submitting}
        onSubmit={handleMenuSubmit}
        onCancelEdit={openCreatePanel}
      />
    )
  }

  function renderSettingsPanel() {
    if (tabKey === 'user') {
      return (
        <RoleSettingsCard
          userId={selectedUserId}
          roles={roles.allRoles}
          loading={roles.loading}
          onBack={openCreatePanel}
          handleSubmit={handleSettingSubmit}
        />
      )
    }
    if (tabKey === 'role') {
      return (
        <MenuSettingsCard
          roleId={selectedRoleId}
          menus={menus.allMenus}
          loading={menus.loading}
          onBack={openCreatePanel}
          handleSubmit={handleSettingSubmit}
        />
      )
    }
    return null
  }

  return (
    <Layout className="shell">
      <Layout.Content className="content">
        <HealthOverview health={health.health} loading={health.loading} />

        <Row gutter={[16, 16]} className="main-grid">
          <Col xs={24} xl={tabKey === 'model' ? 24 : 14}>
            <Tabs
              activeKey={tabKey}
              onChange={(key) => setTabKey(key as TabKey)}
              centered
              tabBarStyle={{ background: '#fff', marginBottom: 0, borderRadius: '20px 20px 0 0' }}
              items={tabItems}
            />
          </Col>

          {tabKey === 'model' ? null : (
            <Col xs={24} xl={10}>
              {sidePanel === 'form' ? renderEditorPanel() : renderSettingsPanel()}
            </Col>
          )}
        </Row>
      </Layout.Content>
    </Layout>
  )
}

export default App
