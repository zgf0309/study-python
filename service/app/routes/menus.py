# traceback: 打印异常堆栈，便于开发时排查错误。
import traceback

# Any: 表示请求体中可接收任意值类型。
from typing import Any

# APIRouter: 创建菜单接口的路由对象。
# Body: 从请求体中读取提交的数据。
# HTTPException: 主动返回 HTTP 错误响应。
# Query: 读取 URL 查询参数。
# status: 提供 HTTP 状态码常量。
from fastapi import APIRouter, Body, HTTPException, Query, status

# IntegrityError: 捕获数据库唯一约束等完整性异常。
from sqlalchemy.exc import IntegrityError

# crud: 提供菜单相关的 CRUD 方法集合。
# schemas: 提供菜单相关的请求与响应数据结构。
from .. import crud, schemas

# SessionLocal: 数据库会话工厂，用于处理当前请求的数据库读写。
from ..database import SessionLocal

# api_response: 统一包装 API 返回结构。
from ..response import api_response

menus_router = APIRouter()


@menus_router.get('/menus')
def read_menus( name: str = Query(default='')):
    name = name.strip()

    with SessionLocal() as db:
        menus = crud.list_menus(
            db,
            name=name or None,
        )

    return api_response(data=[schemas.serialize_menu(menu) for menu in menus])


@menus_router.get('/menus/{menu_id}')
def read_menu(menu_id: int):
    if menu_id <= 0:
        raise HTTPException(status_code=400, detail='菜单 ID 不存在。')

    with SessionLocal() as db:
        menu = crud.get_menu(db, menu_id)

    if not menu:
        raise HTTPException(status_code=404, detail='菜单不存在。')

    return api_response(data=schemas.serialize_menu(menu))


@menus_router.post('/menus', status_code=status.HTTP_201_CREATED)
def add_menu(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    name = str(data.get('name', '')).strip()
    path = str(data.get('path', '')).strip()
    icon = str(data.get('icon', 'appstore')).strip() or 'appstore'
    sort = int(data.get('sort', 0))
    status = str(data.get('status', 'enabled')).strip() or 'enabled'
    if not name:
        raise HTTPException(status_code=400, detail='菜单名称不能为空。')
    if not path or not path.startswith('/'):
        raise HTTPException(status_code=400, detail='菜单路径必须以 / 开头。')
    if status not in ('enabled', 'disabled'):
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')

    payload = schemas.MenuCreate(
        name=name,
        path=path,
        icon=icon,
        sort=sort,
        status=status,
    )

    with SessionLocal() as db:
        try:
            menu = crud.create_menu(db, payload)
        except IntegrityError:
            print(traceback.format_exc())
            db.rollback()
            raise HTTPException(status_code=400, detail='菜单路径已存在，请更换。')

    return api_response(data=schemas.serialize_menu(menu), message='菜单已创建。')


@menus_router.put('/menus')
def update_menu(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    menu_id = data.get('id')
    name = str(data.get('name', '')).strip()
    path = str(data.get('path', '')).strip()
    icon = str(data.get('icon', 'appstore')).strip() or 'appstore'
    sort = int(data.get('sort', 0))
    status = str(data.get('status', 'enabled')).strip() or 'enabled'
    if menu_id in ('', None):
        menu_id = None
    else:
        menu_id = int(menu_id)

    if not menu_id:
        raise HTTPException(status_code=400, detail='菜单 ID 不存在。')

    if not name:
        raise HTTPException(status_code=400, detail='菜单名称不能为空。')
    
    if not path or not path.startswith('/'):
        raise HTTPException(status_code=400, detail='菜单路径必须以 / 开头。')
    
    if status not in ('enabled', 'disabled'):
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')

    payload = schemas.MenuUpdate(
        id=menu_id,
        name=name,
        path=path,
        icon=icon,
        sort=sort,
        status=status,
    )

    with SessionLocal() as db:
        try:
            menu = crud.update_menu(db, payload)
        except ValueError:
            raise HTTPException(status_code=404, detail='菜单不存在。')
        except IntegrityError:
            print(traceback.format_exc())
            db.rollback()
            raise HTTPException(status_code=400, detail='菜单路径已存在，请更换。')

    return api_response(data=schemas.serialize_menu(menu), message='菜单已更新。')


@menus_router.delete('/menus/{menu_id}')
def delete_menu(menu_id: int):
    if menu_id <= 0:
        raise HTTPException(status_code=400, detail='菜单 ID 不存在。')

    with SessionLocal() as db:
        deleted = crud.delete_menu(db, menu_id)

    if not deleted:
        raise HTTPException(status_code=404, detail='菜单不存在。')

    return api_response(data=None, message='菜单已删除。')
