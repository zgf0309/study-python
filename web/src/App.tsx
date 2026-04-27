import { startTransition, useEffect, useState } from 'react'
import { App as AntApp, Col, Form, Layout, Row, Tabs } from 'antd'

import {
  createMenus,
  createRoles,
  createUser,
  deleteMenus,
  deleteUser,
  deleteRoles,
  fetchHealth,
  fetchMenus,
  fetchRoles,
  fetchUsers,
  updateMenus,
  updateUser,
  updateRoles,
  userRelationRoles,
  roleRelationMenus,
  type CreateMenusPayload,
  type CreateUserPayload,
  type CreateRolesPayload,
  type HealthResponse,
  type MenusRecord,
  type RolesRecord,
  type UserRecord,
} from './services/api'
import './App.css'
import { HealthOverview } from './components/HealthOverview'
import { MenuSettingsCard } from './components/MenuSettingsCard'
import { RoleSettingsCard } from './components/RoleSettingsCard'
import { UserEditorCard } from './components/UserEditorCard'
import { RoleEditorCard } from './components/RoleEditorCard'
import { MenuEditorCard } from './components/MenuEditorCard'
import { UserTableCard } from './components/UserTableCard'
import { MenuTableCard } from './components/MenuTableCard'
import { RoleTableCard } from './components/RoleTableCard'


type SidePanel = 'form' | 'settings'
type OptFormMode = 'create' | 'edit'

function dedupeRecordsById<T extends { id: number }>(records: T[]) {
  const recordsById = new Map<number, T>()

  for (const record of records) {
    recordsById.set(record.id, record)
  }

  return Array.from(recordsById.values())
}

