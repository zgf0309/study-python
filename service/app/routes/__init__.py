from fastapi import FastAPI

from .health import health_router
from .menus import menus_router
from .users import users_router


def register_routers(app: FastAPI) -> None:
    app.include_router(health_router, prefix='/api')
    app.include_router(users_router, prefix='/api')
    app.include_router(menus_router, prefix='/api')
