# 后端接口文档

本文档描述当前 FastAPI 后端对外提供的接口。开发环境中前端通过 Vite 代理访问 `/api`，后端实际服务地址通常为：

```text
http://127.0.0.1:8090/api
```

## 1. 通用说明

### 1.1 普通 JSON 接口统一响应结构

除流式接口 `/api/chat/stream` 外，普通接口统一返回：

```json
{
  "code": 200,
  "data": {
    "data": {},
    "total": 0
  },
  "message": ""
}
```

说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `code` | number | 业务状态码，通常与 HTTP 状态码一致 |
| `data.data` | any | 实际业务数据 |
| `data.total` | number | 分页列表总数，部分列表接口传 `page >= 1` 时返回 |
| `message` | string | 提示信息或错误信息 |

### 1.2 常见错误响应

```json
{
  "code": 400,
  "data": {
    "data": null
  },
  "message": "请求参数错误。"
}
```

常见状态码：

| 状态码 | 说明 |
| --- | --- |
| `200` | 请求成功 |
| `201` | 创建成功 |
| `400` | 请求参数错误 |
| `404` | 数据不存在 |
| `422` | 请求参数校验失败 |
| `500` | 服务器内部错误 |
| `502` | 上游模型服务调用失败 |

---

## 2. 健康检查

### 2.1 查询服务健康状态

```http
GET /api/health
```

响应示例：

```json
{
  "code": 200,
  "data": {
    "data": {
      "service": "FastAPI service",
      "status": "ok",
      "database": "connected (SQLite)",
      "frontend_to_backend": "前端通过 HTTP 请求访问 FastAPI /api 接口。",
      "backend_to_database": "FastAPI 通过 SQLAlchemy Session 连接本地 SQLite 数据库。"
    }
  },
  "message": ""
}
```

---

## 3. 用户接口

### 3.1 查询用户列表

```http
GET /api/users
```

Query 参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | string | 否 | `""` | 按用户姓名模糊搜索 |
| `page` | number | 否 | `0` | 页码；`page >= 1` 时返回 `total` |
| `page_size` | number | 否 | `10` | 每页条数，范围 1-100 |

示例：

```http
GET /api/users?name=张&page=1&page_size=10
```

响应数据：

```json
{
  "code": 200,
  "data": {
    "data": [
      {
        "id": 1,
        "name": "张三",
        "email": "zhangsan@example.com",
        "role": "viewer",
        "role_ids": [1, 2],
        "created_at": "2026-05-08T10:00:00"
      }
    ],
    "total": 1
  },
  "message": ""
}
```

### 3.2 新增用户

```http
POST /api/users
Content-Type: application/json
```

请求体：

