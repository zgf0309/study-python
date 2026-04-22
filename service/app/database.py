import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

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
    pass


def get_database_label() -> str:
    backend_name = engine.url.get_backend_name()
    if backend_name == 'sqlite':
        return 'SQLite'
    if backend_name == 'mysql':
        return 'MySQL'
    if backend_name == 'postgresql':
        return 'PostgreSQL'
    return backend_name


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
