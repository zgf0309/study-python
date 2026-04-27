import { Alert, Button, Card, Flex, Input, Space, Table, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'

import type { UserRecord } from '../services/api'
import { formatDateTime } from '../utils/format'

type UserTableCardProps = {
users: UserRecord[]
loading: boolean
onConfigureMenus: (user: UserRecord) => void
search: any
total: number
onSearch: (values: any) => void
onEdit: (user: UserRecord) => void
onDelete: (user: UserRecord) => void
}

export function UserTableCard({
users,
loading,
onConfigureMenus,
search,
total,
onSearch,
onEdit,
onDelete,
}: UserTableCardProps) {
const columns: ColumnsType<UserRecord> = [
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
  render: formatDateTime,
  },
  {
  title: '操作',
  width: 200,
  fixed: 'right',
  key: 'action',
  render: (_, record) => (
  <Space size="middle">
    <Button type="primary" size="small" onClick={()=> onConfigureMenus(record)}>
      配置
    </Button>
    <Button type="primary" size="small" onClick={()=> onEdit(record)}>
      编辑
    </Button>
    <Button type="primary" danger size="small" onClick={()=> onDelete(record)}>
      删除
    </Button>
  </Space>
  ),
  },
  ]

  return (
  <Card title={
    <Flex gap={20} align="center">
      <h4 className="panel-title">用户列表</h4>
      <Input placeholder="搜索用户" style={{ width: 200 }} onInput={(e: any) => onSearch({ ...search, name: e.target.value})} />
    </Flex>
  } extra={<Tag color="processing">数据来自本地数据库</Tag>} style={{borderRadius: '0 0 24px 24px'}}>
    <Alert type="info" showIcon className="hint" message="这里的数据流向是：浏览器 -> FastAPI 接口 -> SQLAlchemy -> SQLite。" />
    <Table rowKey="id" columns={columns} dataSource={users} loading={loading} pagination={{ current: search?.page, pageSize: search.page_size, total: total, onChange: (page, pageSize) => {onSearch({...search, page, page_size: pageSize}) }} } scroll={{ x:
      720 }} />
  </Card>
  )
  }