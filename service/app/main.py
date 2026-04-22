from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from . import crud
from .database import Base, SessionLocal, engine
from .routes import register_routers


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_menu_table_schema()

    with SessionLocal() as db:
        crud.seed_users(db)
        crud.seed_menus(db)


def ensure_menu_table_schema() -> None:
    inspector = inspect(engine)
    if 'menus' not in inspector.get_table_names():
        return

    existing_columns = {column['name'] for column in inspector.get_columns('menus')}
    missing_columns = [name for name in ('user_id', 'icon', 'sort', 'status') if name not in existing_columns]
    if not missing_columns:
        return

    backend = engine.url.get_backend_name()
    statements: list[str] = []
    for column in missing_columns:
        if column == 'user_id':
            column_type = 'INTEGER' if backend in ('sqlite', 'postgresql') else 'INT'
            nullable_clause = ''
            default_clause = ''
        elif column == 'icon':
            column_type = 'VARCHAR(100)'
            nullable_clause = 'NOT NULL'
            default_clause = "DEFAULT 'appstore'"
        elif column == 'sort':
            column_type = 'INTEGER' if backend in ('sqlite', 'postgresql') else 'INT'
            nullable_clause = 'NOT NULL'
            default_clause = 'DEFAULT 0'
        else:
            column_type = 'VARCHAR(20)'
            nullable_clause = 'NOT NULL'
            default_clause = "DEFAULT 'enabled'"

        statement = f'ALTER TABLE menus ADD COLUMN {column} {column_type}'
        if nullable_clause:
            statement = f'{statement} {nullable_clause}'
        if default_clause:
            statement = f'{statement} {default_clause}'
        statements.append(statement)

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:5173', 'http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
register_routers(app)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('app.main:app', host='127.0.0.1', port=8090, reload=True)