```json
{
  "name": "张三",
  "email": "zhangsan@example.com",
  "role": "viewer"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | string | 是 | 用户姓名 |
| `email` | string | 是 | 邮箱，必须包含 `@` |
| `role` | string | 否 | `viewer`、`editor`、`admin` |

响应：

```json
{
  "code": 201,
  "data": {
    "data": {
      "id": 1,
      "name": "张三",
      "email": "zhangsan@example.com",
      "role": "viewer",
      "role_ids": [],
      "created_at": "2026-05-08T10:00:00"
    }
  },
  "message": "用户已创建。"
}
```

### 3.3 更新用户

```http
PUT /api/users
Content-Type: application/json
```

请求体：

```json
{
  "id": 1,
  "name": "张三",
  "email": "zhangsan@example.com",
  "role": "editor"
}
```

响应 message：

```text
用户已更新。
```

### 3.4 删除用户，请求体方式

```http
DELETE /api/users
Content-Type: application/json
```

请求体：

```json
{
  "id": 1
}
```

### 3.5 删除用户，路径参数方式

```http
DELETE /api/users/{user_id}
```

示例：

```http
DELETE /api/users/1
```

响应 message：

```text
用户已删除。
```

### 3.6 为用户配置角色

```http
POST /api/users/relation-roles
Content-Type: application/json
```

请求体：

```json
{
  "id": 1,
  "role_ids": [1, 2, 3]
}
```

说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | number | 是 | 用户 ID |
| `role_ids` | number[] | 是 | 角色 ID 列表 |

响应 message：

```text
用户权限已更新。
```

### 3.7 查询用户已关联角色

```http
GET /api/users/relation-roles?id=1
```

响应数据：

```json
{
  "code": 200,
  "data": {
    "data": [
      {
        "id": 1,
        "name": "管理员",
        "description": "系统管理员",
        "sort": 1,
        "status": "enabled",
        "user_ids": [1],
        "created_at": "2026-05-08T10:00:00"
      }
    ]
  },
  "message": ""
}
```

---

## 4. 角色接口

### 4.1 查询角色列表

```http
GET /api/roles
```

Query 参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | string | 否 | `""` | 按角色名称模糊搜索 |
| `page` | number | 否 | `0` | 页码；`page >= 1` 时返回 `total` |
| `page_size` | number | 否 | `10` | 每页条数，范围 1-100 |

### 4.2 新增角色

```http
POST /api/roles
Content-Type: application/json
```

请求体：

```json
{
  "name": "管理员",
  "description": "系统管理员",
  "sort": 1,
  "status": "enabled"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | string | 是 | 角色名称 |
| `description` | string | 否 | 角色描述 |
| `sort` | number | 否 | 排序值 |
| `status` | string | 否 | `enabled` 或 `disabled` |

### 4.3 更新角色

```http
PUT /api/roles
Content-Type: application/json
```

请求体：

```json
{
  "id": 1,
  "name": "管理员",
  "description": "系统管理员",
  "sort": 1,
  "status": "enabled"
}
```

### 4.4 删除角色

```http
DELETE /api/roles/{role_id}
```

示例：

```http
DELETE /api/roles/1
```

### 4.5 为角色配置菜单

```http
POST /api/roles/relation-menus
Content-Type: application/json
```

请求体：

```json
{
  "id": 1,
  "menu_ids": [1, 2, 3]
}
```

### 4.6 查询角色已关联菜单

```http
GET /api/roles/relation-menus?id=1
```

响应数据为菜单列表。

---

## 5. 菜单接口

### 5.1 查询菜单列表

```http
GET /api/menus
```

Query 参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `name` | string | 否 | `""` | 按菜单名称模糊搜索 |
| `page` | number | 否 | `0` | 页码；`page >= 1` 时返回 `total` |
| `page_size` | number | 否 | `10` | 每页条数，范围 1-100 |

### 5.2 查询单个菜单

```http
GET /api/menus/{menu_id}
```

示例：

```http
GET /api/menus/1
```

### 5.3 新增菜单

```http
POST /api/menus
Content-Type: application/json
```

请求体：

```json
{
  "name": "首页",
  "path": "/home",
  "icon": "home",
  "sort": 1,
  "status": "enabled"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | string | 是 | 菜单名称 |
| `path` | string | 是 | 菜单路径，必须以 `/` 开头 |
| `icon` | string | 否 | 图标名称，默认 `appstore` |
| `sort` | number | 否 | 排序值 |
| `status` | string | 否 | `enabled` 或 `disabled` |

### 5.4 更新菜单

```http
PUT /api/menus
Content-Type: application/json
```

请求体：

```json
{
  "id": 1,
  "name": "首页",
  "path": "/home",
  "icon": "home",
  "sort": 1,
  "status": "enabled"
}
```

### 5.5 删除菜单

```http
DELETE /api/menus/{menu_id}
```

示例：

```http
DELETE /api/menus/1
```

---

## 6. 模型配置接口

### 6.1 查询模型列表

```http
GET /api/models
```

响应数据：

```json
{
  "code": 200,
  "data": {
    "data": [
      {
        "id": 1,
        "name": "jusure-llm 默认模型",
        "base_url": "http://114.242.210.44:8000/v1",
        "model_name": "jusure-llm",
        "provider": "openai-compatible",
        "is_default": true,
        "status": "enabled",
        "created_at": "2026-05-08T10:00:00"
      },
      {
        "id": 2,
        "name": "Qwen3-Embedding-4B 向量模型",
        "base_url": "http://114.242.210.44:6300/v1/embeddings",
        "model_name": "qwen3-embed-4b",
        "provider": "openai-compatible-embedding",
        "is_default": false,
        "status": "enabled",
        "created_at": "2026-05-08T10:00:00"
      }
    ]
  },
  "message": ""
}
```

注意：接口不会返回 `api_key`。

### 6.2 新增模型配置

```http
POST /api/models
Content-Type: application/json
```

请求体：

```json
{
  "name": "本地模型",
  "base_url": "http://127.0.0.1:8000/v1",
  "model_name": "local-llm",
  "api_key": "sk-xxx",
  "provider": "openai-compatible",
  "is_default": false,
  "status": "enabled"
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | string | 是 | 页面展示名称 |
| `base_url` | string | 是 | 模型服务地址，必须以 `http://` 或 `https://` 开头 |
| `model_name` | string | 是 | 模型服务实际模型名 |
| `api_key` | string | 是 | 模型服务密钥 |
| `provider` | string | 否 | `openai-compatible` 或 `openai-compatible-embedding` |
| `is_default` | boolean | 否 | 是否默认对话模型；向量模型不能设置为默认对话模型 |
| `status` | string | 否 | `enabled` 或 `disabled` |

---

## 7. 大模型对话接口

### 7.1 流式对话

```http
POST /api/chat/stream
Content-Type: application/json
Accept: text/event-stream
```

请求体：

```json
{
  "model_id": 1,
  "messages": [
    {
      "role": "system",
      "content": "你是一个中文助手。"
    },
    {
      "role": "user",
      "content": "你好，请介绍一下你自己。"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model_id` | number | 否 | 对话模型 ID；不传时使用默认对话模型 |
| `messages` | array | 是 | 消息列表 |
| `messages[].role` | string | 是 | `system`、`user`、`assistant` |
| `messages[].content` | string | 是 | 消息内容 |
| `temperature` | number | 否 | 温度参数，默认 `0.7` |
| `max_tokens` | number | 否 | 最大输出 token 数 |

响应类型：

```text
text/event-stream
```

正常流式片段示例：

```text
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1710000000,"model":"jusure-llm","choices":[{"index":0,"delta":{"content":"你好"},"finish_reason":null}]}

```

结束片段：

```text
data: [DONE]

```

错误片段示例：

```text
data: {"id":"chatcmpl-error-xxx","object":"chat.completion.chunk","created":1710000000,"model":"jusure-llm","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":"error"}],"error":{"message":"无法连接模型服务","type":"llm_error"}}

```

curl 测试：

```bash
curl -N \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -X POST http://127.0.0.1:8090/api/chat/stream \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

---

## 8. 向量化接口

### 8.1 单文本或文本数组向量化

```http
POST /api/embeddings
Content-Type: application/json
```

请求体，单文本：

```json
{
  "model_id": 2,
  "input": "需要向量化的文本"
}
```

请求体，文本数组：

```json
{
  "model_id": 2,
  "input": [
    "第一段文本",
    "第二段文本"
  ]
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model_id` | number | 否 | 向量模型 ID；不传时使用第一个启用的向量模型 |
| `input` | string 或 string[] | 是 | 待向量化文本 |

响应数据为上游 Embeddings 接口返回的 JSON，示例：

```json
{
  "code": 200,
  "data": {
    "data": {
      "object": "list",
      "model": "qwen3-embed-4b",
      "data": [
        {
          "object": "embedding",
          "index": 0,
          "embedding": [0.01, 0.02, 0.03]
        }
      ],
      "usage": {
        "prompt_tokens": 10,
        "total_tokens": 10
      }
    }
  },
  "message": ""
}
```

curl 测试：

```bash
curl -X POST http://127.0.0.1:8090/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input":"需要向量化的文本"}'
```

### 8.2 长文本切片后批量向量化

```http
POST /api/embeddings/chunks
Content-Type: application/json
```

请求体：

```json
{
  "model_id": 2,
  "text": "这里是一段较长的文档内容，需要先切片，然后再生成每个切片的向量。",
  "chunk_size": 500,
  "chunk_overlap": 80
}
```

字段说明：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `model_id` | number | 否 | `0` | 向量模型 ID；不传时使用第一个启用的向量模型 |
| `text` | string | 是 | - | 待切片的长文本 |
| `chunk_size` | number | 否 | `500` | 每个切片最大字符数，范围 1-5000 |
| `chunk_overlap` | number | 否 | `80` | 相邻切片重叠字符数，必须小于 `chunk_size` |

切片规则：

```text
step = chunk_size - chunk_overlap
```

例如：

```text
chunk_size = 100
chunk_overlap = 20
step = 80

第 1 段：0 - 100
第 2 段：80 - 180
第 3 段：160 - 260
```

响应示例：

```json
{
  "code": 200,
  "data": {
    "data": {
      "model": "qwen3-embed-4b",
      "chunk_size": 500,
      "chunk_overlap": 80,
      "total_chunks": 2,
      "chunks": [
        {
          "index": 0,
          "content": "第一个切片内容",
          "start": 0,
          "end": 500,
          "length": 500,
          "embedding": [0.01, 0.02, 0.03],
          "embedding_dim": 2560
        },
        {
          "index": 1,
          "content": "第二个切片内容",
          "start": 420,
          "end": 920,
          "length": 500,
          "embedding": [0.04, 0.05, 0.06],
          "embedding_dim": 2560
        }
      ],
      "usage": {
        "prompt_tokens": 100,
        "total_tokens": 100
      }
    }
  },
  "message": ""
}
```

curl 测试：

```bash
curl -X POST http://127.0.0.1:8090/api/embeddings/chunks \
  -H "Content-Type: application/json" \
  -d '{
    "text": "RAG 的流程是先切片，再向量化，再检索，再交给大模型生成答案。",
    "chunk_size": 20,
    "chunk_overlap": 5
  }'
```

---

## 9. 前端接口对应关系

| 前端文件 | 后端接口 |
| --- | --- |
| `web/src/hooks/useHealth.ts` | `GET /api/health` |
| `web/src/hooks/useUsers.ts` | `/api/users`、`/api/users/relation-roles` |
| `web/src/hooks/useRoles.ts` | `/api/roles`、`/api/roles/relation-menus` |
| `web/src/hooks/useMenus.ts` | `/api/menus` |
| `web/src/components/ModelTableCard.tsx` | `GET /api/models`、`POST /api/chat/stream`、`POST /api/embeddings`、`POST /api/embeddings/chunks` |
| `web/src/services/api.ts` | 前端接口统一封装 |

---

## 10. 启动与调试

### 10.1 启动后端

```bash
cd service
uvicorn app.main:app --host 127.0.0.1 --port 8090 --reload
```

### 10.2 启动前端

```bash
cd web
npm run dev
```

### 10.3 访问前端

```text
http://127.0.0.1:5173
```

### 10.4 OpenAPI 文档

FastAPI 默认也提供在线接口文档：

```text
http://127.0.0.1:8090/docs
```
