from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from .. import models, schemas


def list_menus(
    db: Session,
    *,
    user_id: int | None = None,
    name: str | None = None,
    status: str | None = None,
) -> list[models.Menu]:
    statement: Select[tuple[models.Menu]] = select(models.Menu)

    if user_id is not None:
        statement = statement.join(models.User, models.Menu.user_id == models.User.id).where(
            models.User.id == user_id
        )

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


def seed_menus(db: Session) -> None:
    if list_menus(db):
        return

    first_user = select(models.User).order_by(models.User.id.asc()).limit(1)
    default_user_id = db.scalar(first_user)
    default_user_id = default_user_id.id if default_user_id else None

    demo_menus = [
        schemas.MenuCreate(
            user_id=default_user_id,
            name='系统首页',
            path='/dashboard',
            icon='dashboard',
            sort=1,
            status='enabled',
        ),
        schemas.MenuCreate(
            user_id=default_user_id,
            name='用户管理',
            path='/users',
            icon='user',
            sort=2,
            status='enabled',
        ),
    ]
    for item in demo_menus:
        create_menu(db, item)
