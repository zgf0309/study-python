from dataclasses import asdict, dataclass
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
    created_at: datetime | None

    def to_dict(self) -> dict[str, str | int]:
        payload = asdict(self)
        payload['created_at'] = self.created_at.isoformat() if self.created_at else None
        return payload


def serialize_user(user: object) -> dict[str, str | int]:
    return UserRead(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
    ).to_dict()
