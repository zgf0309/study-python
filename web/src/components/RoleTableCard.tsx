import { Alert, Button, Card, Flex, Input, Space, Table, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'

import type { RolesRecord } from '../services/api'
import { formatDateTime } from '../utils/format'

type RoleTableCardProps = {
roles: RolesRecord[]
loading: boolean
search: any
total: number
onSearch: (values: any) => void
onConfigureMenus: (role: RolesRecord) => void
onEdit: (role: RolesRecord) => void
onDelete: (role: RolesRecord) => void
}

export function RoleTableCard({
roles,
loading,
search,
total,
onSearch,
onConfigureMenus,
onEdit,
onDelete,
}: RoleTableCardProps) {
const columns: ColumnsType<RolesRecord> = [
  {
  title: 'ID',
  dataIndex: 'id',
  key: 'id',
  width: 80,
  },
  {
  title: '角色名称',
  dataIndex: 'name',
  key: 'name',
  },
  {
  title: '描述',
  dataIndex: 'description',
  key: 'description',
  },
  {
  title: '状态',
  dataIndex: 'status',
  key: 'status',
  render: (status: string) => <Tag color="gold">{status}</Tag>,
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
      <h4 className="panel-title">角色列表</h4>
      <Input placeholder="搜索角色" style={{ width: 200 }} onInput={(e: any) => onSearch({ ...search, name: e.target.value, page: 1 })} />
    </Flex>
  } extra={<Tag color="processing">数据来自本地数据库</Tag>} style={{borderRadius: '0 0 24px 24px'}}>
    <Alert type="info" showIcon className="hint" message="这里的数据流向是：浏览器 -> FastAPI 接口 -> SQLAlchemy -> SQLite。" />
    <Table rowKey="id" columns={columns} dataSource={roles} loading={loading} pagination={{ current: search?.page, pageSize: search?.page_size, total, onChange: (page, pageSize) => onSearch({ ...search, page, page_size: pageSize }) }} scroll={{ x: 720 }} />
  </Card>
  )
  }