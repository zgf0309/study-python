from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass(slots=True)
class MenuCreate:
    name: str
    path: str
    user_id: int | None = None
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
    user_id: int | None = None
    icon: str = 'appstore'
    sort: int = 0
    status: str = 'enabled'

    def model_dump(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(slots=True)
class MenuRead:
    id: int
    user_id: int | None
    name: str
    path: str
    icon: str
    sort: int
    status: str
    created_at: datetime | None
    
    def to_dict(self) -> dict[str, str | int]:
        payload = asdict(self)
        payload['created_at'] = self.created_at.isoformat() if self.created_at else None
        return payload


def serialize_menu(menu: object) -> dict[str, str | int]:
    return MenuRead(
        id=menu.id,
        user_id=menu.user_id,
        name=menu.name,
        path=menu.path,
        icon=menu.icon,
        sort=menu.sort,
        status=menu.status,
        created_at=menu.created_at,
    ).to_dict()
