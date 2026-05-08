# 中文注释：导入当前文件需要使用的 Python 模块。
import json
# 中文注释：导入当前文件需要使用的 Python 模块。
import time
# 中文注释：从指定模块导入当前文件需要使用的对象。
from typing import Any

# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi import APIRouter, Body, HTTPException, status
# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi.responses import StreamingResponse

# 中文注释：从指定模块导入当前文件需要使用的对象。
from .. import crud, schemas
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..database import SessionLocal
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..llm import ChatMessage, LLMClientError, OpenAICompatibleEmbeddingClient, OpenAICompatibleLLMClient
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..response import api_response

# 中文注释：设置变量或字段 model_configs_router 的值，供后续逻辑使用。
model_configs_router = APIRouter()


# 中文注释：定义函数 split_text_into_chunks，封装一段可复用的业务逻辑。
def split_text_into_chunks(text: str, *, chunk_size: int = 500, chunk_overlap: int = 80) -> list[dict[str, int | str]]:
    # 将长文本按固定字符长度切片，并保留一定重叠，便于后续检索时保留上下文。
    # 中文注释：设置变量或字段 normalized_text 的值，供后续逻辑使用。
    normalized_text = text.strip()
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not normalized_text:
        # 中文注释：返回当前函数处理后的结果。
        return []

    # 中文注释：设置字典、响应体或配置项中的一个字段。
    chunks: list[dict[str, int | str]] = []
    # 中文注释：设置变量或字段 start 的值，供后续逻辑使用。
    start = 0
    # 中文注释：设置变量或字段 index 的值，供后续逻辑使用。
    index = 0
    # 中文注释：设置变量或字段 text_length 的值，供后续逻辑使用。
    text_length = len(normalized_text)
    # 中文注释：设置变量或字段 step 的值，供后续逻辑使用。
    step = max(chunk_size - chunk_overlap, 1)

    # 中文注释：当循环条件成立时，持续执行下面的代码块。
    while start < text_length:
        # 中文注释：设置变量或字段 end 的值，供后续逻辑使用。
        end = min(start + chunk_size, text_length)
        # 中文注释：设置变量或字段 content 的值，供后续逻辑使用。
        content = normalized_text[start:end].strip()
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if content:
            # 中文注释：执行当前代码行对应的业务逻辑。
            chunks.append(
                # 中文注释：开始定义多行数据结构或多行参数。
                {
                    # 中文注释：设置字典、响应体或配置项中的一个字段。
                    'index': index,
                    # 中文注释：设置字典、响应体或配置项中的一个字段。
                    'content': content,
                    # 中文注释：设置字典、响应体或配置项中的一个字段。
                    'start': start,
                    # 中文注释：设置字典、响应体或配置项中的一个字段。
                    'end': end,
                    # 中文注释：设置字典、响应体或配置项中的一个字段。
                    'length': len(content),
                # 中文注释：结束当前多行数据结构或多行参数。
                }
            # 中文注释：结束当前多行数据结构或多行参数。
            )
            # 中文注释：设置变量或字段 index + 的值，供后续逻辑使用。
            index += 1
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if end >= text_length:
            # 中文注释：终止当前循环。
            break
        # 中文注释：设置变量或字段 start + 的值，供后续逻辑使用。
        start += step

    # 中文注释：返回当前函数处理后的结果。
    return chunks


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@model_configs_router.get('/models')
# 中文注释：定义函数 read_models，封装一段可复用的业务逻辑。
def read_models():
    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 configs 的值，供后续逻辑使用。
        configs = crud.list_model_configs(db, enabled_only=True)
        # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
        payload = [schemas.serialize_model_config(config) for config in configs]
    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=payload)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@model_configs_router.post('/models', status_code=status.HTTP_201_CREATED)
