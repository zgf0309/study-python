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