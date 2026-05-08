# asynccontextmanager: 提供异步上下文管理器，用于定义应用启动生命周期。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from contextlib import asynccontextmanager

# FastAPI: 应用主对象。
# Request: 请求对象，用于异常处理函数签名。
# HTTPException: FastAPI 标准 HTTP 异常。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi import FastAPI, Request, HTTPException

# CORSMiddleware: 处理浏览器跨域请求的中间件。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi.middleware.cors import CORSMiddleware

# RequestValidationError: 请求参数校验异常。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi.exceptions import RequestValidationError

# inspect: 检查数据库中现有表和字段结构。
# text: 执行原生 SQL 语句。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import inspect, text

# crud: 提供初始化种子数据的 CRUD 方法集合。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from . import crud

# Base: ORM 模型元数据基类，用于创建表结构。
# SessionLocal: 数据库会话工厂，用于创建短生命周期会话。
# engine: 数据库引擎对象，负责连接数据库。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .database import Base, SessionLocal, engine

# api_response: 统一的 API 响应包装方法。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .response import api_response

# register_routers: 统一注册所有 API 路由。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .routes import register_routers


# 中文注释：定义函数 initialize_database，封装一段可复用的业务逻辑。
def initialize_database() -> None:
    # 启动时创建表结构，并补充初始化基础数据。
    # 中文注释：设置变量或字段 Base.metadata.create_all(bind 的值，供后续逻辑使用。
    Base.metadata.create_all(bind=engine)
    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：调用函数或方法，执行对应的业务处理。
        crud.ensure_builtin_model_configs(db)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@asynccontextmanager
# 中文注释：定义异步函数 lifespan，用于处理异步业务流程。
async def lifespan(_: FastAPI):
    # 在应用生命周期开始时执行数据库初始化。
    # 中文注释：调用函数或方法，执行对应的业务处理。
    initialize_database()
    # 中文注释：执行当前代码行对应的业务逻辑。
    yield


# 创建 FastAPI 应用实例，并绑定启动生命周期处理逻辑。
# 中文注释：设置变量或字段 app 的值，供后续逻辑使用。
app = FastAPI(lifespan=lifespan)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@app.exception_handler(HTTPException)
# 中文注释：定义异步函数 handle_http_exception，用于处理异步业务流程。
async def handle_http_exception(_: Request, exc: HTTPException):
    # 中文注释：设置变量或字段 message 的值，供后续逻辑使用。
    message = exc.detail if isinstance(exc.detail, str) else '请求处理失败。'
    # 中文注释：返回当前函数处理后的结果。
    return api_response(code=exc.status_code, data=None, message=message)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@app.exception_handler(RequestValidationError)
# 中文注释：定义异步函数 handle_validation_exception，用于处理异步业务流程。
async def handle_validation_exception(_: Request, exc: RequestValidationError):
    # 中文注释：设置变量或字段 first_error 的值，供后续逻辑使用。
    first_error = exc.errors()[0] if exc.errors() else None
    # 中文注释：设置变量或字段 message 的值，供后续逻辑使用。
    message = first_error.get('msg', '请求参数校验失败。') if first_error else '请求参数校验失败。'
    # 中文注释：返回当前函数处理后的结果。
    return api_response(code=422, data=None, message=message)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@app.exception_handler(Exception)
# 中文注释：定义异步函数 handle_unexpected_exception，用于处理异步业务流程。
async def handle_unexpected_exception(_: Request, __: Exception):
    # 中文注释：返回当前函数处理后的结果。
    return api_response(code=500, data=None, message='服务器内部错误，请稍后重试。')


# 中文注释：执行当前代码行对应的业务逻辑。
app.add_middleware(
    # 中文注释：执行当前代码行对应的业务逻辑。
    CORSMiddleware,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    allow_origins=['http://127.0.0.1:5173', 'http://localhost:5173'],
    # 中文注释：设置变量或字段 allow_credentials 的值，供后续逻辑使用。
    allow_credentials=True,
    # 中文注释：设置变量或字段 allow_methods 的值，供后续逻辑使用。
    allow_methods=['*'],
    # 中文注释：设置变量或字段 allow_headers 的值，供后续逻辑使用。
    allow_headers=['*'],
# 中文注释：结束当前多行数据结构或多行参数。
)
# 中文注释：调用函数或方法，执行对应的业务处理。
register_routers(app)


# 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
if __name__ == '__main__':
    # 本地直接运行当前模块时，使用 uvicorn 启动开发服务。
    # 中文注释：导入当前文件需要使用的 Python 模块。
    import uvicorn

    # 中文注释：设置变量或字段 uvicorn.run('app.main:app', host 的值，供后续逻辑使用。
    uvicorn.run('app.main:app', host='127.0.0.1', port=8090, reload=True)