# 中文注释：定义函数 add_model，封装一段可复用的业务逻辑。
def add_model(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
    name = str(data.get('name', '')).strip()
    # 中文注释：设置变量或字段 base_url 的值，供后续逻辑使用。
    base_url = str(data.get('base_url', '')).strip().rstrip('/')
    # 中文注释：设置变量或字段 model_name 的值，供后续逻辑使用。
    model_name = str(data.get('model_name', '')).strip()
    # 中文注释：设置变量或字段 api_key 的值，供后续逻辑使用。
    api_key = str(data.get('api_key', '')).strip()
    # 中文注释：设置变量或字段 provider 的值，供后续逻辑使用。
    provider = str(data.get('provider', 'openai-compatible')).strip() or 'openai-compatible'
    # 中文注释：设置变量或字段 is_default 的值，供后续逻辑使用。
    is_default = bool(data.get('is_default', False))
    # 中文注释：设置变量或字段 status_value 的值，供后续逻辑使用。
    status_value = str(data.get('status', 'enabled')).strip() or 'enabled'

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not name:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='模型名称不能为空。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not base_url.startswith(('http://', 'https://')):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='base_url 必须是 http 或 https 地址。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not model_name:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='model_name 不能为空。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not api_key:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='api_key 不能为空。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if provider not in ('openai-compatible', 'openai-compatible-embedding'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='当前仅支持 openai-compatible 或 openai-compatible-embedding 模型服务。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if provider == 'openai-compatible-embedding' and is_default:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='向量模型不能设置为默认对话模型。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if status_value not in ('enabled', 'disabled'):
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='状态只能是 enabled 或 disabled。')

    # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
    payload = schemas.ModelConfigCreate(
        # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
        name=name,
        # 中文注释：设置变量或字段 base_url 的值，供后续逻辑使用。
        base_url=base_url,
        # 中文注释：设置变量或字段 model_name 的值，供后续逻辑使用。
        model_name=model_name,
        # 中文注释：设置变量或字段 api_key 的值，供后续逻辑使用。
        api_key=api_key,
        # 中文注释：设置变量或字段 provider 的值，供后续逻辑使用。
        provider=provider,
        # 中文注释：设置变量或字段 is_default 的值，供后续逻辑使用。
        is_default=is_default,
        # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
        status=status_value,
    # 中文注释：结束当前多行数据结构或多行参数。
    )
    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 config 的值，供后续逻辑使用。
        config = crud.create_model_config(db, payload)
        # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
        response_data = schemas.serialize_model_config(config)
    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data, message='模型配置已创建。')


