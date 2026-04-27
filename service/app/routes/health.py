# APIRouter: 创建健康检查接口的路由对象。
from fastapi import APIRouter
# text: 执行原生 SQL，用于数据库连通性探活。
from sqlalchemy import text

# schemas: 健康检查接口使用的响应数据结构模块。
from .. import schemas

# SessionLocal: 数据库会话工厂，用于执行探活查询。
# get_database_label: 返回当前数据库类型的展示名称。
from ..database import SessionLocal, get_database_label

# api_response: 统一包装 API 返回结构。
from ..response import api_response

health_router = APIRouter()

@health_router.get('/health')
def read_health():
    with SessionLocal() as db:
        db.execute(text('SELECT 1'))

    database_label = get_database_label()
    payload = schemas.HealthResponse(
        service='FastAPI service',
        status='ok',
        database=f'connected ({database_label})',
        frontend_to_backend='前端通过 HTTP 请求访问 FastAPI /api 接口。',
        backend_to_database=f'FastAPI 通过 SQLAlchemy Session 连接本地 {database_label} 数据库。',
    )
    return api_response(data=payload.to_dict())
