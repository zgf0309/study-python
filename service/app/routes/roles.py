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

roles_router = APIRouter()


@roles_router.get('/roles')
def read_roles(
    name: str = Query(default=''),
    page: int = Query(default=0),
    page_size: int = Query(default=10, ge=1, le=100),
):
    name = name.strip()

    with SessionLocal() as db:
        roles = crud.list_roles(
            db,
            name=name or None,
            page=page,
            page_size=page_size,
        )
        payload = [schemas.serialize_role(role) for role in roles]
        extra = {'total': crud.count_roles(db, name=name or None)} if page >= 1 else {}

    return api_response(data=payload, **extra)

@roles_router.post('/roles')
def add_role(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    name = str(data.get('name', '')).strip()
    description = str(data.get('description', '')).strip()
    sort = int(data.get('sort', 0))
    role_status = str(data.get('status', 'enabled')).strip() or 'enabled'
    if not name:
        raise HTTPException(status_code=400, detail='角色名称不能为空。')
    if role_status not in ('enabled', 'disabled'):
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')
    
    payload = schemas.RoleCreate(
        name=name,
        description=description,
        sort=sort,
        status=role_status,
    )
    with SessionLocal() as db:
        try:
            role = crud.create_role(db, payload)
        except IntegrityError:
            print(traceback.format_exc())
            db.rollback()
            raise HTTPException(status_code=400, detail='角色名称已存在，请更换。')

    return api_response( data=schemas.serialize_role(role), message='角色已创建。')

@roles_router.put('/roles')
def update_role(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    role_id = int(data.get('id', 0))
    name = str(data.get('name', '')).strip()
    description = str(data.get('description', '')).strip()
    sort = int(data.get('sort', 0))
    role_status = str(data.get('status', 'enabled')).strip() or 'enabled'
    if role_id <= 0:
        raise HTTPException(status_code=400, detail='角色 ID 不存在。')
    if not name:
        raise HTTPException(status_code=400, detail='角色名称不能为空。')
    if role_status not in ('enabled', 'disabled'):
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')

    payload = schemas.RoleUpdate(
        id=role_id,
        name=name,
        description=description,
        sort=sort,
        status=role_status,
    )

    with SessionLocal() as db:
        try:
            role = crud.update_role(db, payload)
        except IntegrityError:
            print(traceback.format_exc())
            db.rollback()
            raise HTTPException(status_code=400, detail='角色名称已存在，请更换。')

    return api_response(data=schemas.serialize_role(role), message='角色已更新。')  

@roles_router.delete('/roles/{role_id}')
def delete_role(role_id: int):
    if role_id is None or role_id <= 0:
        raise HTTPException(status_code=400, detail='角色 ID 不存在。')

    with SessionLocal() as db:
        role = crud.delete_role(db, role_id)
        if not role:
            raise HTTPException(status_code=404, detail='角色不存在。')

    return api_response(data=None, message='角色已删除。')

@roles_router.post('/roles/relation-menus')
def role_relation_menus(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    role_id = int(data.get('id', 0))
    menu_ids = data.get('menu_ids', [])
    if role_id <= 0:
        raise HTTPException(status_code=400, detail='角色 ID 不存在。')
    if not isinstance(menu_ids, list) or not all(isinstance(i, int) and i > 0 for i in menu_ids):
        raise HTTPException(status_code=400, detail='菜单 ID 列表不合法。')

    with SessionLocal() as db:
        try:
            role = crud.role_relation_menus(db, role_id, menu_ids)
            response_data = schemas.serialize_role(role)
        except ValueError:
            raise HTTPException(status_code=404, detail='角色不存在。')

    return api_response(data=response_data, message='角色菜单关联已更新。')