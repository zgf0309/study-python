# 构造 ORM 查询语句。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import Select, func, select
# 表示当前 CRUD 使用的数据库会话类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.orm import Session

# models: 菜单、用户等 ORM 模型定义模块。
# schemas: 菜单相关的数据传输结构模块。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .. import models, schemas
# dedupe_int_ids: 统一处理前端传入的 ID 列表，避免重复 ID 影响数量校验。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..utils import dedupe_int_ids


# 中文注释：定义函数 list_roles，封装一段可复用的业务逻辑。
def list_roles(
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    db: Session,
    # 中文注释：执行当前代码行对应的业务逻辑。
    *,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    name: str | None = None,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    status: str | None = None,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    page: int = 0,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    page_size: int = 10,
# 中文注释：执行当前代码行对应的业务逻辑。
) -> list[models.Role]:
    # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
    statement = select(models.Role)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if name:
        # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
        statement = statement.where(models.Role.name.ilike(f'%{name}%'))

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if status:
        # 中文注释：调用函数或方法，执行对应的业务处理。
        statement = statement.where(models.Role.status == status)

    # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
    statement = statement.order_by(models.Role.sort.asc(), models.Role.id.asc())

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if page >= 1 and page_size > 0:
        # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
        statement = statement.offset((page - 1) * page_size).limit(page_size)

    # 中文注释：返回当前函数处理后的结果。
    return list(db.scalars(statement))


# 中文注释：定义函数 count_roles，封装一段可复用的业务逻辑。
def count_roles(
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    db: Session,
    # 中文注释：执行当前代码行对应的业务逻辑。
    *,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    name: str | None = None,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    status: str | None = None,
# 中文注释：执行当前代码行对应的业务逻辑。
) -> int:
    # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
    statement = select(func.count()).select_from(models.Role)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if name:
        # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
        statement = statement.where(models.Role.name.ilike(f'%{name}%'))

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if status:
        # 中文注释：调用函数或方法，执行对应的业务处理。
        statement = statement.where(models.Role.status == status)

    # 中文注释：返回当前函数处理后的结果。
    return int(db.scalar(statement) or 0)

# 中文注释：定义函数 create_role，封装一段可复用的业务逻辑。
def create_role(db: Session, payload: schemas.RoleCreate) -> models.Role:
    # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
    data = payload.model_dump()
    # 创建角色时 id 通常由数据库自增生成；如果前端没有传 id，就不要把 None 写入 ORM。
    # 中文注释：调用函数或方法，执行对应的业务处理。
    data.pop('id', None)
    # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
    role = models.Role(**data)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.add(role)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.refresh(role)
    # 中文注释：返回当前函数处理后的结果。
    return role

# 中文注释：定义函数 update_role，封装一段可复用的业务逻辑。
def update_role(db: Session, payload: schemas.RoleUpdate) -> models.Role:
    # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
    role = db.get(models.Role, payload.id)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not role:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise ValueError('Role not found')
    # 中文注释：遍历集合中的每一项，并逐项执行下面的代码块。
    for key, value in payload.model_dump().items():
        # 主键 id 只用于定位记录，不应在更新时再次写回，避免误改主键导致关联数据异常。
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if key == 'id':
            # 中文注释：跳过本轮循环，继续处理下一项。
            continue
        # 中文注释：调用函数或方法，执行对应的业务处理。
        setattr(role, key, value)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.refresh(role)
    # 中文注释：返回当前函数处理后的结果。
    return role

# 中文注释：定义函数 delete_role，封装一段可复用的业务逻辑。
def delete_role(db: Session, role_id: int) -> bool:
    # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
    role = db.get(models.Role, role_id)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not role:
        # 中文注释：返回当前函数处理后的结果。
        return False
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.delete(role)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：返回当前函数处理后的结果。
    return True


# 中文注释：定义函数 role_relation_menus，封装一段可复用的业务逻辑。
def role_relation_menus(db: Session, role_id: int, menu_ids: list[int]) -> models.Role:
    # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
    role = db.get(models.Role, role_id)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not role:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise ValueError('Role not found')

    # 中文注释：设置变量或字段 menus 的值，供后续逻辑使用。
    menu_ids = dedupe_int_ids(menu_ids)
    menus = []
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if menu_ids:
        # 中文注释：设置变量或字段 menus 的值，供后续逻辑使用。
        menus = list(db.scalars(select(models.Menu).where(models.Menu.id.in_(menu_ids))))
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if len(menus) != len(menu_ids):
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise ValueError('Some menus not found')

    # 中文注释：设置变量或字段 role.menus 的值，供后续逻辑使用。
    role.menus = menus
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.refresh(role)
    # 中文注释：返回当前函数处理后的结果。
    return role

# 中文注释：定义函数 query_relation_menus，封装一段可复用的业务逻辑。
def query_relation_menus(db: Session, id: int) -> list[models.Menu]:
    # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
    role = db.get(models.Role, id)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not role:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise ValueError('Role not found')
    
    # 构造查询语句：从 menus 表出发，关联 role_menus 中间表，筛出指定角色拥有的菜单
    # 中文注释：设置变量或字段 statement 的值，供后续逻辑使用。
    statement = (
        # 主查询对象为 Menu，最终返回的也是 Menu 实体列表
        # 中文注释：调用函数或方法，执行对应的业务处理。
        select(models.Menu)
        # INNER JOIN 关联表 role_menus，连接条件为 role_menus.menu_id = menus.id
        # 等价 SQL: JOIN role_menus ON role_menus.menu_id = menus.id
        # 中文注释：调用函数或方法，执行对应的业务处理。
        .join(models.RoleMenus, models.RoleMenus.menu_id == models.Menu.id)
        # 过滤条件：只保留属于当前角色的关联记录
        # 等价 SQL: WHERE role_menus.role_id = :id
        # 中文注释：调用函数或方法，执行对应的业务处理。
        .where(models.RoleMenus.role_id == id)
        # 排序：先按菜单的 sort 字段升序（业务排序），sort 相同则按 id 升序兜底，保证结果稳定
        # 中文注释：调用函数或方法，执行对应的业务处理。
        .order_by(models.Menu.sort.asc(), models.Menu.id.asc())
    # 中文注释：结束当前多行数据结构或多行参数。
    )
    # db.scalars(statement) 执行查询并返回 Menu 对象迭代器，外层 list() 转成列表返回
    # 中文注释：返回当前函数处理后的结果。
    return list(db.scalars(statement))
