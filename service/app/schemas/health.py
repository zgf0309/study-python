# asdict: 将数据类对象转换成字典。
from dataclasses import asdict
# dataclass: 声明健康检查响应的数据结构。
from dataclasses import dataclass


@dataclass(slots=True)
class HealthResponse:
    service: str
    status: str
    database: str
    frontend_to_backend: str
    backend_to_database: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
