from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas


def list_users(db: Session) -> list[models.User]:
    statement = select(models.User).order_by(models.User.id.desc())
    return list(db.scalars(statement))


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


def seed_users(db: Session) -> None:
    if list_users(db):
        return

    demo_users = [
        schemas.UserCreate(name='张三', email='zhangsan@example.com', role='admin'),
        schemas.UserCreate(name='李四', email='lisi@example.com', role='viewer'),
    ]
    for item in demo_users:
        create_user(db, item)
