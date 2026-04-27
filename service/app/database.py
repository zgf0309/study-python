# os: 用于读取环境变量中的数据库配置。
import os
# Generator: 表示 yield 数据库会话的生成器返回类型。
from collections.abc import Generator
# Path: 用于拼接和定位项目中的文件路径。
from pathlib import Path

# load_dotenv: 加载 .env 文件中的环境变量配置。
from dotenv import load_dotenv
# create_engine: 创建数据库引擎，负责底层连接管理。
from sqlalchemy import create_engine
# DeclarativeBase: 作为所有 ORM 模型的声明式基类。
from sqlalchemy.orm import DeclarativeBase
# Session: 表示一次具体的数据库会话类型。
from sqlalchemy.orm import Session
# sessionmaker: 用于生成数据库会话工厂 SessionLocal。
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_FILE = BASE_DIR / 'app.db'
DEFAULT_SQLITE_URL = f"sqlite:///{DATABASE_FILE}"

load_dotenv(BASE_DIR / '.env')

DATABASE_URL = os.getenv('DATABASE_URL', DEFAULT_SQLITE_URL)

engine_options: dict[str, object] = {}
if DATABASE_URL.startswith('sqlite'):
    engine_options['connect_args'] = {'check_same_thread': False}

engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    # 所有 ORM 模型的公共基类。
    pass


def get_database_label() -> str:
    # 将数据库后端名称转换为更易读的展示文本。
    backend_name = engine.url.get_backend_name()
    if backend_name == 'sqlite':
        return 'SQLite'
    if backend_name == 'mysql':
        return 'MySQL'
    if backend_name == 'postgresql':
        return 'PostgreSQL'
    return backend_name


def get_db() -> Generator[Session, None, None]:
    # 为 FastAPI 路由提供数据库会话，并在请求结束后关闭连接。
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
