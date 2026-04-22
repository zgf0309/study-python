from dataclasses import asdict, dataclass


@dataclass(slots=True)
class HealthResponse:
    service: str
    status: str
    database: str
    frontend_to_backend: str
    backend_to_database: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
