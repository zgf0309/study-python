import { CloseOutlined } from '@ant-design/icons'
import { Button, Card, Flex, Table } from 'antd'
import type { ColumnsType } from 'antd/es/table'

import type { MenusRecord } from '../services/api'
import { formatDateTime } from '../utils/format'
import { useState } from 'react'
import type { TableRowSelection } from 'antd/es/table/interface'
import type { RolesRecord } from '../services/api'

type MenuSettingsCardProps = {
  menus: MenusRecord[]
  loading: boolean
  onBack: () => void
  handleSubmit: (keys: React.Key[]) => void
  }

  export function MenuSettingsCard({
  menus,
  loading,
  onBack,
  handleSubmit,
  }: MenuSettingsCardProps) {
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
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
    ]

    const rowSelection: TableRowSelection<MenusRecord> = {
      selectedRowKeys,
      onChange: (newSelectedRowKeys: React.Key[]) => {
        setSelectedRowKeys(newSelectedRowKeys);
      },
    };
    
    return (
    <Card title={ <Flex justify="space-between" align="center">
      <h5 className="panel-title">配置菜单</h5>
      <CloseOutlined onClick={onBack} />
      </Flex>
      }
      >
      <Table rowKey="id" columns={columns} dataSource={menus} loading={loading} rowSelection={rowSelection} pagination={false} scroll={{
        x: 720, y: 520}} />
      <Flex gap={10} justify="end" style={{ marginTop: 16 }}>
        <Button type="primary" onClick={() => handleSubmit(selectedRowKeys)}>配置权限</Button>
        <Button onClick={onBack}>关闭</Button>
      </Flex>
    </Card>
    )
    }