# datetime: 表示模型中的时间字段类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from datetime import datetime
# Optional: 表示字段可以为空的类型提示。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from typing import Optional

# 定义数据库中的日期时间字段类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import DateTime
# 定义多对多关联表。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import Column
# 定义表之间的外键约束。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import ForeignKey
# 定义字符串字段类型及长度。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import String
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import Boolean
from sqlalchemy import Text
# 定义普通表结构对象。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import Table
# 提供数据库函数，如当前时间 func.now()。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import func
# 为模型字段提供类型化映射声明。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.orm import Mapped, relationship
# 定义 ORM 模型中的列配置。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.orm import mapped_column

# Base: 所有数据模型共享的声明式基类。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from .database import Base




# 中文注释：定义 UserRoles 类，用于组织相关数据或业务逻辑。
class UserRoles(Base):
    # 用户角色关联表模型，保存用户角色关联信息。
    # 中文注释：设置变量或字段 __tablename__ 的值，供后续逻辑使用。
    __tablename__ = 'user_roles'
    # 中文注释：设置变量或字段 user_id: Mapped[int] 的值，供后续逻辑使用。
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    # 中文注释：设置变量或字段 role_id: Mapped[int] 的值，供后续逻辑使用。
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)

# 中文注释：定义 RoleMenus 类，用于组织相关数据或业务逻辑。
class RoleMenus(Base):
    # 角色菜单关联表模型，保存角色菜单关联信息。
    # 中文注释：设置变量或字段 __tablename__ 的值，供后续逻辑使用。
    __tablename__ = 'role_menus'
    # 中文注释：设置变量或字段 role_id: Mapped[int] 的值，供后续逻辑使用。
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    # 中文注释：设置变量或字段 menu_id: Mapped[int] 的值，供后续逻辑使用。
    menu_id: Mapped[int] = mapped_column(ForeignKey('menus.id', ondelete='CASCADE'), primary_key=True)

# 中文注释：定义 User 类，用于组织相关数据或业务逻辑。
class User(Base):
    # 用户表模型，保存账号基础信息。
    # 中文注释：设置变量或字段 __tablename__ 的值，供后续逻辑使用。
    __tablename__ = 'users'

    # 中文注释：设置变量或字段 id: Mapped[int] 的值，供后续逻辑使用。
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # 中文注释：设置变量或字段 name: Mapped[str] 的值，供后续逻辑使用。
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 中文注释：设置变量或字段 email: Mapped[str] 的值，供后续逻辑使用。
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    # 中文注释：设置变量或字段 role: Mapped[str] 的值，供后续逻辑使用。
    role: Mapped[str] = mapped_column(String(50), nullable=False, default='viewer')
    # 中文注释：设置变量或字段 roles: Mapped[list['Role']] 的值，供后续逻辑使用。
    roles: Mapped[list['Role']] = relationship(
        # 中文注释：设置变量或字段 secondary 的值，供后续逻辑使用。
        secondary='user_roles',
        # 中文注释：设置变量或字段 back_populates 的值，供后续逻辑使用。
        back_populates='users',
    # 中文注释：结束当前多行数据结构或多行参数。
    )

    # 中文注释：设置变量或字段 created_at: Mapped[datetime] 的值，供后续逻辑使用。
    created_at: Mapped[datetime] = mapped_column(
        # 中文注释：设置变量或字段 DateTime(timezone 的值，供后续逻辑使用。
        DateTime(timezone=True),
        # 中文注释：设置变量或字段 server_default 的值，供后续逻辑使用。
        server_default=func.now(),
        # 中文注释：设置变量或字段 nullable 的值，供后续逻辑使用。
        nullable=False,
    # 中文注释：结束当前多行数据结构或多行参数。
    )

