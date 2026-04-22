import traceback
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from .. import crud, schemas
from ..database import SessionLocal

menus_router = APIRouter()


@menus_router.get('/menus')
def read_menus(user_id: int | None = Query(default=None), name: str = Query(default='')):
    name = name.strip()

    with SessionLocal() as db:
        menus = crud.list_menus(
            db,
            user_id=user_id,
            name=name or None,
        )

    return [schemas.serialize_menu(menu) for menu in menus]


@menus_router.get('/menus/{menu_id}')
def read_menu(menu_id: int):
    if menu_id <= 0:
        raise HTTPException(status_code=400, detail='菜单 ID 不存在。')

    with SessionLocal() as db:
        menu = crud.get_menu(db, menu_id)

    if not menu:
        raise HTTPException(status_code=404, detail='菜单不存在。')

    return schemas.serialize_menu(menu)


@menus_router.post('/menus', status_code=status.HTTP_201_CREATED)
def add_menu(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    user_id = data.get('user_id')
    name = str(data.get('name', '')).strip()
    path = str(data.get('path', '')).strip()
    icon = str(data.get('icon', 'appstore')).strip() or 'appstore'
    sort = int(data.get('sort', 0))
    status = str(data.get('status', 'enabled')).strip() or 'enabled'

    if user_id in ('', None):
        user_id = None
    else:
        user_id = int(user_id)

    if not name:
        raise HTTPException(status_code=400, detail='菜单名称不能为空。')
    if not path or not path.startswith('/'):
        raise HTTPException(status_code=400, detail='菜单路径必须以 / 开头。')
    if user_id is not None and user_id <= 0:
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')
    if status not in ('enabled', 'disabled'):
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')

    payload = schemas.MenuCreate(
        user_id=user_id,
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

    return schemas.serialize_menu(menu)


@menus_router.put('/menus')
def update_menu(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    menu_id = data.get('id')
    user_id = data.get('user_id')
    name = str(data.get('name', '')).strip()
    path = str(data.get('path', '')).strip()
    icon = str(data.get('icon', 'appstore')).strip() or 'appstore'
    sort = int(data.get('sort', 0))
    status = str(data.get('status', 'enabled')).strip() or 'enabled'

    if user_id in ('', None):
        user_id = None
    else:
        user_id = int(user_id)

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
    
    if user_id is not None and user_id <= 0:
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')
    
    if status not in ('enabled', 'disabled'):
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')

    payload = schemas.MenuUpdate(
        id=menu_id,
        user_id=user_id,
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

    return schemas.serialize_menu(menu)


@menus_router.delete('/menus/{menu_id}')
def delete_menu(menu_id: int):
    if menu_id <= 0:
        raise HTTPException(status_code=400, detail='菜单 ID 不存在。')

    with SessionLocal() as db:
        deleted = crud.delete_menu(db, menu_id)

    if not deleted:
        raise HTTPException(status_code=404, detail='菜单不存在。')

    return {'detail': '菜单已删除。'}
