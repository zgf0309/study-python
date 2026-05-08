# traceback: 打印异常堆栈，便于开发时排查错误。
# 中文注释：导入当前文件需要使用的 Python 模块。
import traceback

# Any: 表示请求体中可接收任意值类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from typing import Any

# APIRouter: 创建用户接口的路由对象。
# Body: 从请求体中读取提交的数据。
# HTTPException: 主动返回 HTTP 错误响应。
# status: 提供 HTTP 状态码常量。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi import APIRouter, Body, HTTPException, Query, status, Request

# IntegrityError: 捕获数据库唯一约束等完整性异常。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.exc import IntegrityError

# crud: 提供用户相关的 CRUD 方法集合。
# schemas: 提供用户相关的请求与响应数据结构。
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

# 中文注释：设置变量或字段 users_router 的值，供后续逻辑使用。
users_router = APIRouter()
# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@users_router.get('/users')
# 中文注释：定义函数 read_users，封装一段可复用的业务逻辑。
def read_users(
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
        # 中文注释：设置变量或字段 users 的值，供后续逻辑使用。
        users = crud.list_users(
            # 中文注释：执行当前代码行对应的业务逻辑。
            db,
            # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
            name=name or None,
            # 中文注释：设置变量或字段 page 的值，供后续逻辑使用。
            page=page,
            # 中文注释：设置变量或字段 page_size 的值，供后续逻辑使用。
            page_size=page_size,)
        # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
        payload = [schemas.serialize_user(user) for user in users]
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        extra = {'total': crud.count_users(db, name=name or None)} if page >= 1 else {}

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=payload, **extra)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@users_router.post('/users', status_code=status.HTTP_201_CREATED)
# 中文注释：定义函数 add_user，封装一段可复用的业务逻辑。
def add_user(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
    name = clean_string(data.get('name'))
    # 中文注释：设置变量或字段 email 的值，供后续逻辑使用。
    email = clean_string(data.get('email'))
    # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
    role = clean_string(data.get('role'), 'viewer') or 'viewer'

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not name:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='姓名不能为空。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if '@' not in email or email.startswith('@') or email.endswith('@'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='邮箱格式不正确。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if role not in ('viewer', 'editor', 'admin'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='角色只能是 viewer、editor 或 admin。')

    # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
    payload = schemas.UserCreate(name=name, email=email, role=role)

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：设置变量或字段 user 的值，供后续逻辑使用。
            user = crud.create_user(db, payload)
            # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
            response_data = schemas.serialize_user(user)
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except IntegrityError:
            # 中文注释：打印调试信息，便于开发阶段排查问题。
            print(traceback.format_exc())
            # 中文注释：调用函数或方法，执行对应的业务处理。
            db.rollback()
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='邮箱已存在，请更换。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data, message='用户已创建。')


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@users_router.put('/users')
# 中文注释：定义函数 update_user，封装一段可复用的业务逻辑。
def update_user(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 user_id 的值，供后续逻辑使用。
    user_id = parse_int(data.get('id'))
    # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
    name = clean_string(data.get('name'))
    # 中文注释：设置变量或字段 email 的值，供后续逻辑使用。
    email = clean_string(data.get('email'))
    # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
    role = clean_string(data.get('role'), 'viewer') or 'viewer'

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not user_id or user_id <= 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not name:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='姓名不能为空。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if '@' not in email or email.startswith('@') or email.endswith('@'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='邮箱格式不正确。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if role not in ('viewer', 'editor', 'admin'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='角色只能是 viewer、editor 或 admin。')

    # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
    payload = schemas.UserUpdate(id=user_id, name=name, email=email, role=role)

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：设置变量或字段 user 的值，供后续逻辑使用。
            user = crud.update_user(db, payload)
            # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
            response_data = schemas.serialize_user(user)
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except ValueError:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='用户不存在。')
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except IntegrityError:
            # 中文注释：打印调试信息，便于开发阶段排查问题。
            print(traceback.format_exc())
            # 中文注释：调用函数或方法，执行对应的业务处理。
            db.rollback()
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='邮箱已存在，请更换。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data, message='用户已更新。')


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@users_router.delete('/users')
# 中文注释：定义函数 delete_user，封装一段可复用的业务逻辑。
def delete_user(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 user_id 的值，供后续逻辑使用。
    user_id = parse_int(data.get('id'))
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not user_id or user_id <= 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 deleted 的值，供后续逻辑使用。
        deleted = crud.delete_user(db, user_id)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not deleted:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=404, detail='用户不存在。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=None, message='用户已删除。')


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@users_router.delete('/users/{user_id}')
# 中文注释：定义函数 delete_user_by_path，封装一段可复用的业务逻辑。
def delete_user_by_path(user_id: int):
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if user_id <= 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 deleted 的值，供后续逻辑使用。
        deleted = crud.delete_user(db, user_id)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not deleted:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=404, detail='用户不存在。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=None, message='用户已删除。')


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@users_router.post('/users/relation-roles')
# 中文注释：定义函数 user_relation_roles，封装一段可复用的业务逻辑。
def user_relation_roles(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 user_id 的值，供后续逻辑使用。
    user_id = parse_int(data.get('id'))
    # 中文注释：设置变量或字段 raw_role_ids 的值，供后续逻辑使用。
    raw_role_ids = data.get('role_ids', [])

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not user_id or user_id <= 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='用户 ID 不存在。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not isinstance(raw_role_ids, list):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='角色 ID 列表格式不正确。')

    # 中文注释：开始执行可能抛出异常的代码块。
    # 中文注释：设置变量或字段 role_ids 的值，供后续逻辑使用。
    role_ids = dedupe_int_ids(raw_role_ids)

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：调用函数或方法，执行对应的业务处理。
            crud.user_relation_roles(db, user_id, role_ids)
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except ValueError:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='用户不存在。')

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=None, message='用户权限已更新。')

# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@users_router.get('/users/relation-roles')
# 中文注释：定义函数 query_relation_roles，封装一段可复用的业务逻辑。
def query_relation_roles(id: int = Query(default=0)):

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：设置变量或字段 roles 的值，供后续逻辑使用。
            roles = crud.query_relation_roles(db, id)
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except ValueError:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='用户不存在。')
        # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
        payload = [schemas.serialize_role(role) for role in roles]

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=payload)

# 多查询参数时，用request.query_params.get()获取参数值，避免 FastAPI 对参数进行类型转换导致的错误。
# def query_relation_roles(request: Request):
#     id = request.query_params.get('id')
#     with SessionLocal() as db:
#         try:
#             roles = crud.query_relation_roles(db, id)
#         except ValueError:
#             raise HTTPException(status_code=404, detail='用户不存在。')
#         payload = [schemas.serialize_role(role) for role in roles]

#     return api_response(data=payload)
