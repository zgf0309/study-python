# 标注查询语句对象的类型。
from sqlalchemy import Select
# 构造 ORM 查询语句。
from sqlalchemy import select
# 表示当前 CRUD 使用的数据库会话类型。
from sqlalchemy.orm import Session

# models: 菜单、用户等 ORM 模型定义模块。
# schemas: 菜单相关的数据传输结构模块。
from .. import models, schemas


def list_menus(
    db: Session,
    *,
    name: str | None = None,
    status: str | None = None,
) -> list[models.Menu]:
    statement: Select[tuple[models.Menu]] = select(models.Menu)

    if name:
        statement = statement.where(models.Menu.name.ilike(f'%{name}%'))

    if status:
        statement = statement.where(models.Menu.status == status)

    statement = statement.order_by(models.Menu.sort.asc(), models.Menu.id.asc())
    return list(db.scalars(statement))


def get_menu(db: Session, menu_id: int) -> models.Menu | None:
    return db.get(models.Menu, menu_id)


def create_menu(db: Session, payload: schemas.MenuCreate) -> models.Menu:
    menu = models.Menu(**payload.model_dump())
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


def update_menu(db: Session, payload: schemas.MenuUpdate) -> models.Menu:
    menu = db.get(models.Menu, payload.id)
    if not menu:
        raise ValueError('Menu not found')
    for key, value in payload.model_dump().items():
        setattr(menu, key, value)
    db.commit()
    db.refresh(menu)
    return menu


def delete_menu(db: Session, menu_id: int) -> bool:
    menu = db.get(models.Menu, menu_id)
    if not menu:
        return False
    db.delete(menu)
    db.commit()
    return True

