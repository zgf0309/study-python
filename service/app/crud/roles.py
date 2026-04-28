# 构造 ORM 查询语句。
from sqlalchemy import Select, func, select
# 表示当前 CRUD 使用的数据库会话类型。
from sqlalchemy.orm import Session, contains_eager

# models: 菜单、用户等 ORM 模型定义模块。
# schemas: 菜单相关的数据传输结构模块。
from .. import models, schemas


def list_roles(
    db: Session,
    *,
    name: str | None = None,
    status: str | None = None,
    page: int = 0,
    page_size: int = 10,
) -> list[models.Role]:
    statement = select(models.Role)

    if name:
        statement = statement.where(models.Role.name.ilike(f'%{name}%'))

    if status:
        statement = statement.where(models.Role.status == status)

    statement = statement.order_by(models.Role.sort.asc(), models.Role.id.asc())

    if page >= 1 and page_size > 0:
        statement = statement.offset((page - 1) * page_size).limit(page_size)

    return list(db.scalars(statement))


def count_roles(
    db: Session,
    *,
    name: str | None = None,
    status: str | None = None,
) -> int:
    statement = select(func.count()).select_from(models.Role)

    if name:
        statement = statement.where(models.Role.name.ilike(f'%{name}%'))

    if status:
        statement = statement.where(models.Role.status == status)

    return int(db.scalar(statement) or 0)

def create_role(db: Session, payload: schemas.RoleCreate) -> models.Role:
    role = models.Role(**payload.model_dump())
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def update_role(db: Session, payload: schemas.RoleUpdate) -> models.Role:
    role = db.get(models.Role, payload.id)
    if not role:
        raise ValueError('Role not found')
    for key, value in payload.model_dump().items():
        setattr(role, key, value)
    db.commit()
    db.refresh(role)
    return role

def delete_role(db: Session, role_id: int) -> bool:
    role = db.get(models.Role, role_id)
    if not role:
        raise ValueError('Role not found')
    db.delete(role)
    db.commit()
    return True


def role_relation_menus(db: Session, role_id: int, menu_ids: list[int]) -> models.Role:
    role = db.get(models.Role, role_id)
    if not role:
        raise ValueError('Role not found')

    menus = []
    if menu_ids:
        menus = list(db.scalars(select(models.Menu).where(models.Menu.id.in_(menu_ids))))
        if len(menus) != len(menu_ids):
            raise ValueError('Some menus not found')

    role.menus = menus
    db.commit()
    db.refresh(role)
    return role

def query_relation_menus(db: Session, id: int) -> list[models.Menu]:
    role = db.get(models.Role, id)
    if not role:
        raise ValueError('Role not found')
    
    # 构造查询语句：从 menus 表出发，关联 role_menus 中间表，筛出指定角色拥有的菜单
    statement = (
        # 主查询对象为 Menu，最终返回的也是 Menu 实体列表
        select(models.Menu)
        # INNER JOIN 关联表 role_menus，连接条件为 role_menus.menu_id = menus.id
        # 等价 SQL: JOIN role_menus ON role_menus.menu_id = menus.id
        .join(models.RoleMenus, models.RoleMenus.menu_id == models.Menu.id)
        # 过滤条件：只保留属于当前角色的关联记录
        # 等价 SQL: WHERE role_menus.role_id = :id
        .where(models.RoleMenus.role_id == id)
        # 排序：先按菜单的 sort 字段升序（业务排序），sort 相同则按 id 升序兜底，保证结果稳定
        .order_by(models.Menu.sort.asc(), models.Menu.id.asc())
    )
    # db.scalars(statement) 执行查询并返回 Menu 对象迭代器，外层 list() 转成列表返回
    return list(db.scalars(statement))