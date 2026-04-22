import traceback
from typing import Any

from fastapi import APIRouter, Body, HTTPException, status
from sqlalchemy.exc import IntegrityError

from .. import crud, schemas
from ..database import SessionLocal

users_router = APIRouter()


@users_router.get('/users')
def read_users():
    with SessionLocal() as db:
        users = crud.list_users(db)

    return [schemas.serialize_user(user) for user in users]


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
        except IntegrityError:
            print(traceback.format_exc())
            db.rollback()
            raise HTTPException(status_code=400, detail='邮箱已存在，请更换。')

    return schemas.serialize_user(user)


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
        except ValueError:
            raise HTTPException(status_code=404, detail='用户不存在。')
        except IntegrityError:
            print(traceback.format_exc())
            db.rollback()
            raise HTTPException(status_code=400, detail='邮箱已存在，请更换。')

    return schemas.serialize_user(user)


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

    return {'detail': '用户已删除。'}


@users_router.delete('/users/{user_id}')
def delete_user_by_path(user_id: int):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')

    with SessionLocal() as db:
        deleted = crud.delete_user(db, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail='用户不存在。')

    return {'detail': '用户已删除。'}
