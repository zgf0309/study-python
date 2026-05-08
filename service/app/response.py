# JSONResponse: 返回统一 JSON 响应对象。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi.responses import JSONResponse


# 中文注释：定义函数 api_response，封装一段可复用的业务逻辑。
def api_response(
    # 中文注释：执行当前代码行对应的业务逻辑。
    *,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    code: int = 200,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    data: object = None,
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    message: str = '',
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    **extra: object,
# 中文注释：执行当前代码行对应的业务逻辑。
) -> JSONResponse:
    # 中文注释：返回当前函数处理后的结果。
    return JSONResponse(
        # 中文注释：设置变量或字段 status_code 的值，供后续逻辑使用。
        status_code=code,
        # 中文注释：开始定义多行数据结构或多行参数。
        content={
            # 中文注释：设置字典、响应体或配置项中的一个字段。
            'code': code,
            # 中文注释：开始定义多行数据结构或多行参数。
            'data': {
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'data': data,
                # 中文注释：执行当前代码行对应的业务逻辑。
                **extra, 
            # 中文注释：结束当前多行数据结构或多行参数。
            },
            # 中文注释：设置字典、响应体或配置项中的一个字段。
            'message': message,
           
        # 中文注释：结束当前多行数据结构或多行参数。
        },
    # 中文注释：结束当前多行数据结构或多行参数。
    )