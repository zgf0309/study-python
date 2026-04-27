import { Button, Card, Divider, Flex, Form, Input, Switch ,Typography } from 'antd'
export function RoleEditorCard({
  mode,
  form,
  submitting,
  onSubmit,
  onCancelEdit,
  }) {
  const isEditing = mode === 'edit'

  return (
  <Card title={isEditing ? '编辑角色' : '新增角色' }>
    <Typography.Paragraph className="form-copy">
      提交表单后，前端会调用 POST /api/roles，后端校验并写入本地数据库，再把新记录回传给前端更新列表。
    </Typography.Paragraph>
    <Form form={form} layout="vertical" onFinish={onSubmit}>
      <Form.Item label="ID" name="id" hidden>
        <Input placeholder="例如：1" />
      </Form.Item>
      <Form.Item label="用户ID" name="user_id" hidden>
        <Input placeholder="例如：1" />
      </Form.Item>
      <Form.Item label="角色名称" name="name" rules={[{ required: true, message: '请输入角色名称' }]}>
        <Input placeholder="例如：管理员" />
      </Form.Item>
      <Form.Item label="排序" name="sort" rules={[{ required: true, message: '请输入排序' }]}>
        <Input placeholder="例如：1" />
      </Form.Item>
      <Form.Item label="描述" name="description" rules={[{ required: true, message: '请输入描述' }]}>
        <Input.TextArea autoSize={{ minRows: 2, maxRows: 4 }} placeholder="例如：具有全部权限的角色" />
      </Form.Item>
      <Form.Item label="状态" name="status" valuePropName="checked" rules={[{ required: true, message: '请输入状态' }]}>
        <Switch checkedChildren="开启" unCheckedChildren="关闭" />
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