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
# dedupe_int_ids: 统一处理 ID 列表，兼顾去重、转整数和过滤非法值。
# parse_int: 安全转换整数，避免前端传空字符串时接口报 500。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..utils import clean_string, dedupe_int_ids, parse_int

# 中文注释：设置变量或字段 roles_router 的值，供后续逻辑使用。
roles_router = APIRouter()


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@roles_router.get('/roles')
# 中文注释：定义函数 read_roles，封装一段可复用的业务逻辑。
def read_roles(
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
        # 中文注释：设置变量或字段 roles 的值，供后续逻辑使用。
        roles = crud.list_roles(
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
        payload = [schemas.serialize_role(role) for role in roles]
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        extra = {'total': crud.count_roles(db, name=name or None)} if page >= 1 else {}

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=payload, **extra)

# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@roles_router.post('/roles')
# 中文注释：定义函数 add_role，封装一段可复用的业务逻辑。
def add_role(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
    name = clean_string(data.get('name'))
    # 中文注释：设置变量或字段 description 的值，供后续逻辑使用。
    description = clean_string(data.get('description'))
    # 中文注释：设置变量或字段 sort 的值，供后续逻辑使用。
    sort = parse_int(data.get('sort'))
    # 中文注释：设置变量或字段 role_status 的值，供后续逻辑使用。
    role_status = clean_string(data.get('status'), 'enabled') or 'enabled'
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not name:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='角色名称不能为空。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if role_status not in ('enabled', 'disabled'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')
    
    # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
    payload = schemas.RoleCreate(
        # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
        name=name,
        # 中文注释：设置变量或字段 description 的值，供后续逻辑使用。
        description=description,
        # 中文注释：设置变量或字段 sort 的值，供后续逻辑使用。
        sort=sort,
        # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
        status=role_status,
    # 中文注释：结束当前多行数据结构或多行参数。
    )
    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
            role = crud.create_role(db, payload)
            # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
            response_data = schemas.serialize_role(role)
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except IntegrityError:
            # 中文注释：打印调试信息，便于开发阶段排查问题。
            print(traceback.format_exc())
            # 中文注释：调用函数或方法，执行对应的业务处理。
            db.rollback()
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='角色名称已存在，请更换。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data, message='角色已创建。')

# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@roles_router.put('/roles')
# 中文注释：定义函数 update_role，封装一段可复用的业务逻辑。
def update_role(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 role_id 的值，供后续逻辑使用。
    role_id = parse_int(data.get('id'))
    # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
    name = clean_string(data.get('name'))
    # 中文注释：设置变量或字段 description 的值，供后续逻辑使用。
    description = clean_string(data.get('description'))
    # 中文注释：设置变量或字段 sort 的值，供后续逻辑使用。
    sort = parse_int(data.get('sort'))
    # 中文注释：设置变量或字段 role_status 的值，供后续逻辑使用。
    role_status = clean_string(data.get('status'), 'enabled') or 'enabled'
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if role_id <= 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='角色 ID 不存在。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not name:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='角色名称不能为空。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if role_status not in ('enabled', 'disabled'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')

    # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
    payload = schemas.RoleUpdate(
        # 中文注释：设置变量或字段 id 的值，供后续逻辑使用。
        id=role_id,
        # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
        name=name,
        # 中文注释：设置变量或字段 description 的值，供后续逻辑使用。
        description=description,
        # 中文注释：设置变量或字段 sort 的值，供后续逻辑使用。
        sort=sort,
        # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
        status=role_status,
    # 中文注释：结束当前多行数据结构或多行参数。
    )

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
            role = crud.update_role(db, payload)
            # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
            response_data = schemas.serialize_role(role)
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except IntegrityError:
            # 中文注释：打印调试信息，便于开发阶段排查问题。
            print(traceback.format_exc())
            # 中文注释：调用函数或方法，执行对应的业务处理。
            db.rollback()
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='角色名称已存在，请更换。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data, message='角色已更新。')  

# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@roles_router.delete('/roles/{role_id}')
# 中文注释：定义函数 delete_role，封装一段可复用的业务逻辑。
def delete_role(role_id: int):
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if role_id is None or role_id <= 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='角色 ID 不存在。')

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
        role = crud.delete_role(db, role_id)
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if not role:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='角色不存在。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=None, message='角色已删除。')

# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@roles_router.post('/roles/relation-menus')
# 中文注释：定义函数 role_relation_menus，封装一段可复用的业务逻辑。
def role_relation_menus(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 role_id 的值，供后续逻辑使用。
    role_id = parse_int(data.get('id'))
    # 中文注释：设置变量或字段 menu_ids 的值，供后续逻辑使用。
    menu_ids = data.get('menu_ids', [])
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if role_id <= 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='角色 ID 不存在。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not isinstance(menu_ids, list):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='菜单 ID 列表不合法。')
    # 中文注释：设置变量或字段 menu_ids 的值，供后续逻辑使用。
    menu_ids = dedupe_int_ids(menu_ids)

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
            role = crud.role_relation_menus(db, role_id, menu_ids)
            # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
            response_data = schemas.serialize_role(role)
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except ValueError:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='角色不存在。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data, message='角色菜单关联已更新。')


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@roles_router.get('/roles/relation-menus')
# 中文注释：定义函数 query_relation_menus，封装一段可复用的业务逻辑。
def query_relation_menus(id: int = Query(default=0)):
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not id or id <= 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='角色 ID 不存在。')

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：设置变量或字段 menus 的值，供后续逻辑使用。
            menus = crud.query_relation_menus(db, id)
            # 角色存在但暂未分配菜单时，应返回空列表，而不是误报“角色不存在”。
            # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
            response_data = [schemas.serialize_menu(menu) for menu in menus]
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except ValueError:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='角色不存在。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data, message='角色关联菜单获取成功。')
