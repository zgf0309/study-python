import { Alert, Button, Card, Flex, Input, Table, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'

import type { MenusRecord } from '../services/api'
import { formatDateTime } from '../utils/format'

type MenuTableCardProps = {
menus: MenusRecord[]
loading: boolean
search: any
total: number
onSearch: (values: any) => void
onEdit: (menu: MenusRecord) => void
onDelete: (menu: MenusRecord) => void
}

export function MenuTableCard({
menus,
loading,
search,
total,
onSearch,
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
  <Card title={
    <Flex gap={20} align="center">
      <h4 className="panel-title">菜单列表</h4>
      <Input placeholder="搜索菜单" style={{ width: 200 }} onInput={(e: any) => onSearch({ ...search, name: e.target.value, page: 1 })} />
    </Flex>
  } extra={<Tag color="processing">数据来自本地数据库</Tag>} style={{borderRadius: '0 0 24px 24px'}}>
    <Alert type="info" showIcon className="hint" message="这里的数据流向是：浏览器 -> FastAPI 接口 -> SQLAlchemy -> SQLite。" />
    <Table rowKey="id" columns={columns} dataSource={menus} loading={loading} pagination={{ current: search?.page, pageSize: search?.page_size, total, onChange: (page, pageSize) => onSearch({ ...search, page, page_size: pageSize }) }} scroll={{ x: 720 }} />
  </Card>
  )
  }