# 中文注释：定义 Role 类，用于组织相关数据或业务逻辑。
class Role(Base):
    # 角色表模型，保存用户角色信息。
    # 中文注释：设置变量或字段 __tablename__ 的值，供后续逻辑使用。
    __tablename__ = 'roles'

    # 中文注释：设置变量或字段 id: Mapped[int] 的值，供后续逻辑使用。
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # 中文注释：设置变量或字段 name: Mapped[str] 的值，供后续逻辑使用。
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 中文注释：设置变量或字段 description: Mapped[str] 的值，供后续逻辑使用。
    description: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # 中文注释：设置变量或字段 sort: Mapped[int] 的值，供后续逻辑使用。
    sort: Mapped[int] = mapped_column(nullable=False, default=0)
    # 中文注释：设置变量或字段 status: Mapped[str] 的值，供后续逻辑使用。
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='enabled')
    # 中文注释：设置变量或字段 users: Mapped[list[User]] 的值，供后续逻辑使用。
    users: Mapped[list[User]] = relationship(
        # 中文注释：设置变量或字段 secondary 的值，供后续逻辑使用。
        secondary='user_roles',
        # 中文注释：设置变量或字段 back_populates 的值，供后续逻辑使用。
        back_populates='roles',
    # 中文注释：结束当前多行数据结构或多行参数。
    )
    # 中文注释：设置变量或字段 menus: Mapped[list[Menu]] 的值，供后续逻辑使用。
    menus: Mapped[list[Menu]] = relationship(
        # 中文注释：设置变量或字段 secondary 的值，供后续逻辑使用。
        secondary='role_menus',
        # 中文注释：设置变量或字段 back_populates 的值，供后续逻辑使用。
        back_populates='roles',
    # 中文注释：结束当前多行数据结构或多行参数。
    )
    # 中文注释：设置变量或字段 created_at: Mapped[datetime] 的值，供后续逻辑使用。
    created_at: Mapped[datetime] = mapped_column(
        # 中文注释：设置变量或字段 DateTime(timezone 的值，供后续逻辑使用。
        DateTime(timezone=True),
        # 中文注释：设置变量或字段 server_default 的值，供后续逻辑使用。
        server_default=func.now(),
        # 中文注释：设置变量或字段 nullable 的值，供后续逻辑使用。
        nullable=False,
    # 中文注释：结束当前多行数据结构或多行参数。
    )

# 中文注释：定义 Menu 类，用于组织相关数据或业务逻辑。
class Menu(Base):
    # 菜单表模型，保存前端菜单配置与所属用户关联。
    # 中文注释：设置变量或字段 __tablename__ 的值，供后续逻辑使用。
    __tablename__ = 'menus'

    # 中文注释：设置变量或字段 id: Mapped[int] 的值，供后续逻辑使用。
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # 中文注释：设置变量或字段 name: Mapped[str] 的值，供后续逻辑使用。
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 中文注释：设置变量或字段 path: Mapped[str] 的值，供后续逻辑使用。
    path: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    # 中文注释：设置变量或字段 icon: Mapped[str] 的值，供后续逻辑使用。
    icon: Mapped[str] = mapped_column(String(100), nullable=False, default='appstore')
    # 中文注释：设置变量或字段 sort: Mapped[int] 的值，供后续逻辑使用。
    sort: Mapped[int] = mapped_column(nullable=False, default=0)
    # 中文注释：设置变量或字段 status: Mapped[str] 的值，供后续逻辑使用。
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='enabled')
    # 中文注释：设置变量或字段 roles: Mapped[list[Role]] 的值，供后续逻辑使用。
    roles: Mapped[list[Role]] = relationship(
        # 中文注释：设置变量或字段 secondary 的值，供后续逻辑使用。
        secondary='role_menus',
        # 中文注释：设置变量或字段 back_populates 的值，供后续逻辑使用。
        back_populates='menus',
    # 中文注释：结束当前多行数据结构或多行参数。
    )
    # 中文注释：设置变量或字段 created_at: Mapped[datetime] 的值，供后续逻辑使用。
    created_at: Mapped[datetime] = mapped_column(
        # 中文注释：设置变量或字段 DateTime(timezone 的值，供后续逻辑使用。
        DateTime(timezone=True),
        # 中文注释：设置变量或字段 server_default 的值，供后续逻辑使用。
        server_default=func.now(),
        # 中文注释：设置变量或字段 nullable 的值，供后续逻辑使用。
        nullable=False,
    # 中文注释：结束当前多行数据结构或多行参数。
    )


