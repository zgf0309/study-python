# asdict: 将数据类对象转换成字典。
from dataclasses import asdict
# dataclass: 声明轻量级用户数据结构。
from dataclasses import dataclass
# datetime: 表示用户创建时间字段类型。
from datetime import datetime


@dataclass(slots=True)
class UserCreate:
    name: str
    email: str
    role: str = 'viewer'

    def model_dump(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class UserUpdate:
    id: int
    name: str
    email: str
    role: str = 'viewer'

    def model_dump(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(slots=True)
class UserRead:
    id: int
    name: str
    email: str
    role: str
    role_ids: list[int]
    created_at: datetime | None

    def to_dict(self) -> dict[str, str | int | list[int] | None]:
        payload = asdict(self)
        payload['created_at'] = self.created_at.isoformat() if self.created_at else None
        return payload


def serialize_user(user: object) -> dict[str, str | int | list[int] | None]:
    return UserRead(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        role_ids=[role.id for role in user.roles],
        created_at=user.created_at,
    ).to_dict()
