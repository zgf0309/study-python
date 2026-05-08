# 中文注释：导入当前文件需要使用的 Python 模块。
from collections.abc import Iterable


# 中文注释：定义函数 clean_string，封装一段可复用的业务逻辑。
def clean_string(value: object, default: str = '') -> str:
    # 将前端传入的任意值安全转换为去除首尾空格的字符串，避免每个路由重复写 str(...).strip()。
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if value is None:
        # 中文注释：返回当前函数处理后的结果。
        return default
    # 中文注释：返回当前函数处理后的结果。
    return str(value).strip()


# 中文注释：定义函数 parse_int，封装一段可复用的业务逻辑。
def parse_int(value: object, default: int = 0) -> int:
    # 将请求参数安全转换成整数；转换失败时返回默认值，避免接口因为 ValueError 直接变成 500。
    # 中文注释：开始执行可能抛出异常的代码块。
    try:
        # 中文注释：返回当前函数处理后的结果。
        return int(value)
    # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
    except (TypeError, ValueError):
        # 中文注释：返回当前函数处理后的结果。
        return default


# 中文注释：定义函数 dedupe_int_ids，封装一段可复用的业务逻辑。
def dedupe_int_ids(values: Iterable[object] | None) -> list[int]:
    # 对 ID 列表做“转整数 + 去重 + 保持原顺序”，方便关联角色、菜单等多对多关系。
    # 中文注释：设置变量或字段 result 的值，供后续逻辑使用。
    result: list[int] = []
    # 中文注释：设置变量或字段 seen 的值，供后续逻辑使用。
    seen: set[int] = set()
    # 中文注释：遍历集合中的每一项，并逐项执行下面的代码块。
    for value in values or []:
        # 中文注释：设置变量或字段 item_id 的值，供后续逻辑使用。
        item_id = parse_int(value)
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if item_id <= 0 or item_id in seen:
            # 中文注释：跳过本轮循环，继续处理下一项。
            continue
        # 中文注释：调用函数或方法，执行对应的业务处理。
        seen.add(item_id)
        # 中文注释：调用函数或方法，执行对应的业务处理。
        result.append(item_id)
    # 中文注释：返回当前函数处理后的结果。
    return result