function App() {
  const { message } = AntApp.useApp()
  const [userForm] = Form.useForm<CreateUserPayload>()
  const [roleForm] = Form.useForm<CreateRolesPayload>()
  const [menuForm] = Form.useForm<CreateMenusPayload>()

  const [sidePanel, setSidePanel] = useState<SidePanel>('form')
  const [optFormMode, setOptFormMode] = useState<OptFormMode>('create')
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null)
  const [tabKey, setTabKey] = useState<string>('user')
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [userParams, setUserParams] = useState<any>({ name: '', page: 1, page_size: 5 })
  const [totalUsers, setTotalUsers] = useState<number>(0)
  const [users, setUsers] = useState<UserRecord[]>([])
  const [menus, setMenus] = useState<MenusRecord[]>([])
  const [roles, setRoles] = useState<RolesRecord[]>([])

  const [loading, setLoading] = useState(false)
  const [userLoading, setUserLoading] = useState(false)
  const [roleLoading, setRoleLoading] = useState(false)
  const [menuLoading, setMenuLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    void Promise.all([loadUsers(), loadHealth()])
  }, [])

  useEffect(() => {
    console.log('tabKey changed to', tabKey)
    setOptFormMode('create');
    setSidePanel('form')
    if (tabKey === 'user') {
      loadUsers()
    } else if (tabKey === 'role') {
      loadRoles()
    } else if (tabKey === 'menu') {
      loadMenus()
    }
  }, [tabKey, userParams])

  useEffect(() => {
    if (sidePanel !== 'settings' || selectedUserId === null) {
      return
      }
      resetForm()
    void loadRoles()
  }, [selectedUserId])


  useEffect(() => {
    if (sidePanel !== 'settings' || selectedRoleId === null) {
      return
    }
    resetForm()
    void loadMenus()
  }, [selectedRoleId])

  function showBackendUnavailable() {
    void message.error('无法连接本地后端，请先启动 service 项目。')
  }

  function resetForm() {
    if (tabKey === 'user') {
      userForm.resetFields()
      userForm.setFieldsValue({ role: 'viewer' })
    } else if (tabKey === 'role') {
      roleForm.resetFields()
      roleForm.setFieldsValue({
        status: true,
      })
    } else if (tabKey === 'menu') {
      menuForm.resetFields()
      menuForm.setFieldsValue({
        status: true,
      })
    }
  }

  async function loadHealth() {
    setLoading(true)
    try {
      const healthData: any = await fetchHealth()
      const { code, data } = healthData
      if (code === 200) {
        startTransition(() => {
        setHealth(data?.data || null)
      })
      }
    } catch {
      showBackendUnavailable()
    } finally {
      setLoading(false)
    }
  }

  async function loadUsers() {
    setUserLoading(true)
    try {
      const userData: any = await fetchUsers(userParams)
      console.log('userData', userData)
      const {code, data} = userData
      if (code === 200) {
        startTransition(() => {
          setUsers(dedupeRecordsById(data?.data || []))
          setTotalUsers(data?.total || 0)
        })
      } else {
        setUsers([])
        setTotalUsers(0)
      }
      
    } catch {
      showBackendUnavailable()
    } finally {
      setUserLoading(false)
    }
  }

  async function loadRoles() {

    setRoleLoading(true)
    try {
      const roleData: any = await fetchRoles({name: ''})
      const {code, data} = roleData
      if (code === 200) {
        startTransition(() => {
          setRoles(dedupeRecordsById(data?.data || []))
        })
      }
    } catch {
      showBackendUnavailable()
    } finally {
      setRoleLoading(false)
    }
  }

  async function loadMenus() {

    setMenuLoading(true)
    try {
      const menuData: any = await fetchMenus({ name: '' })
      const { code, data } = menuData
      if (code === 200) {
        startTransition(() => {
          setMenus(dedupeRecordsById(data?.data || []))
        })
      }
    } catch {
      showBackendUnavailable()
    } finally {
      setMenuLoading(false)
    }
  }

  async function handleUserSubmit(values: CreateUserPayload) {
    setSubmitting(true)

    try {
      if (values.id) {
        await updateUser(values)
      } else {
        await createUser(values)
      }

      await loadUsers()
      resetForm()
      setOptFormMode('create')
      setSidePanel('form')
      void message.success(values.id ? '用户已更新本地数据库。' : '用户已写入本地数据库。')
    } catch {
      void message.error(values.id ? '更新失败，请检查后端和数据库连接。' : '写入失败，请检查后端和数据库连接。')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteUser = async (user: UserRecord) => {
    try {
      await deleteUser(user)
      await loadUsers()
      void message.success('用户已删除。')
    } catch {
      void message.error('删除失败，请检查后端和数据库连接。')
    }
  }

  const handleDeleteRole = async (role: RolesRecord) => {
    try {
      await deleteRoles(role)
      await loadRoles()
      void message.success('角色已删除!')
    } catch {
      void message.error('操作失败，请检查后端和数据库连接。')
    }
  }

  const handleDeleteMenus = async (menu: MenusRecord) => {
    try {
      await deleteMenus(menu)
      await loadMenus()
      void message.success('菜单已删除。')
    } catch {
      void message.error('删除失败，请检查后端和数据库连接。')
    }
  }

  function openCreatePanel() {
    setSidePanel('form')
    setOptFormMode('create')
    resetForm()
  }

  function openEditUserPanel(user: UserRecord) {
    setSidePanel('form')
    setOptFormMode('edit')
    userForm.setFieldsValue({
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role,
    })
  }

  function openEditRolePanel(role: RolesRecord) {
    setSidePanel('form')
    setOptFormMode('edit')
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
    setOptFormMode('edit')
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

  const handleRoleSubmit = async (values: CreateRolesPayload) => {
    const payload: CreateRolesPayload = {
      ...values,
      status: values.status === true ? 'enabled' : 'disabled',
    }

    setSubmitting(true)
    try {
      if (payload.id) {
        await updateRoles(payload)
      } else {
        await createRoles(payload)
      }

      await loadRoles()
      resetForm()
      setOptFormMode('create')
      setSidePanel('form')
      void message.success(payload.id ? '角色已更新本地数据库。' : '角色已写入本地数据库。')
    } catch {
      void message.error(payload.id ? '更新失败，请检查后端和数据库连接。' : '写入失败，请检查后端和数据库连接。')
    } finally {
      setSubmitting(false)
    }
  }

  const handleMenuSubmit = async (values: CreateMenusPayload) => {
    const payload: CreateMenusPayload = {
      ...values,
      status: values.status === true ? 'enabled' : 'disabled',
    }

    setSubmitting(true)
    try {
      if (payload.id) {
        await updateMenus(payload)
      } else {
        await createMenus(payload)
      }

      await loadMenus()
      resetForm()
      void message.success(payload.id ? '菜单已更新本地数据库。' : '菜单已写入本地数据库。')
    } catch {
      void message.error(payload.id ? '更新失败，请检查后端和数据库连接。' : '写入失败，请检查后端和数据库连接。')
    } finally {
      setSubmitting(false)
    }
  }

  const handleSettingSubmit = async (keys: React.Key[]) => {
    if (tabKey === 'user' && selectedUserId !== null) {
      try {
        await userRelationRoles({ id: selectedUserId, role_ids: keys || [] })
        await loadUsers()
        void message.success('用户权限已更新。')
      } catch {
        void message.error('更新失败，请检查后端和数据库连接。')
      }
    } else if (tabKey === 'role' && selectedRoleId !== null) {
      try {
        await roleRelationMenus({ id: selectedRoleId, menu_ids: keys || [] })
        await loadRoles()
        void message.success('角色权限已更新。')
      } catch {
        void message.error('更新失败，请检查后端和数据库连接。')
      }
    }
  }

  const TabItems: any[] = [{
        label: '用户',
        key: 'user',
        children: <UserTableCard
                search={userParams}
                onSearch={setUserParams}
                total={totalUsers}
                users={users}
                loading={userLoading}
                onConfigureMenus={openRoleSettings}
                onEdit={openEditUserPanel}
                onDelete={handleDeleteUser}
              />,
      }, {
        label: '角色',
        key: 'role',
        children: <RoleTableCard
                roles={roles}
                loading={roleLoading}
                onConfigureMenus={openMenuSettings}
                onEdit={openEditRolePanel}
                onDelete={handleDeleteRole}
              />,
      }, {
        label: '菜单',
        key: 'menu',
        children: <MenuTableCard
                menus={menus}
                loading={menuLoading}
                onEdit={openEditMenuPanel}
                onDelete={handleDeleteMenus}
              />,
      },
    ]
  return (
    <Layout className="shell">
      <Layout.Content className="content">
        <HealthOverview health={health} loading={loading} />

        <Row gutter={[16, 16]} className="main-grid">
          <Col xs={24} xl={14}>
            <Tabs
              activeKey={tabKey}
              onChange={setTabKey}
              centered
              tabBarStyle={{background: '#fff', marginBottom: 0, borderRadius: '20px 20px 0 0'}}
              items={TabItems}
            />
          </Col>

          <Col xs={24} xl={10}>
            {sidePanel === 'form' ? (
              <>
                {tabKey === 'user' && (
                  <UserEditorCard
                    mode={optFormMode}
                    form={userForm}
                    submitting={submitting}
                    onSubmit={handleUserSubmit}
                    onCancelEdit={openCreatePanel}
                />)}
                {tabKey === 'role' && (
                  <RoleEditorCard
                    mode={optFormMode}
                    form={roleForm}
                    submitting={submitting}
                    onSubmit={handleRoleSubmit}
                    onCancelEdit={openCreatePanel}
                />)}
                {tabKey === 'menu' && (
                  <MenuEditorCard
                    mode={optFormMode}
                    form={menuForm}
                    submitting={submitting}
                    onSubmit={handleMenuSubmit}
                    onCancelEdit={openCreatePanel}
                />)}
              </>
            ) : (
              <>
                { tabKey === 'user' && (
                  <RoleSettingsCard
                    roles={roles}
                    loading={roleLoading}
                    onBack={openCreatePanel}
                    handleSubmit={handleSettingSubmit}
                  />)}
                { tabKey === 'role' && (
                  <MenuSettingsCard
                    menus={menus}
                    loading={menuLoading}
                    onBack={openCreatePanel}
                    handleSubmit={handleSettingSubmit}
                  />)}
              </>
            )}
          </Col>
        </Row>
      </Layout.Content>
    </Layout>
  )
}

export default App
