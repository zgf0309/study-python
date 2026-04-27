# 构造 ORM 查询语句。
from sqlalchemy import Select, func, select
# 表示当前 CRUD 使用的数据库会话类型。
from sqlalchemy.orm import Session, selectinload, contains_eager

# models: 用户等 ORM 模型定义模块。
# schemas: 用户相关的数据传输结构模块。
from .. import models, schemas


def list_users(
    db: Session,
    *,
    name: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> list[models.User]:
    statement: Select[tuple[models.User]] = select(models.User)

    if name:
        statement = statement.where(models.User.name.ilike(f'%{name}%'))

    statement = statement.order_by(models.User.id.asc())

    if page >= 1 and page_size > 0:
        statement = statement.offset((page - 1) * page_size).limit(page_size)

    return list(db.scalars(statement))


def count_users(db: Session, *, name: str | None = None) -> int:
    statement = select(func.count()).select_from(models.User)

    if name:
        statement = statement.where(models.User.name.ilike(f'%{name}%'))

    return int(db.scalar(statement) or 0)

def get_user(db: Session, user_id: int) -> models.User | None:
    return db.get(models.User, user_id)


def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    user = models.User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, payload: schemas.UserUpdate) -> models.User:
    user = db.get(models.User, payload.id)
    if not user:
        raise ValueError('User not found')
    for key, value in payload.model_dump().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = db.get(models.User, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

def user_relation_roles(db: Session, user_id: int, role_ids: list[int]) -> models.User:
    user = db.get(models.User, user_id)
    if not user:
        raise ValueError('User not found')

    roles = []
    if role_ids:
        roles = list(db.scalars(select(models.Role).where(models.Role.id.in_(role_ids))))
        if len(roles) != len(role_ids):
            raise ValueError('Role not found')

    user.roles = roles
    db.commit()
    db.refresh(user)
    return user
