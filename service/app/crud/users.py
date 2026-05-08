# 构造 ORM 查询语句。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import Select, func, select
# 表示当前 CRUD 使用的数据库会话类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.orm import Session

# models: 用户等 ORM 模型定义模块。
# schemas: 用户相关的数据传输结构模块。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .. import models, schemas
# dedupe_int_ids: 统一处理前端传入的 ID 列表，避免重复 ID 影响数量校验。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..utils import dedupe_int_ids


# 中文注释：定义函数 list_users，封装一段可复用的业务逻辑。
def list_users(
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    db: Session,
    # 中文注释：执行当前代码行对应的业务逻辑。
    *,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    name: str | None = None,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    page: int = 1,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    page_size: int = 10,
# 中文注释：执行当前代码行对应的业务逻辑。
) -> list[models.User]:
    # 中文注释：设置变量或字段 statement: Select[tuple[models.User]] 的值，供后续逻辑使用。
    statement: Select[tuple[models.User]] = select(models.User)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if name:
        # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
        statement = statement.where(models.User.name.ilike(f'%{name}%'))

    # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
    statement = statement.order_by(models.User.id.asc())

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if page >= 1 and page_size > 0:
        # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
        statement = statement.offset((page - 1) * page_size).limit(page_size)

    # 中文注释：返回当前函数处理后的结果。
    return list(db.scalars(statement))


# 中文注释：定义函数 count_users，封装一段可复用的业务逻辑。
def count_users(db: Session, *, name: str | None = None) -> int:
    # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
    statement = select(func.count()).select_from(models.User)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if name:
        # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
        statement = statement.where(models.User.name.ilike(f'%{name}%'))

    # 中文注释：返回当前函数处理后的结果。
    return int(db.scalar(statement) or 0)

# 中文注释：定义函数 get_user，封装一段可复用的业务逻辑。
def get_user(db: Session, user_id: int) -> models.User | None:
    # 中文注释：返回当前函数处理后的结果。
    return db.get(models.User, user_id)


# 中文注释：定义函数 create_user，封装一段可复用的业务逻辑。
def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    # 中文注释：设置变量或字段 user 的值，供后续逻辑使用。
    user = models.User(**payload.model_dump())
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.add(user)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.refresh(user)
    # 中文注释：返回当前函数处理后的结果。
    return user


# 中文注释：定义函数 update_user，封装一段可复用的业务逻辑。
def update_user(db: Session, payload: schemas.UserUpdate) -> models.User:
    # 中文注释：设置变量或字段 user 的值，供后续逻辑使用。
    user = db.get(models.User, payload.id)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not user:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise ValueError('User not found')
    # 中文注释：遍历集合中的每一项，并逐项执行下面的代码块。
    for key, value in payload.model_dump().items():
        # 主键 id 只用于定位记录，不应在更新时再次写回，避免误改主键导致关联数据异常。
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if key == 'id':
            # 中文注释：跳过本轮循环，继续处理下一项。
            continue
        # 中文注释：调用函数或方法，执行对应的业务处理。
        setattr(user, key, value)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.refresh(user)
    # 中文注释：返回当前函数处理后的结果。
    return user


# 中文注释：定义函数 delete_user，封装一段可复用的业务逻辑。
def delete_user(db: Session, user_id: int) -> bool:
    # 中文注释：设置变量或字段 user 的值，供后续逻辑使用。
    user = db.get(models.User, user_id)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not user:
        # 中文注释：返回当前函数处理后的结果。
        return False
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.delete(user)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：返回当前函数处理后的结果。
    return True

# 中文注释：定义函数 user_relation_roles，封装一段可复用的业务逻辑。
def user_relation_roles(db: Session, user_id: int, role_ids: list[int]) -> models.User:
    # 中文注释：设置变量或字段 user 的值，供后续逻辑使用。
    user = db.get(models.User, user_id)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not user:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise ValueError('User not found')

    # 中文注释：设置变量或字段 roles 的值，供后续逻辑使用。
    role_ids = dedupe_int_ids(role_ids)
    roles = []
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if role_ids:
        # 中文注释：设置变量或字段 roles 的值，供后续逻辑使用。
        roles = list(db.scalars(select(models.Role).where(models.Role.id.in_(role_ids))))
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if len(roles) != len(role_ids):
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise ValueError('Role not found')

    # 中文注释：设置变量或字段 user.roles 的值，供后续逻辑使用。
    user.roles = roles
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.refresh(user)
    # 中文注释：返回当前函数处理后的结果。
    return user

# 中文注释：定义函数 query_relation_roles，封装一段可复用的业务逻辑。
def query_relation_roles(db: Session, user_id: int) -> list[models.Role]:
    # 中文注释：设置变量或字段 user 的值，供后续逻辑使用。
    user = db.get(models.User, user_id)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not user:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise ValueError('User not found')

    # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
    statement = (
        # 中文注释：调用函数或方法，执行对应的业务处理。
        select(models.Role)
        # 中文注释：调用函数或方法，执行对应的业务处理。
        .join(models.UserRoles, models.UserRoles.role_id == models.Role.id)
        # 中文注释：调用函数或方法，执行对应的业务处理。
        .where(models.UserRoles.user_id == user_id)
        # 中文注释：调用函数或方法，执行对应的业务处理。
        .order_by(models.Role.sort.asc(), models.Role.id.asc())
    # 中文注释：结束当前多行数据结构或多行参数。
    )
    # 中文注释：返回当前函数处理后的结果。
    return list(db.scalars(statement))
