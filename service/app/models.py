# datetime: 表示模型中的时间字段类型。
from datetime import datetime
# Optional: 表示字段可以为空的类型提示。
from typing import Optional

# 定义数据库中的日期时间字段类型。
from sqlalchemy import DateTime
# 定义多对多关联表。
from sqlalchemy import Column
# 定义表之间的外键约束。
from sqlalchemy import ForeignKey
# 定义字符串字段类型及长度。
from sqlalchemy import String
# 定义普通表结构对象。
from sqlalchemy import Table
# 提供数据库函数，如当前时间 func.now()。
from sqlalchemy import func
# 为模型字段提供类型化映射声明。
from sqlalchemy.orm import Mapped, relationship
# 定义 ORM 模型中的列配置。
from sqlalchemy.orm import mapped_column

# Base: 所有数据模型共享的声明式基类。
from .database import Base




class UserRoles(Base):
    # 用户角色关联表模型，保存用户角色关联信息。
    __tablename__ = 'user_roles'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)

class RoleMenus(Base):
    # 角色菜单关联表模型，保存角色菜单关联信息。
    __tablename__ = 'role_menus'
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey('menus.id', ondelete='CASCADE'), primary_key=True)

class User(Base):
    # 用户表模型，保存账号基础信息。
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default='viewer')
    roles: Mapped[list['Role']] = relationship(
        secondary='user_roles',
        back_populates='users',
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

class Role(Base):
    # 角色表模型，保存用户角色信息。
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sort: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='enabled')
    users: Mapped[list[User]] = relationship(
        secondary='user_roles',
        back_populates='roles',
    )
    menus: Mapped[list[Menu]] = relationship(
        secondary='role_menus',
        back_populates='roles',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

class Menu(Base):
    # 菜单表模型，保存前端菜单配置与所属用户关联。
    __tablename__ = 'menus'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    path: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    icon: Mapped[str] = mapped_column(String(100), nullable=False, default='appstore')
    sort: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='enabled')
    roles: Mapped[list[Role]] = relationship(
        secondary='role_menus',
        back_populates='menus',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

