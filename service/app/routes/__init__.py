# FastAPI: FastAPI 应用类型，用于给注册函数添加参数类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi import FastAPI

# files_router: 文件上传路由实例。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .files import files_router

# health_router: 健康检查路由实例。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .health import health_router
# menus_router: 菜单模块的路由实例。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .menus import menus_router
# roles_router: 角色模块的路由实例。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .roles import roles_router
# users_router: 用户模块的路由实例。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .users import users_router
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .model_configs import model_configs_router


# 中文注释：定义函数 register_routers，封装一段可复用的业务逻辑。
def register_routers(app: FastAPI) -> None:
    # 中文注释：设置变量或字段 app.include_router(files_router, prefix 的值，供后续逻辑使用。
    app.include_router(files_router, prefix='/api')
    # 中文注释：设置变量或字段 app.include_router(health_router, prefix 的值，供后续逻辑使用。
    app.include_router(health_router, prefix='/api')
    # 中文注释：设置变量或字段 app.include_router(users_router, prefix 的值，供后续逻辑使用。
    app.include_router(users_router, prefix='/api')
    # 中文注释：设置变量或字段 app.include_router(roles_router, prefix 的值，供后续逻辑使用。
    app.include_router(roles_router, prefix='/api')
    # 中文注释：设置变量或字段 app.include_router(menus_router, prefix 的值，供后续逻辑使用。
    app.include_router(menus_router, prefix='/api')
    # 中文注释：设置变量或字段 app.include_router(model_configs_router, prefix 的值，供后续逻辑使用。
    app.include_router(model_configs_router, prefix='/api')
