import { Button, Card, Divider, Flex, Form, Input, Typography } from 'antd'
import type { FormInstance } from 'antd'

import type { CreateUserPayload } from '../services/api'

type UserEditorCardProps = {
mode: 'create' | 'edit'
form: FormInstance<CreateUserPayload>
  submitting: boolean
  onSubmit: (values: CreateUserPayload) => void
  onCancelEdit: () => void
  }

export function UserEditorCard({
  mode,
  form,
  submitting,
  onSubmit,
  onCancelEdit,
  }: UserEditorCardProps) {
  const isEditing = mode === 'edit'

  return (
  <Card title={isEditing ? '编辑用户' : '新增用户' }>
    <Typography.Paragraph className="form-copy">
      提交表单后，前端会调用 POST /api/users，后端校验并写入本地数据库，再把新记录回传给前端更新列表。
    </Typography.Paragraph>
    <Form form={form} layout="vertical" onFinish={onSubmit}>
      <Form.Item label="ID" name="id" hidden>
        <Input placeholder="例如：1" />
      </Form.Item>
      <Form.Item label="姓名" name="name" rules={[{ required: true, message: '请输入姓名' }]}>
        <Input placeholder="例如：张三" />
      </Form.Item>
      <Form.Item label="邮箱" name="email" rules={[ { required: true, message: '请输入邮箱' }, { type: 'email' ,
        message: '邮箱格式不正确' }, ]}>
        <Input placeholder="name@example.com" />
      </Form.Item>
      <Form.Item label="角色" name="role" initialValue="viewer" rules={[{ required: true, message: '请输入角色' }]}>
        <Input placeholder="viewer / admin" />
      </Form.Item>
      {isEditing ? (
      <Flex gap={10} justify="center">
        <Button type="primary" htmlType="submit" loading={submitting} block>
          修改本地数据库
        </Button>
        <Button htmlType="button" onClick={onCancelEdit}>
          取消
        </Button>
      </Flex>
      ) : (
      <Button type="primary" htmlType="submit" loading={submitting} block>
        写入本地数据库
      </Button>
      )}
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
  </Card>
  )
  }