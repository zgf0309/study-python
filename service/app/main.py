# asynccontextmanager: 提供异步上下文管理器，用于定义应用启动生命周期。
from contextlib import asynccontextmanager

# FastAPI: 应用主对象。
# Request: 请求对象，用于异常处理函数签名。
# HTTPException: FastAPI 标准 HTTP 异常。
from fastapi import FastAPI, Request, HTTPException

# CORSMiddleware: 处理浏览器跨域请求的中间件。
from fastapi.middleware.cors import CORSMiddleware

# RequestValidationError: 请求参数校验异常。
from fastapi.exceptions import RequestValidationError

# inspect: 检查数据库中现有表和字段结构。
# text: 执行原生 SQL 语句。
from sqlalchemy import inspect, text

# crud: 提供初始化种子数据的 CRUD 方法集合。
from . import crud

# Base: ORM 模型元数据基类，用于创建表结构。
# SessionLocal: 数据库会话工厂，用于创建短生命周期会话。
# engine: 数据库引擎对象，负责连接数据库。
from .database import Base, SessionLocal, engine

# api_response: 统一的 API 响应包装方法。
from .response import api_response

# register_routers: 统一注册所有 API 路由。
from .routes import register_routers


def initialize_database() -> None:
    # 启动时创建表结构，并补充初始化基础数据。
    Base.metadata.create_all(bind=engine)
@asynccontextmanager
async def lifespan(_: FastAPI):
    # 在应用生命周期开始时执行数据库初始化。
    initialize_database()
    yield


# 创建 FastAPI 应用实例，并绑定启动生命周期处理逻辑。
app = FastAPI(lifespan=lifespan)


@app.exception_handler(HTTPException)
async def handle_http_exception(_: Request, exc: HTTPException):
    message = exc.detail if isinstance(exc.detail, str) else '请求处理失败。'
    return api_response(code=exc.status_code, data=None, message=message)


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(_: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else None
    message = first_error.get('msg', '请求参数校验失败。') if first_error else '请求参数校验失败。'
    return api_response(code=422, data=None, message=message)


@app.exception_handler(Exception)
async def handle_unexpected_exception(_: Request, __: Exception):
    return api_response(code=500, data=None, message='服务器内部错误，请稍后重试。')


app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:5173', 'http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
register_routers(app)


if __name__ == '__main__':
    # 本地直接运行当前模块时，使用 uvicorn 启动开发服务。
    import uvicorn

    uvicorn.run('app.main:app', host='127.0.0.1', port=8090, reload=True)
