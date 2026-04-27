import { Alert, Button, Card, Flex, Space, Table, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'

import type { MenusRecord } from '../api'
import { formatDateTime } from '../utils/format'

type MenuTableCardProps = {
menus: MenusRecord[]
loading: boolean
onEdit: (menu: MenusRecord) => void
onDelete: (menu: MenusRecord) => void
}

export function MenuTableCard({
menus,
loading,
onEdit,
onDelete,
}: MenuTableCardProps) {
const columns: ColumnsType<MenusRecord> = [
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
    render: formatDateTime,
    },
    {
    title: '操作',
    width: 130,
    fixed: 'right',
    key: 'action',
    render: (_, record) => (
    <Flex gap={12}>
      <Button type="primary" size="small" onClick={()=> onEdit(record)}>
        编辑
      </Button>
      <Button type="primary" danger size="small" onClick={()=> onDelete(record)}>
        删除
      </Button>
    </Flex>
    ),
    },
    ]

  return (
  <Card title="菜单列表" extra={<Tag color="processing">数据来自本地数据库</Tag>} style={{borderRadius: '0 0 24px 24px'}}>
    <Alert type="info" showIcon className="hint" message="这里的数据流向是：浏览器 -> FastAPI 接口 -> SQLAlchemy -> SQLite。" />
    <Table rowKey="id" columns={columns} dataSource={menus} loading={loading} pagination={{ pageSize: 5 }} scroll={{ x:
      720 }} />
  </Card>
  )
  }