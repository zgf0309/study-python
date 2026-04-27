import { Card, Col, Row, Space, Statistic, Tag, Timeline, Typography } from 'antd'

import type { HealthResponse } from '../api'

type HealthOverviewProps = {
health: HealthResponse | null
loading: boolean
}

export function HealthOverview({ health, loading }: HealthOverviewProps) {
return (
<>
  <section className="hero-panel">
    <Space direction="vertical" size={18} className="hero-copy">
      <Tag color="cyan" bordered={false} className="eyebrow">
        React + Ant Design + FastAPI + SQLite
      </Tag>
      <Typography.Title level={1}>本地前后端联调示例</Typography.Title>
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
      <Timeline items={[ { color: health ? 'blue' : 'gray' , children: '前端页面加载后，Axios 调用 /api/health。' , }, { color:
        health?.status==='ok' ? 'green' : 'gray' , children: health?.frontend_to_backend || '等待后端响应。' , }, { color:
        health?.database==='connected' ? 'green' : 'gray' , children: health?.backend_to_database || '等待数据库检查结果。' , },
        ]} />
    </Card>
  </section>

  <Row gutter={[16, 16]}>
    <Col xs={24} md={8}>
    <Card loading={loading}>
      <Statistic title="后端服务" value={health?.service || 'service' } />
    </Card>
    </Col>
    <Col xs={24} md={8}>
    <Card loading={loading}>
      <Statistic title="接口状态" value={health?.status || 'unknown' } />
    </Card>
    </Col>
    <Col xs={24} md={8}>
    <Card loading={loading}>
      <Statistic title="数据库状态" value={health?.database || 'unknown' } />
    </Card>
    </Col>
  </Row>
</>
)
}