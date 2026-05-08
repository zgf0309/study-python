# os: 用于读取环境变量中的数据库配置。
# 中文注释：导入当前文件需要使用的 Python 模块。
import os
# Generator: 表示 yield 数据库会话的生成器返回类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from collections.abc import Generator
# Path: 用于拼接和定位项目中的文件路径。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from pathlib import Path

# load_dotenv: 加载 .env 文件中的环境变量配置。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from dotenv import load_dotenv
# create_engine: 创建数据库引擎，负责底层连接管理。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import create_engine
# DeclarativeBase: 作为所有 ORM 模型的声明式基类。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.orm import DeclarativeBase
# Session: 表示一次具体的数据库会话类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.orm import Session
# sessionmaker: 用于生成数据库会话工厂 SessionLocal。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.orm import sessionmaker

# 中文注释：设置变量或字段 BASE_DIR 的值，供后续逻辑使用。
BASE_DIR = Path(__file__).resolve().parent.parent
# 中文注释：设置变量或字段 DATABASE_FILE 的值，供后续逻辑使用。
DATABASE_FILE = BASE_DIR / 'app.db'
# 中文注释：设置变量或字段 DEFAULT_SQLITE_URL 的值，供后续逻辑使用。
DEFAULT_SQLITE_URL = f"sqlite:///{DATABASE_FILE}"

# 中文注释：调用函数或方法，执行对应的业务处理。
load_dotenv(BASE_DIR / '.env')

# 中文注释：设置变量或字段 DATABASE_URL 的值，供后续逻辑使用。
DATABASE_URL = os.getenv('DATABASE_URL', DEFAULT_SQLITE_URL)

# 中文注释：设置字典、响应体或配置项中的一个字段。
engine_options: dict[str, object] = {}
# 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
if DATABASE_URL.startswith('sqlite'):
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    engine_options['connect_args'] = {'check_same_thread': False}

# 中文注释：设置变量或字段 engine 的值，供后续逻辑使用。
engine = create_engine(DATABASE_URL, **engine_options)
# 中文注释：设置变量或字段 SessionLocal 的值，供后续逻辑使用。
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# 中文注释：定义 Base 类，用于组织相关数据或业务逻辑。
class Base(DeclarativeBase):
    # 所有 ORM 模型的公共基类。
    # 中文注释：占位语句，表示这里暂时不需要执行任何操作。
    pass


# 中文注释：定义函数 get_database_label，封装一段可复用的业务逻辑。
def get_database_label() -> str:
    # 将数据库后端名称转换为更易读的展示文本。
    # 中文注释：设置变量或字段 backend_name 的值，供后续逻辑使用。
    backend_name = engine.url.get_backend_name()
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if backend_name == 'sqlite':
        # 中文注释：返回当前函数处理后的结果。
        return 'SQLite'
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if backend_name == 'mysql':
        # 中文注释：返回当前函数处理后的结果。
        return 'MySQL'
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if backend_name == 'postgresql':
        # 中文注释：返回当前函数处理后的结果。
        return 'PostgreSQL'
    # 中文注释：返回当前函数处理后的结果。
    return backend_name


# 中文注释：定义函数 get_db，封装一段可复用的业务逻辑。
def get_db() -> Generator[Session, None, None]:
    # 为 FastAPI 路由提供数据库会话，并在请求结束后关闭连接。
    # 中文注释：设置变量或字段 db 的值，供后续逻辑使用。
    db = SessionLocal()
    # 中文注释：开始执行可能抛出异常的代码块。
    try:
        # 中文注释：生成一段结果并返回给调用方，同时保留后续继续执行的状态。
        yield db
    # 中文注释：无论是否发生异常，都会执行这里的收尾逻辑。
    finally:
        # 中文注释：调用函数或方法，执行对应的业务处理。
        db.close()
