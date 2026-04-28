# asdict: 将数据类对象转换成字典。
from dataclasses import asdict
# dataclass: 声明轻量级菜单数据结构。
from dataclasses import dataclass
# datetime: 表示菜单创建时间字段类型。
from datetime import datetime


@dataclass(slots=True)
class MenuCreate:
    name: str
    path: str
    icon: str = 'appstore'
    sort: int = 0
    status: str = 'enabled'

    def model_dump(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(slots=True)
class MenuUpdate:
    id: int
    name: str
    path: str
    icon: str = 'appstore'
    sort: int = 0
    status: str = 'enabled'

    def model_dump(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(slots=True)
class MenuRead:
    id: int
    name: str
    path: str
    icon: str
    sort: int
    role_ids: list[int]
    status: str
    created_at: datetime | None
    
    def to_dict(self) -> dict[str, str | int]:
        payload = asdict(self)
        payload['created_at'] = self.created_at.isoformat() if self.created_at else None
        return payload


def serialize_menu(menu: object) -> dict[str, str | int]:
    return MenuRead(
        id=menu.id,
        name=menu.name,
        path=menu.path,
        icon=menu.icon,
        sort=menu.sort,
        status=menu.status,
        role_ids=[role.id for role in menu.roles],
        created_at=menu.created_at,
    ).to_dict()
