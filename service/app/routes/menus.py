# traceback: 打印异常堆栈，便于开发时排查错误。
# 中文注释：导入当前文件需要使用的 Python 模块。
import traceback

# Any: 表示请求体中可接收任意值类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from typing import Any

# APIRouter: 创建菜单接口的路由对象。
# Body: 从请求体中读取提交的数据。
# HTTPException: 主动返回 HTTP 错误响应。
# Query: 读取 URL 查询参数。
# status: 提供 HTTP 状态码常量。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi import APIRouter, Body, HTTPException, Query, status

# IntegrityError: 捕获数据库唯一约束等完整性异常。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.exc import IntegrityError

# crud: 提供菜单相关的 CRUD 方法集合。
# schemas: 提供菜单相关的请求与响应数据结构。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .. import crud, schemas

# SessionLocal: 数据库会话工厂，用于处理当前请求的数据库读写。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..database import SessionLocal

# api_response: 统一包装 API 返回结构。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..response import api_response
# clean_string: 统一处理字符串参数，减少每个接口里重复的 str(...).strip()。
# parse_int: 安全转换整数，避免前端传空字符串时接口报 500。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..utils import clean_string, parse_int

# 中文注释：设置变量或字段 menus_router 的值，供后续逻辑使用。
menus_router = APIRouter()


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@menus_router.get('/menus')
# 中文注释：定义函数 read_menus，封装一段可复用的业务逻辑。
def read_menus(
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    name: str = Query(default=''),
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    page: int = Query(default=0),
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    page_size: int = Query(default=10, ge=1, le=100),
# 中文注释：执行当前代码行对应的业务逻辑。
):
    # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
    name = clean_string(name)

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 menus 的值，供后续逻辑使用。
        menus = crud.list_menus(
            # 中文注释：执行当前代码行对应的业务逻辑。
            db,
            # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
            name=name or None,
            # 中文注释：设置变量或字段 page 的值，供后续逻辑使用。
            page=page,
            # 中文注释：设置变量或字段 page_size 的值，供后续逻辑使用。
            page_size=page_size,
        # 中文注释：结束当前多行数据结构或多行参数。
        )
        # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
        payload = [schemas.serialize_menu(menu) for menu in menus]
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        extra = {'total': crud.count_menus(db, name=name or None)} if page >= 1 else {}

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=payload, **extra)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@menus_router.get('/menus/{menu_id}')
# 中文注释：定义函数 read_menu，封装一段可复用的业务逻辑。
def read_menu(menu_id: int):
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if menu_id <= 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='菜单 ID 不存在。')

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 menu 的值，供后续逻辑使用。
        menu = crud.get_menu(db, menu_id)
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if not menu:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='菜单不存在。')
        # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
        response_data = schemas.serialize_menu(menu)

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@menus_router.post('/menus', status_code=status.HTTP_201_CREATED)
# 中文注释：定义函数 add_menu，封装一段可复用的业务逻辑。
def add_menu(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
    name = clean_string(data.get('name'))
    # 中文注释：设置变量或字段 path 的值，供后续逻辑使用。
    path = clean_string(data.get('path'))
    # 中文注释：设置变量或字段 icon 的值，供后续逻辑使用。
    icon = clean_string(data.get('icon'), 'appstore') or 'appstore'
    # 中文注释：设置变量或字段 sort 的值，供后续逻辑使用。
    sort = parse_int(data.get('sort'))
    # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
    status = clean_string(data.get('status'), 'enabled') or 'enabled'
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not name:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='菜单名称不能为空。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not path or not path.startswith('/'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='菜单路径必须以 / 开头。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if status not in ('enabled', 'disabled'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')

    # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
    payload = schemas.MenuCreate(
        # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
        name=name,
        # 中文注释：设置变量或字段 path 的值，供后续逻辑使用。
        path=path,
        # 中文注释：设置变量或字段 icon 的值，供后续逻辑使用。
        icon=icon,
        # 中文注释：设置变量或字段 sort 的值，供后续逻辑使用。
        sort=sort,
        # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
        status=status,
    # 中文注释：结束当前多行数据结构或多行参数。
    )

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：设置变量或字段 menu 的值，供后续逻辑使用。
            menu = crud.create_menu(db, payload)
            # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
            response_data = schemas.serialize_menu(menu)
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except IntegrityError:
            # 中文注释：打印调试信息，便于开发阶段排查问题。
            print(traceback.format_exc())
            # 中文注释：调用函数或方法，执行对应的业务处理。
            db.rollback()
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='菜单路径已存在，请更换。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data, message='菜单已创建。')


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@menus_router.put('/menus')
# 中文注释：定义函数 update_menu，封装一段可复用的业务逻辑。
def update_menu(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 menu_id 的值，供后续逻辑使用。
    menu_id = data.get('id')
    # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
    name = clean_string(data.get('name'))
    # 中文注释：设置变量或字段 path 的值，供后续逻辑使用。
    path = clean_string(data.get('path'))
    # 中文注释：设置变量或字段 icon 的值，供后续逻辑使用。
    icon = clean_string(data.get('icon'), 'appstore') or 'appstore'
    # 中文注释：设置变量或字段 sort 的值，供后续逻辑使用。
    sort = parse_int(data.get('sort'))
    # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
    status = clean_string(data.get('status'), 'enabled') or 'enabled'
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if menu_id in ('', None):
        # 中文注释：设置变量或字段 menu_id 的值，供后续逻辑使用。
        menu_id = None
    # 中文注释：当前面条件都不成立时，执行默认分支逻辑。
    else:
        # 中文注释：设置变量或字段 menu_id 的值，供后续逻辑使用。
        menu_id = parse_int(menu_id)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not menu_id:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='菜单 ID 不存在。')

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not name:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='菜单名称不能为空。')
    
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not path or not path.startswith('/'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='菜单路径必须以 / 开头。')
    
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if status not in ('enabled', 'disabled'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')

    # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
    payload = schemas.MenuUpdate(
        # 中文注释：设置变量或字段 id 的值，供后续逻辑使用。
        id=menu_id,
        # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
        name=name,
        # 中文注释：设置变量或字段 path 的值，供后续逻辑使用。
        path=path,
        # 中文注释：设置变量或字段 icon 的值，供后续逻辑使用。
        icon=icon,
        # 中文注释：设置变量或字段 sort 的值，供后续逻辑使用。
        sort=sort,
        # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
        status=status,
    # 中文注释：结束当前多行数据结构或多行参数。
    )

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：设置变量或字段 menu 的值，供后续逻辑使用。
            menu = crud.update_menu(db, payload)
            # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
            response_data = schemas.serialize_menu(menu)
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except ValueError:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='菜单不存在。')
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except IntegrityError:
            # 中文注释：打印调试信息，便于开发阶段排查问题。
            print(traceback.format_exc())
            # 中文注释：调用函数或方法，执行对应的业务处理。
            db.rollback()
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='菜单路径已存在，请更换。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data, message='菜单已更新。')


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@menus_router.delete('/menus/{menu_id}')
# 中文注释：定义函数 delete_menu，封装一段可复用的业务逻辑。
def delete_menu(menu_id: int):
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if menu_id <= 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='菜单 ID 不存在。')

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 deleted 的值，供后续逻辑使用。
        deleted = crud.delete_menu(db, menu_id)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not deleted:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=404, detail='菜单不存在。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=None, message='菜单已删除。')
