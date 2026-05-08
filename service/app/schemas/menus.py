# asdict: 将数据类对象转换成字典。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from dataclasses import asdict
# dataclass: 声明轻量级菜单数据结构。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from dataclasses import dataclass
# datetime: 表示菜单创建时间字段类型。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from datetime import datetime


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@dataclass(slots=True)
# 中文注释：定义 MenuCreate 类，用于组织相关数据或业务逻辑。
class MenuCreate:
    # 中文注释：执行当前代码行对应的业务逻辑。
    name: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    path: str
    # 中文注释：设置变量或字段 icon: str 的值，供后续逻辑使用。
    icon: str = 'appstore'
    # 中文注释：设置变量或字段 sort: int 的值，供后续逻辑使用。
    sort: int = 0
    # 中文注释：设置变量或字段 status: str 的值，供后续逻辑使用。
    status: str = 'enabled'

    # 中文注释：定义函数 model_dump，封装一段可复用的业务逻辑。
    def model_dump(self) -> dict[str, str | int]:
        # 中文注释：返回当前函数处理后的结果。
        return asdict(self)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@dataclass(slots=True)
# 中文注释：定义 MenuUpdate 类，用于组织相关数据或业务逻辑。
class MenuUpdate:
    # 中文注释：执行当前代码行对应的业务逻辑。
    id: int
    # 中文注释：执行当前代码行对应的业务逻辑。
    name: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    path: str
    # 中文注释：设置变量或字段 icon: str 的值，供后续逻辑使用。
    icon: str = 'appstore'
    # 中文注释：设置变量或字段 sort: int 的值，供后续逻辑使用。
    sort: int = 0
    # 中文注释：设置变量或字段 status: str 的值，供后续逻辑使用。
    status: str = 'enabled'

    # 中文注释：定义函数 model_dump，封装一段可复用的业务逻辑。
    def model_dump(self) -> dict[str, str | int]:
        # 中文注释：返回当前函数处理后的结果。
        return asdict(self)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@dataclass(slots=True)
# 中文注释：定义 MenuRead 类，用于组织相关数据或业务逻辑。
class MenuRead:
    # 中文注释：执行当前代码行对应的业务逻辑。
    id: int
    # 中文注释：执行当前代码行对应的业务逻辑。
    name: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    path: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    icon: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    sort: int
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    role_ids: list[int]
    # 中文注释：执行当前代码行对应的业务逻辑。
    status: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    created_at: datetime | None
    
    # 中文注释：定义函数 to_dict，封装一段可复用的业务逻辑。
    def to_dict(self) -> dict[str, str | int]:
        # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
        payload = asdict(self)
        # 中文注释：设置变量或字段 payload['created_at'] 的值，供后续逻辑使用。
        payload['created_at'] = self.created_at.isoformat() if self.created_at else None
        # 中文注释：返回当前函数处理后的结果。
        return payload


# 中文注释：定义函数 serialize_menu，封装一段可复用的业务逻辑。
def serialize_menu(menu: object) -> dict[str, str | int]:
    # 中文注释：返回当前函数处理后的结果。
    return MenuRead(
        # 中文注释：设置变量或字段 id 的值，供后续逻辑使用。
        id=menu.id,
        # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
        name=menu.name,
        # 中文注释：设置变量或字段 path 的值，供后续逻辑使用。
        path=menu.path,
        # 中文注释：设置变量或字段 icon 的值，供后续逻辑使用。
        icon=menu.icon,
        # 中文注释：设置变量或字段 sort 的值，供后续逻辑使用。
        sort=menu.sort,
        # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
        status=menu.status,
        # 中文注释：设置变量或字段 role_ids 的值，供后续逻辑使用。
        role_ids=[role.id for role in menu.roles],
        # 中文注释：设置变量或字段 created_at 的值，供后续逻辑使用。
        created_at=menu.created_at,
    # 中文注释：调用函数或方法，执行对应的业务处理。
    ).to_dict()