# 中文注释：定义 LLMModelConfig 类，用于组织相关数据或业务逻辑。
class LLMModelConfig(Base):
    # 大模型配置表，保存 OpenAI 兼容模型服务的连接信息。
    # 中文注释：设置变量或字段 __tablename__ 的值，供后续逻辑使用。
    __tablename__ = 'llm_model_configs'

    # 中文注释：设置变量或字段 id: Mapped[int] 的值，供后续逻辑使用。
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # 中文注释：设置变量或字段 name: Mapped[str] 的值，供后续逻辑使用。
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 中文注释：设置变量或字段 base_url: Mapped[str] 的值，供后续逻辑使用。
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    # 中文注释：设置变量或字段 model_name: Mapped[str] 的值，供后续逻辑使用。
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # 中文注释：设置变量或字段 api_key: Mapped[str] 的值，供后续逻辑使用。
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    # 中文注释：设置变量或字段 provider: Mapped[str] 的值，供后续逻辑使用。
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default='openai-compatible')
    # 中文注释：设置变量或字段 is_default: Mapped[bool] 的值，供后续逻辑使用。
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # 中文注释：设置变量或字段 status: Mapped[str] 的值，供后续逻辑使用。
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='enabled')
    # 中文注释：设置变量或字段 created_at: Mapped[datetime] 的值，供后续逻辑使用。
    created_at: Mapped[datetime] = mapped_column(
        # 中文注释：设置变量或字段 DateTime(timezone 的值，供后续逻辑使用。
        DateTime(timezone=True),
        # 中文注释：设置变量或字段 server_default 的值，供后续逻辑使用。
        server_default=func.now(),
        # 中文注释：设置变量或字段 nullable 的值，供后续逻辑使用。
        nullable=False,
    # 中文注释：结束当前多行数据结构或多行参数。
    )


class KnowledgeBase(Base):
    # 知识库表，文件切片向量化时可关联到指定知识库。
    __tablename__ = 'knowledge_bases'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='enabled')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    files: Mapped[list['KnowledgeFile']] = relationship(back_populates='knowledge_base')


class KnowledgeFile(Base):
    # MinIO 文件处理记录表，保存文件列表和切片向量化状态。
    __tablename__ = 'knowledge_files'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    bucket: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    object_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    knowledge_base_id: Mapped[Optional[int]] = mapped_column(ForeignKey('knowledge_bases.id', ondelete='SET NULL'), nullable=True, index=True)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False, default='application/octet-stream')
    size: Mapped[int] = mapped_column(nullable=False, default=0)
    chunk_size: Mapped[int] = mapped_column(nullable=False, default=500)
    chunk_overlap: Mapped[int] = mapped_column(nullable=False, default=80)
    chunk_count: Mapped[int] = mapped_column(nullable=False, default=0)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False, default='')
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='completed')
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    chunks: Mapped[list['KnowledgeFileChunk']] = relationship(
        back_populates='file',
        cascade='all, delete-orphan',
    )
    knowledge_base: Mapped[Optional[KnowledgeBase]] = relationship(back_populates='files')


class KnowledgeFileChunk(Base):
    # 文件切片向量表，保存每个切片文本及其向量 JSON。
    __tablename__ = 'knowledge_file_chunks'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey('knowledge_files.id', ondelete='CASCADE'), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    start: Mapped[int] = mapped_column(nullable=False, default=0)
    end: Mapped[int] = mapped_column(nullable=False, default=0)
    length: Mapped[int] = mapped_column(nullable=False, default=0)
    embedding: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    embedding_dim: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    file: Mapped[KnowledgeFile] = relationship(back_populates='chunks')
