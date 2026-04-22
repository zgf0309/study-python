from fastapi import APIRouter
from sqlalchemy import text

from .. import schemas
from ..database import SessionLocal, get_database_label

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
    return payload.to_dict()
