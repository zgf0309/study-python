# JSONResponse: 返回统一 JSON 响应对象。
from fastapi.responses import JSONResponse


def api_response(
    *,
    code: int = 200,
    data: object = None,
    message: str = '',
    **extra: object,
) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        content={
            'code': code,
            'data': {
                'data': data,
                **extra, 
            },
            'message': message,
           
        },
    )