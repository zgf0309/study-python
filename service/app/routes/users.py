# traceback: 打印异常堆栈，便于开发时排查错误。
import traceback

# Any: 表示请求体中可接收任意值类型。
from typing import Any

# APIRouter: 创建用户接口的路由对象。
# Body: 从请求体中读取提交的数据。
# HTTPException: 主动返回 HTTP 错误响应。
# status: 提供 HTTP 状态码常量。
from fastapi import APIRouter, Body, HTTPException, Query, status

# IntegrityError: 捕获数据库唯一约束等完整性异常。
from sqlalchemy.exc import IntegrityError

# crud: 提供用户相关的 CRUD 方法集合。
# schemas: 提供用户相关的请求与响应数据结构。
from .. import crud, schemas

# SessionLocal: 数据库会话工厂，用于处理当前请求的数据库读写。
from ..database import SessionLocal

# api_response: 统一包装 API 返回结构。
from ..response import api_response

users_router = APIRouter()
@users_router.get('/users')
def read_users(name: str = Query(default=''), page: int = Query(default=0), page_size: int = Query(default=10, ge=1, le=100)):
    with SessionLocal() as db:
        users = crud.list_users(
            db,
            name=name,
            page=page,
            page_size=page_size,)
        payload = [schemas.serialize_user(user) for user in users]
        extra = {'total': crud.count_users(db, name=name)} if page >= 1 else {}

        print(f"==========>{extra}")

    return api_response(data=payload, **extra)


@users_router.post('/users', status_code=status.HTTP_201_CREATED)
def add_user(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip()
    role = str(data.get('role', 'viewer')).strip() or 'viewer'

    if not name:
        raise HTTPException(status_code=400, detail='姓名不能为空。')
    if '@' not in email or email.startswith('@') or email.endswith('@'):
        raise HTTPException(status_code=400, detail='邮箱格式不正确。')
    if role not in ('viewer', 'editor', 'admin'):
        raise HTTPException(status_code=400, detail='角色只能是 viewer、editor 或 admin。')

    payload = schemas.UserCreate(name=name, email=email, role=role)

    with SessionLocal() as db:
        try:
            user = crud.create_user(db, payload)
            response_data = schemas.serialize_user(user)
        except IntegrityError:
            print(traceback.format_exc())
            db.rollback()
            raise HTTPException(status_code=400, detail='邮箱已存在，请更换。')

    return api_response(data=response_data, message='用户已创建。')


@users_router.put('/users')
def update_user(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    user_id = int(data.get('id', 0))
    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip()
    role = str(data.get('role', 'viewer')).strip() or 'viewer'

    if not user_id or user_id <= 0:
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')
    if not name:
        raise HTTPException(status_code=400, detail='姓名不能为空。')
    if '@' not in email or email.startswith('@') or email.endswith('@'):
        raise HTTPException(status_code=400, detail='邮箱格式不正确。')
    if role not in ('viewer', 'editor', 'admin'):
        raise HTTPException(status_code=400, detail='角色只能是 viewer、editor 或 admin。')

    payload = schemas.UserUpdate(id=user_id, name=name, email=email, role=role)

    with SessionLocal() as db:
        try:
            user = crud.update_user(db, payload)
            response_data = schemas.serialize_user(user)
        except ValueError:
            raise HTTPException(status_code=404, detail='用户不存在。')
        except IntegrityError:
            print(traceback.format_exc())
            db.rollback()
            raise HTTPException(status_code=400, detail='邮箱已存在，请更换。')

    return api_response(data=response_data, message='用户已更新。')


@users_router.delete('/users')
def delete_user(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    user_id = int(data.get('id', 0))
    if not user_id or user_id <= 0:
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')

    with SessionLocal() as db:
        deleted = crud.delete_user(db, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail='用户不存在。')

    return api_response(data=None, message='用户已删除。')


@users_router.delete('/users/{user_id}')
def delete_user_by_path(user_id: int):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')

    with SessionLocal() as db:
        deleted = crud.delete_user(db, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail='用户不存在。')

    return api_response(data=None, message='用户已删除。')


@users_router.post('/users/relation-roles')
def user_relation_roles(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    user_id = int(data.get('id', 0))
    raw_role_ids = data.get('role_ids', [])

    if not user_id or user_id <= 0:
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')
    if not isinstance(raw_role_ids, list):
        raise HTTPException(status_code=400, detail='角色 ID 列表格式不正确。')

    try:
        role_ids = list(dict.fromkeys(int(role_id) for role_id in raw_role_ids if int(role_id) > 0))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail='角色 ID 列表格式不正确。')

    with SessionLocal() as db:
        try:
            crud.user_relation_roles(db, user_id, role_ids)
        except ValueError:
            raise HTTPException(status_code=404, detail='用户不存在。')

    return api_response(data=None, message='用户权限已更新。')
