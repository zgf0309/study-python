# APIRouter: 创建健康检查接口的路由对象。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi import APIRouter
# text: 执行原生 SQL，用于数据库连通性探活。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import text

# schemas: 健康检查接口使用的响应数据结构模块。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .. import schemas

# SessionLocal: 数据库会话工厂，用于执行探活查询。
# get_database_label: 返回当前数据库类型的展示名称。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..database import SessionLocal, get_database_label

# api_response: 统一包装 API 返回结构。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..response import api_response

# 中文注释：设置变量或字段 health_router 的值，供后续逻辑使用。
health_router = APIRouter()

# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@health_router.get('/health')
# 中文注释：定义函数 read_health，封装一段可复用的业务逻辑。
def read_health():
    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：调用函数或方法，执行对应的业务处理。
        db.execute(text('SELECT 1'))

    # 中文注释：设置变量或字段 database_label 的值，供后续逻辑使用。
    database_label = get_database_label()
    # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
    payload = schemas.HealthResponse(
        # 中文注释：设置变量或字段 service 的值，供后续逻辑使用。
        service='FastAPI service',
        # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
        status='ok',
        # 中文注释：设置变量或字段 database 的值，供后续逻辑使用。
        database=f'connected ({database_label})',
        # 中文注释：设置变量或字段 frontend_to_backend 的值，供后续逻辑使用。
        frontend_to_backend='前端通过 HTTP 请求访问 FastAPI /api 接口。',
        # 中文注释：设置变量或字段 backend_to_database 的值，供后续逻辑使用。
        backend_to_database=f'FastAPI 通过 SQLAlchemy Session 连接本地 {database_label} 数据库。',
    # 中文注释：结束当前多行数据结构或多行参数。
    )
    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=payload.to_dict())
