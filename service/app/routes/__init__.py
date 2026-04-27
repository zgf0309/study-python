# FastAPI: FastAPI 应用类型，用于给注册函数添加参数类型。
from fastapi import FastAPI

# health_router: 健康检查路由实例。
from .health import health_router
# menus_router: 菜单模块的路由实例。
from .menus import menus_router
# roles_router: 角色模块的路由实例。
from .roles import roles_router
# users_router: 用户模块的路由实例。
from .users import users_router


def register_routers(app: FastAPI) -> None:
    app.include_router(health_router, prefix='/api')
    app.include_router(users_router, prefix='/api')
    app.include_router(roles_router, prefix='/api')
    app.include_router(menus_router, prefix='/api')
    app.include_router(roles_router, prefix='/api')
