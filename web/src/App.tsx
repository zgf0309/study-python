import { startTransition, useEffect, useState } from 'react'
import {
  Alert,
  App as AntApp,
  Button,
  Card,
  Col,
  Divider,
  Flex,
  Form,
  Input,
  Layout,
  Modal,
  Row,
  Space,
  Statistic,
  Switch,
  Table,
  Tag,
  Timeline,
  Typography,
} from 'antd'
import {CloseOutlined} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { createUser, updateUser, deleteUser, createMenus, updateMenus, deleteMenus, fetchHealth, fetchUsers, fetchMenus, type CreateUserPayload, type CreateMenusPayload, type HealthResponse, type UserRecord, type MenusRecord } from './api'
import './App.css'



function App() {
  const { message } = AntApp.useApp()
  const [form] = Form.useForm<CreateUserPayload>()
  const [menusForm] = Form.useForm<CreateMenusPayload>()
  const [isEdit, setIsEdit] = useState<boolean>(false)
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [users, setUsers] = useState<UserRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [userLoading, setUserLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [isSetting, setIsSetting] = useState(false)

  const userColumns: ColumnsType<UserRecord> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => <Tag color="gold">{role}</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (value: string) => new Date(value).toLocaleString(),
    },
    {
      title: '操作',
      width: '200px',
      fixed: 'right',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button type="primary" size="small" onClick={() => {
            setUserId(record.id)
            setIsSetting(true) 
          }}>配置</Button>
          <Button type="primary" size="small" onClick={() => {
            setIsEdit(true) 
            form.setFieldsValue({
              id: record.id || undefined,
              name: record.name,
              email: record.email,
              role: record.role,
            });
          }}>编辑</Button>
          <Button type="primary" danger size="small" onClick={() => {
            handleDeleteUser(record)
          }}>删除</Button>
        </Space>
      ),
    },
  ]
  const menuColumns: ColumnsType<MenusRecord> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '菜单名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'path',
      dataIndex: 'path',
      key: 'path',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (value: string) => new Date(value).toLocaleString(),
    },
    {
      title: '操作',
      width: '130px',
      fixed: 'right',
      key: 'action',
      render: (_, record: MenusRecord) => (
        <Space size="middle">
          <Button type="primary" size="small" onClick={() => {
            setMenuModalMode('edit')
            setIsMenuModalOpen(true)
            menusForm.setFieldsValue({
              id: record.id || undefined,
              user_id: record.user_id || undefined,
              name: record.name,
              path: record.path,
              status: record.status === 'enabled',
            })
          }}>编辑</Button>
          
          <Button type="primary" danger size="small" onClick={() => {
            handleDeleteMenus(record)
          }}>删除</Button>
        </Space>
      ),
    },
  ]

  useEffect(() => {
    getUsers();
    getHealth();
  }, [])


  async function getHealth() {
    setLoading(true)
    try {
      const healthData = await fetchHealth()
      startTransition(() => {
        setHealth(healthData)
      })
    } catch (error) {
        void message.error('无法连接本地后端，请先启动 service 项目。')
    } finally {
      setLoading(false)
    }
  }

  async function getUsers() {
    setUserLoading(true)
    try {
      const userData = await fetchUsers()
      startTransition(() => {
        setUsers(userData)
      })
    } catch (error) {
        void message.error('无法连接本地后端，请先启动 service 项目。')
    } finally {
      setUserLoading(false)
    }
  }

  async function handleOptUser(values: CreateUserPayload) {
    setSubmitting(true)

    try {
      if (values?.id) {
        await updateUser(values)
      } else {
        await createUser(values)
      }
      
      startTransition(() => {
        getUsers();
      })
      form.resetFields()
      setIsEdit(false)
      void message.success(values?.id ? '用户已更新本地数据库。' : '用户已写入本地数据库。')
    } catch (error) {
      void message.error(values?.id ? '更新失败，请检查后端和数据库连接。' : '写入失败，请检查后端和数据库连接。')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteUser = async (user: UserRecord) => {
    try {
      await deleteUser(user)
      getUsers();
      void message.success('用户已删除。')
    } catch (error) {
      void message.error('删除失败，请检查后端和数据库连接。')
    }
  }

  const [userId, setUserId] = useState<any>('')
  const [menus, setMenus] = useState<MenusRecord[]>([])
  const [menuLoading, setMenuLoading] = useState<boolean>(false)
  const [isMenuModalOpen, setIsMenuModalOpen] = useState<boolean>(false)
  const [menuModalMode, setMenuModalMode] = useState<'create' | 'edit'>('create')

  useEffect(() => {
    if (isSetting && userId) {
      menusForm.setFieldsValue({
        user_id: userId
      })
      getMenus();
    }
  }, [isSetting, userId])

   async function getMenus() {
    setMenuLoading(true)
    try {
      const params: any = {
        user_id: userId || '',
      }
      const menuData: any = await fetchMenus(params);
      startTransition(() => {
        setMenus(menuData)
      })
    } catch (error) {
        void message.error('无法连接本地后端，请先启动 service 项目。')
    } finally {
      setMenuLoading(false)
    }
  }

  const handleDeleteMenus = async (menu: MenusRecord) => {
    try {
      await deleteMenus(menu)
      getMenus();
      void message.success('菜单已删除。')
    } catch (error) {
      void message.error('删除失败，请检查后端和数据库连接。')
    }
  }

  const handleOptMenus = async (menus: CreateMenusPayload) => {
    const values: any = {
      ...menus,
      status: menus?.status === true ? 'enabled' : 'disabled'
    }
    setSubmitting(true) 
    try {
      if (values?.id) {
        await updateMenus(values)
      } else {
        await createMenus(values)
      }
      
      startTransition(() => {
        setIsMenuModalOpen(false)
        getMenus();
      })
      menusForm.resetFields()
      setIsEdit(false)
      void message.success(values?.id ? '菜单已更新本地数据库。' : '菜单已写入本地数据库。')
    } catch (error) {
      void message.error(values?.id ? '更新失败，请检查后端和数据库连接。' : '写入失败，请检查后端和数据库连接。')
    } finally {
      setSubmitting(false)
    }
  }

  const popoverContent = () => (
    <Form form={menusForm} labelCol={{span: 8}} onFinish={handleOptMenus}>
    <Form.Item
      label="ID"
      name="id"
      hidden={true}
    >
      <Input placeholder="例如：1" />
    </Form.Item>
      <Form.Item
      label="用户ID"
      name="user_id"
      hidden={true}
    >
      <Input placeholder="例如：1" />
    </Form.Item>
    <Form.Item
      label="菜单名称"
      name="name"
      rules={[{ required: true, message: '请输入菜单名称' }]}
    >
      <Input placeholder="例如：张三" />
    </Form.Item>
    <Form.Item
      label="path"
      name="path"
      rules={[
        { required: true, message: '请输入路径' },]}
    >
      <Input placeholder="例如：/index" />
    </Form.Item>
    <Form.Item
      label="状态"
      name="status"
      valuePropName="checked"
      rules={[
        { required: true, message: '请输入状态' },]}
    >
      <Switch checkedChildren="开启" unCheckedChildren="关闭" />
    </Form.Item>
    <Flex gap={10} justify="center">
      <Button type="primary" htmlType="submit" loading={submitting} block>
        保存
      </Button>
      <Button type="default" onClick={() => {
        setIsMenuModalOpen(false)
        menusForm.resetFields()
        menusForm.setFieldsValue({
          user_id: userId,
          status: true,
        })
      }} block>
        取消
      </Button>
    </Flex>
  </Form>
  ) 

  return (
    <Layout className="shell">
      <div className="aurora aurora-left"></div>
      <div className="aurora aurora-right"></div>

      <Layout.Content className="content">
        <section className="hero-panel">
          <Space direction="vertical" size={18} className="hero-copy">
            <Tag color="cyan" bordered={false} className="eyebrow">
              React + Ant Design + FastAPI + SQLite
            </Tag>
            <Typography.Title level={1}>
              本地前后端联调示例
            </Typography.Title>
            <Typography.Paragraph>
              前端通过 /api 请求本地 Python 服务；后端再通过 SQLAlchemy 访问本地 SQLite 数据库。
            </Typography.Paragraph>
            <Space wrap>
              <Tag color="blue">前端 {'->'} 后端: HTTP / JSON</Tag>
              <Tag color="green">后端 {'->'} 数据库: ORM / SQL</Tag>
              <Tag color="gold">独立运行</Tag>
            </Space>
          </Space>

          <Card className="signal-card" loading={loading}>
            <Typography.Title level={4}>当前链路状态</Typography.Title>
            <Timeline
              items={[
                {
                  color: health ? 'blue' : 'gray',
                  children: '前端页面加载后，Axios 调用 /api/health。',
                },
                {
                  color: health?.status === 'ok' ? 'green' : 'gray',
                  children: health?.frontend_to_backend || '等待后端响应。',
                },
                {
                  color: health?.database === 'connected' ? 'green' : 'gray',
                  children: health?.backend_to_database || '等待数据库检查结果。',
                },
              ]}
            />
          </Card>
        </section>

        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Card loading={loading}>
              <Statistic title="后端服务" value={health?.service || 'service'} />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card loading={loading}>
              <Statistic title="接口状态" value={health?.status || 'unknown'} />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card loading={loading}>
              <Statistic title="数据库状态" value={health?.database || 'unknown'} />
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} className="main-grid">
          <Col xs={24} xl={14}>
            <Card
              title="用户列表"
              extra={<Tag color="processing">数据来自本地数据库</Tag>}
            >
              <Alert
                type="info"
                showIcon
                className="hint"
                message="这里的数据流向是：浏览器 -> FastAPI 接口 -> SQLAlchemy -> SQLite。"
              />
              <Table
                rowKey="id"
                columns={userColumns}
                dataSource={users}
                loading={userLoading}
                pagination={{ pageSize: 5 }}
                scroll={{ x: 720 }}
              />
            </Card>
          </Col>

          <Col xs={24} xl={10}>
            {!isSetting ? <Card title="新增用户">
              <Typography.Paragraph className="form-copy">
                提交表单后，前端会调用 POST /api/users，后端校验并写入本地数据库，再把新记录回传给前端更新列表。
              </Typography.Paragraph>
              <Form form={form} layout="vertical" onFinish={handleOptUser}>
                <Form.Item
                  label="ID"
                  name="id"
                  hidden={true}
                >
                  <Input placeholder="例如：1" />
                </Form.Item>
                <Form.Item
                  label="姓名"
                  name="name"
                  rules={[{ required: true, message: '请输入姓名' }]}
                >
                  <Input placeholder="例如：张三" />
                </Form.Item>
                <Form.Item
                  label="邮箱"
                  name="email"
                  rules={[
                    { required: true, message: '请输入邮箱' },
                    { type: 'email', message: '邮箱格式不正确' },
                  ]}
                >
                  <Input placeholder="name@example.com" />
                </Form.Item>
                <Form.Item
                  label="角色"
                  name="role"
                  initialValue="viewer"
                  rules={[{ required: true, message: '请输入角色' }]}
                >
                  <Input placeholder="viewer / admin" />
                </Form.Item>
                {isEdit ? <Flex gap={10} justify="center">
                  <Button type="primary" htmlType="submit" loading={submitting} block>
                    修改本地数据库
                  </Button>
                    <Button htmlType="button" onClick={() => {
                      setIsEdit(false)
                      form.resetFields()
                    }}>
                    取消
                  </Button>
                </Flex> :
                 <Button type="primary" htmlType="submit" loading={submitting} block>
                  写入本地数据库
                </Button>}
              </Form>

              <Divider />

              <Typography.Title level={5}>通讯重点</Typography.Title>
              <div className="flow-list">
                <div>
                  <strong>前端和后台通讯</strong>
                  <p>开发环境由 Vite 代理 /api 到 127.0.0.1:8090，避免本地跨域配置复杂化。</p>
                </div>
                <div>
                  <strong>后台和数据库通讯</strong>
                  <p>FastAPI 通过 SQLAlchemy Session 管理数据库连接，模型变更最终落到 SQLite 文件。</p>
                </div>
              </div>
            </Card> :
            <Card title={<Flex justify={'space-between'}><h5>配置菜单</h5><CloseOutlined onClick={() => setIsSetting(false)} /></Flex>}>
               
               <Flex justify={'flex-end'}> 
                  <Button type={'primary'} size={'small'} onClick={() => {
                    setMenuModalMode('create')
                    setIsMenuModalOpen(true)
                    menusForm.resetFields()
                    menusForm.setFieldsValue({
                      user_id: userId,
                      status: true,
                    })
                  }}>添加菜单</Button>
               </Flex>
                 <Modal
                  open={isMenuModalOpen}
                  title={menuModalMode === 'edit' ? '修改菜单' : '添加菜单'}
                  footer={null}
                  onCancel={() => {
                    setIsMenuModalOpen(false)
                    menusForm.resetFields()
                    menusForm.setFieldsValue({
                      user_id: userId,
                      status: true,
                    })
                  }}
                  destroyOnHidden={false}
                 >
                  {popoverContent()}
                 </Modal>
               <Table
                rowKey="id"
                columns={menuColumns}
                dataSource={menus}
                loading={menuLoading}
                pagination={{ pageSize: 5 }}
                scroll={{ x: 720 }}
              />
            </Card>}
          </Col>
        </Row>
      </Layout.Content>
    </Layout>
  )
}

export default App
