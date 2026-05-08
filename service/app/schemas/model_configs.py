# asdict: 将数据类对象转换成字典。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from dataclasses import asdict, dataclass
# 中文注释：从指定模块导入当前文件需要使用的对象。
from datetime import datetime


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@dataclass(slots=True)
# 中文注释：定义 ModelConfigCreate 类，用于组织相关数据或业务逻辑。
class ModelConfigCreate:
    # 中文注释：执行当前代码行对应的业务逻辑。
    name: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    base_url: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    model_name: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    api_key: str
    # 中文注释：设置变量或字段 provider: str 的值，供后续逻辑使用。
    provider: str = 'openai-compatible'
    # 中文注释：设置变量或字段 is_default: bool 的值，供后续逻辑使用。
    is_default: bool = False
    # 中文注释：设置变量或字段 status: str 的值，供后续逻辑使用。
    status: str = 'enabled'

    # 中文注释：定义函数 model_dump，封装一段可复用的业务逻辑。
    def model_dump(self) -> dict[str, str | bool]:
        # 中文注释：返回当前函数处理后的结果。
        return asdict(self)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@dataclass(slots=True)
# 中文注释：定义 ModelConfigRead 类，用于组织相关数据或业务逻辑。
class ModelConfigRead:
    # 中文注释：执行当前代码行对应的业务逻辑。
    id: int
    # 中文注释：执行当前代码行对应的业务逻辑。
    name: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    base_url: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    model_name: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    provider: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    is_default: bool
    # 中文注释：执行当前代码行对应的业务逻辑。
    status: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    created_at: datetime | None

    # 中文注释：定义函数 to_dict，封装一段可复用的业务逻辑。
    def to_dict(self) -> dict[str, str | int | bool | None]:
        # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
        payload = asdict(self)
        # 中文注释：设置变量或字段 payload['created_at'] 的值，供后续逻辑使用。
        payload['created_at'] = self.created_at.isoformat() if self.created_at else None
        # 中文注释：返回当前函数处理后的结果。
        return payload


# 中文注释：定义函数 serialize_model_config，封装一段可复用的业务逻辑。
def serialize_model_config(config: object) -> dict[str, str | int | bool | None]:
    # 中文注释：返回当前函数处理后的结果。
    return ModelConfigRead(
        # 中文注释：设置变量或字段 id 的值，供后续逻辑使用。
        id=config.id,
        # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
        name=config.name,
        # 中文注释：设置变量或字段 base_url 的值，供后续逻辑使用。
        base_url=config.base_url,
        # 中文注释：设置变量或字段 model_name 的值，供后续逻辑使用。
        model_name=config.model_name,
        # 中文注释：设置变量或字段 provider 的值，供后续逻辑使用。
        provider=config.provider,
        # 中文注释：设置变量或字段 is_default 的值，供后续逻辑使用。
        is_default=bool(config.is_default),
        # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
        status=config.status,
        # 中文注释：设置变量或字段 created_at 的值，供后续逻辑使用。
        created_at=config.created_at,
    # 中文注释：调用函数或方法，执行对应的业务处理。
    ).to_dict()
