# asdict: 将数据类对象转换成字典。
from dataclasses import asdict
# dataclass: 声明轻量级菜单数据结构。
from dataclasses import dataclass
# datetime: 表示菜单创建时间字段类型。
from datetime import datetime



@dataclass(slots=True)
class RoleCreate:
    name: str
    description: str
    id: int | None = None
    sort: int = 0
    status: str = 'enabled'

    def model_dump(self) -> dict[str, str | int]:
        return asdict(self)
    
@dataclass(slots=True)
class RoleUpdate:
    id: int
    name: str
    description: str
    sort: int = 0
    status: str = 'enabled'

    def model_dump(self) -> dict[str, str | int]:
        return asdict(self)
    
@dataclass(slots=True)
class RoleRead:
    id: int
    name: str
    description: str
    sort: int
    # user_ids: list[int]
    status: str
    created_at: datetime | None 
    def to_dict(self) -> dict[str, str | int]:
        payload = asdict(self)
        payload['created_at'] = self.created_at.isoformat() if self.created_at else None
        return payload
def serialize_role(role: object) -> dict[str, str | int]:
    return RoleRead(
        id=role.id,
        name=role.name,
        description=role.description,
        sort=role.sort,
        # user_ids=[ user.id for user in role.users ],
        status=role.status,
        created_at=role.created_at,
    ).to_dict()