# 中文注释：定义函数 _sse_error，封装一段可复用的业务逻辑。
def _sse_error(message: str, *, model_name: str = '') -> str:
    # 中文注释：开始定义多行数据结构或多行参数。
    chunk = {
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        'id': f'chatcmpl-error-{int(time.time())}',
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        'object': 'chat.completion.chunk',
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        'created': int(time.time()),
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        'model': model_name,
        # 中文注释：执行当前代码行对应的业务逻辑。
        'choices': [
            # 中文注释：开始定义多行数据结构或多行参数。
            {
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'index': 0,
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'delta': {'role': 'assistant', 'content': ''},
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'finish_reason': 'error',
            # 中文注释：结束当前多行数据结构或多行参数。
            }
        # 中文注释：结束当前多行数据结构或多行参数。
        ],
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        'error': {'message': message, 'type': 'llm_error'},
    # 中文注释：结束当前多行数据结构或多行参数。
    }
    # 中文注释：返回当前函数处理后的结果。
    return f'data: {json.dumps(chunk, ensure_ascii=False)}\n\n'


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@model_configs_router.post('/chat/stream')
# 中文注释：定义函数 stream_chat，封装一段可复用的业务逻辑。
def stream_chat(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 raw_messages 的值，供后续逻辑使用。
    raw_messages = data.get('messages', [])
    # 中文注释：设置变量或字段 model_id 的值，供后续逻辑使用。
    model_id = int(data.get('model_id') or 0)
    # 中文注释：设置变量或字段 temperature 的值，供后续逻辑使用。
    temperature = float(data.get('temperature', 0.7))
    # 中文注释：设置变量或字段 max_tokens 的值，供后续逻辑使用。
    max_tokens = data.get('max_tokens')

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not isinstance(raw_messages, list) or not raw_messages:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='messages 不能为空。')

    # 中文注释：设置字典、响应体或配置项中的一个字段。
    messages: list[ChatMessage] = []
    # 中文注释：遍历集合中的每一项，并逐项执行下面的代码块。
    for item in raw_messages:
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if not isinstance(item, dict):
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='messages 格式不正确。')
        # 中文注释：设置变量或字段 role 的值，供后续逻辑使用。
        role = str(item.get('role', '')).strip()
        # 中文注释：设置变量或字段 content 的值，供后续逻辑使用。
        content = str(item.get('content', '')).strip()
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if role not in ('system', 'user', 'assistant') or not content:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='messages 中的 role 或 content 不正确。')
        # 中文注释：设置变量或字段 messages.append(ChatMessage(role 的值，供后续逻辑使用。
        messages.append(ChatMessage(role=role, content=content))

    # 中文注释：设置变量或字段 parsed_max_tokens 的值，供后续逻辑使用。
    parsed_max_tokens = None
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if max_tokens not in (None, ''):
        # 中文注释：设置变量或字段 parsed_max_tokens 的值，供后续逻辑使用。
        parsed_max_tokens = int(max_tokens)
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if parsed_max_tokens <= 0:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='max_tokens 必须大于 0。')

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 config 的值，供后续逻辑使用。
        config = crud.get_model_config(db, model_id) if model_id > 0 else crud.get_default_model_config(db)
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if not config or config.status != 'enabled':
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='模型配置不存在或未启用。')
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if config.provider != 'openai-compatible':
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='当前接口只能调用对话模型，请选择 openai-compatible 模型。')
        # 中文注释：设置变量或字段 client 的值，供后续逻辑使用。
        client = OpenAICompatibleLLMClient(
            # 中文注释：设置变量或字段 base_url 的值，供后续逻辑使用。
            base_url=config.base_url,
            # 中文注释：设置变量或字段 model_name 的值，供后续逻辑使用。
            model_name=config.model_name,
            # 中文注释：设置变量或字段 api_key 的值，供后续逻辑使用。
            api_key=config.api_key,
        # 中文注释：结束当前多行数据结构或多行参数。
        )
        # 中文注释：设置变量或字段 model_name 的值，供后续逻辑使用。
        model_name = config.model_name

    # 中文注释：定义函数 event_generator，封装一段可复用的业务逻辑。
    def event_generator():
        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 中文注释：遍历集合中的每一项，并逐项执行下面的代码块。
            for chunk in client.stream_chat(
                # 中文注释：设置变量或字段 messages 的值，供后续逻辑使用。
                messages=messages,
                # 中文注释：设置变量或字段 temperature 的值，供后续逻辑使用。
                temperature=temperature,
                # 中文注释：设置变量或字段 max_tokens 的值，供后续逻辑使用。
                max_tokens=parsed_max_tokens,
            # 中文注释：执行当前代码行对应的业务逻辑。
            ):
                # 中文注释：生成一段结果并返回给调用方，同时保留后续继续执行的状态。
                yield chunk
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except LLMClientError as exc:
            # 中文注释：生成一段结果并返回给调用方，同时保留后续继续执行的状态。
            yield _sse_error(str(exc), model_name=model_name)
            # 中文注释：生成一段结果并返回给调用方，同时保留后续继续执行的状态。
            yield 'data: [DONE]\n\n'

    # 中文注释：返回当前函数处理后的结果。
    return StreamingResponse(
        # 中文注释：执行当前代码行对应的业务逻辑。
        event_generator(),
        # 中文注释：设置变量或字段 media_type 的值，供后续逻辑使用。
        media_type='text/event-stream',
        # 中文注释：开始定义多行数据结构或多行参数。
        headers={
            # 中文注释：设置字典、响应体或配置项中的一个字段。
            'Cache-Control': 'no-cache',
            # 中文注释：设置字典、响应体或配置项中的一个字段。
            'X-Accel-Buffering': 'no',
        # 中文注释：结束当前多行数据结构或多行参数。
        },
    # 中文注释：结束当前多行数据结构或多行参数。
    )


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@model_configs_router.post('/embeddings')
# 中文注释：定义函数 create_embeddings，封装一段可复用的业务逻辑。
def create_embeddings(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 model_id 的值，供后续逻辑使用。
    model_id = int(data.get('model_id') or 0)
    # 中文注释：设置变量或字段 input_value 的值，供后续逻辑使用。
    input_value = data.get('input')

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if isinstance(input_value, str):
        # 中文注释：设置变量或字段 input_text: str | list[str] 的值，供后续逻辑使用。
        input_text: str | list[str] = input_value.strip()
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if not input_text:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='input 不能为空。')
    # 中文注释：当前面的条件不成立时，继续判断这个分支条件。
    elif isinstance(input_value, list):
        # 中文注释：设置变量或字段 input_text 的值，供后续逻辑使用。
        input_text = [str(item).strip() for item in input_value if str(item).strip()]
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if not input_text:
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='input 不能为空。')
    # 中文注释：当前面条件都不成立时，执行默认分支逻辑。
    else:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='input 必须是字符串或字符串数组。')

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 config 的值，供后续逻辑使用。
        config = crud.get_model_config(db, model_id) if model_id > 0 else crud.get_default_embedding_model_config(db)
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if not config or config.status != 'enabled':
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='向量模型配置不存在或未启用。')
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if config.provider != 'openai-compatible-embedding':
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='当前接口只能调用向量模型，请选择 openai-compatible-embedding 模型。')
        # 中文注释：设置变量或字段 client 的值，供后续逻辑使用。
        client = OpenAICompatibleEmbeddingClient(
            # 中文注释：设置变量或字段 base_url 的值，供后续逻辑使用。
            base_url=config.base_url,
            # 中文注释：设置变量或字段 model_name 的值，供后续逻辑使用。
            model_name=config.model_name,
            # 中文注释：设置变量或字段 api_key 的值，供后续逻辑使用。
            api_key=config.api_key,
        # 中文注释：结束当前多行数据结构或多行参数。
        )

    # 中文注释：开始执行可能抛出异常的代码块。
    try:
        # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
        response_data = client.create_embeddings(input_text=input_text)
    # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
    except LLMClientError as exc:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=502, detail=str(exc))

    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=response_data)


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@model_configs_router.post('/embeddings/chunks')
# 中文注释：定义函数 create_chunk_embeddings，封装一段可复用的业务逻辑。
def create_chunk_embeddings(data: dict[str, Any] | None = Body(default=None)):
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = data or {}
    # 中文注释：设置变量或字段 model_id 的值，供后续逻辑使用。
    model_id = int(data.get('model_id') or 0)
    # 中文注释：设置变量或字段 text 的值，供后续逻辑使用。
    text = str(data.get('text', '')).strip()
    # 中文注释：设置变量或字段 chunk_size 的值，供后续逻辑使用。
    chunk_size = int(data.get('chunk_size') or 500)
    # 中文注释：设置变量或字段 chunk_overlap 的值，供后续逻辑使用。
    chunk_overlap = int(data.get('chunk_overlap') or 80)

    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not text:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='text 不能为空。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if chunk_size <= 0 or chunk_size > 5000:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='chunk_size 必须在 1 到 5000 之间。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if chunk_overlap < 0:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='chunk_overlap 不能小于 0。')
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if chunk_overlap >= chunk_size:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='chunk_overlap 必须小于 chunk_size。')

    # 中文注释：设置变量或字段 chunks 的值，供后续逻辑使用。
    chunks = split_text_into_chunks(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not chunks:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='切片结果为空。')

    # 中文注释：使用上下文管理器自动管理资源的创建和释放。
    with SessionLocal() as db:
        # 中文注释：设置变量或字段 config 的值，供后续逻辑使用。
        config = crud.get_model_config(db, model_id) if model_id > 0 else crud.get_default_embedding_model_config(db)
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if not config or config.status != 'enabled':
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=404, detail='向量模型配置不存在或未启用。')
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if config.provider != 'openai-compatible-embedding':
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise HTTPException(status_code=400, detail='当前接口只能调用向量模型，请选择 openai-compatible-embedding 模型。')
        # 中文注释：设置变量或字段 client 的值，供后续逻辑使用。
        client = OpenAICompatibleEmbeddingClient(
            # 中文注释：设置变量或字段 base_url 的值，供后续逻辑使用。
            base_url=config.base_url,
            # 中文注释：设置变量或字段 model_name 的值，供后续逻辑使用。
            model_name=config.model_name,
            # 中文注释：设置变量或字段 api_key 的值，供后续逻辑使用。
            api_key=config.api_key,
        # 中文注释：结束当前多行数据结构或多行参数。
        )

    # 中文注释：开始执行可能抛出异常的代码块。
    try:
        # 中文注释：设置变量或字段 response_data 的值，供后续逻辑使用。
        response_data = client.create_embeddings(input_text=[str(chunk['content']) for chunk in chunks])
    # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
    except LLMClientError as exc:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=502, detail=str(exc))

    # 中文注释：开始定义多行数据结构或多行参数。
    embeddings_by_index = {
        # 中文注释：调用函数或方法，执行对应的业务处理。
        int(item.get('index', 0)): item.get('embedding', [])
        # 中文注释：遍历集合中的每一项，并逐项执行下面的代码块。
        for item in response_data.get('data', [])
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if isinstance(item, dict)
    # 中文注释：结束当前多行数据结构或多行参数。
    }
    # 中文注释：开始定义多行数据结构或多行参数。
    payload = {
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        'model': response_data.get('model', config.model_name),
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        'chunk_size': chunk_size,
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        'chunk_overlap': chunk_overlap,
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        'total_chunks': len(chunks),
        # 中文注释：执行当前代码行对应的业务逻辑。
        'chunks': [
            # 中文注释：开始定义多行数据结构或多行参数。
            {
                # 中文注释：执行当前代码行对应的业务逻辑。
                **chunk,
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'embedding': embeddings_by_index.get(int(chunk['index']), []),
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'embedding_dim': len(embeddings_by_index.get(int(chunk['index']), [])),
            # 中文注释：结束当前多行数据结构或多行参数。
            }
            # 中文注释：遍历集合中的每一项，并逐项执行下面的代码块。
            for chunk in chunks
        # 中文注释：结束当前多行数据结构或多行参数。
        ],
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        'usage': response_data.get('usage', {}),
    # 中文注释：结束当前多行数据结构或多行参数。
    }
    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=payload)
