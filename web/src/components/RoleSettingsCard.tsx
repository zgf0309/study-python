import { CloseOutlined } from '@ant-design/icons'
import { Tag, Card, Flex, Table, Button } from 'antd'
import type { ColumnsType } from 'antd/es/table'

import type { RolesRecord } from '../services/api'
import { formatDateTime } from '../utils/format'
import { useState } from 'react'
import type { TableRowSelection } from 'antd/es/table/interface'

type RoleSettingsCardProps = {
  roles: RolesRecord[]
  loading: boolean
  onBack: () => void
  handleSubmit: (keys: React.Key[]) => void
  }

  export function RoleSettingsCard({
  roles,
  loading,
  onBack,
  handleSubmit,
  }: RoleSettingsCardProps) {
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
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
    ]

    const rowSelection: TableRowSelection<RolesRecord> = {
      selectedRowKeys,
      onChange: (newSelectedRowKeys: React.Key[]) => {
        setSelectedRowKeys(newSelectedRowKeys);
      },
    };
    return (
    <Card title={ <Flex justify="space-between" align="center">
      <h5 className="panel-title">配置角色</h5>
      <CloseOutlined onClick={onBack} />
      </Flex>
      }
      >
      <Table rowKey="id" columns={columns} dataSource={roles} loading={loading} rowSelection={rowSelection} pagination={false} scroll={{
        x: 720, y: 520}} />
      <Flex gap={10} justify="end" style={{ marginTop: 16 }}>
        <Button type="primary" onClick={() => handleSubmit(selectedRowKeys)}>配置权限</Button>
        <Button onClick={onBack}>关闭</Button>
      </Flex>
    </Card>
    )
    }