# ABC: 定义抽象基类，要求子类实现统一的模型调用接口。
# abstractmethod: 标记抽象方法，避免直接实例化未完整实现的客户端。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from abc import ABC, abstractmethod
# Iterator: 表示同步迭代器返回类型，用于逐段产出流式 SSE 内容。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from collections.abc import Iterator
# dataclass: 快速声明轻量级消息数据结构。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from dataclasses import dataclass
# Any: 表示请求载荷中可包含任意 JSON 兼容值。
# 中文注释：从指定模块导入当前文件需要使用的对象。
from typing import Any
# json: 将 Python 字典序列化为模型接口需要的 JSON 请求体。
# 中文注释：导入当前文件需要使用的 Python 模块。
import json
# urllib.error: 捕获 HTTP、网络连接等标准库请求异常。
# 中文注释：导入当前文件需要使用的 Python 模块。
import urllib.error
# urllib.request: 使用标准库发起 HTTP 请求，避免引入额外第三方依赖。
# 中文注释：导入当前文件需要使用的 Python 模块。
import urllib.request


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@dataclass(slots=True)
# 中文注释：定义 ChatMessage 类，用于组织相关数据或业务逻辑。
class ChatMessage:
    # 单条聊天消息，role 表示消息角色，content 表示消息内容。
    # 中文注释：执行当前代码行对应的业务逻辑。
    role: str
    # 中文注释：执行当前代码行对应的业务逻辑。
    content: str


# 中文注释：定义 LLMClientError 类，用于组织相关数据或业务逻辑。
class LLMClientError(RuntimeError):
    # 模型客户端统一异常，供路由层捕获并转换为标准流式错误响应。
    # 中文注释：占位语句，表示这里暂时不需要执行任何操作。
    pass


# 中文注释：定义 BaseLLMClient 类，用于组织相关数据或业务逻辑。
class BaseLLMClient(ABC):
    # 中文注释：执行当前代码行对应的业务逻辑。
    """模型调用基类：统一不同模型服务的流式聊天接口。"""

    # 中文注释：定义函数 __init__，封装一段可复用的业务逻辑。
    def __init__(self, *, base_url: str, model_name: str, api_key: str, timeout: float = 60.0) -> None:
        # 去掉 base_url 尾部斜杠，避免拼接接口路径时出现双斜杠。
        # 中文注释：设置变量或字段 self.base_url 的值，供后续逻辑使用。
        self.base_url = base_url.rstrip('/')
        # 当前调用的模型名称，对应模型服务中的 model 参数。
        # 中文注释：设置变量或字段 self.model_name 的值，供后续逻辑使用。
        self.model_name = model_name
        # 模型服务鉴权密钥，调用时放入 Authorization 请求头。
        # 中文注释：设置变量或字段 self.api_key 的值，供后续逻辑使用。
        self.api_key = api_key
        # 请求超时时间，防止模型服务长时间无响应导致连接悬挂。
        # 中文注释：设置变量或字段 self.timeout 的值，供后续逻辑使用。
        self.timeout = timeout

    # 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
    @abstractmethod
    # 中文注释：定义函数 stream_chat，封装一段可复用的业务逻辑。
    def stream_chat(
        # 中文注释：执行当前代码行对应的业务逻辑。
        self,
        # 中文注释：执行当前代码行对应的业务逻辑。
        *,
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        messages: list[ChatMessage],
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        temperature: float = 0.7,
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        max_tokens: int | None = None,
    # 中文注释：执行当前代码行对应的业务逻辑。
    ) -> Iterator[str]:
        # 中文注释：执行当前代码行对应的业务逻辑。
        """返回标准 SSE 数据行：data: {OpenAI ChatCompletionChunk}\n\n。"""
        # 抽象方法：不同厂商/协议的模型客户端需要各自实现流式聊天逻辑。
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise NotImplementedError


# 中文注释：定义 OpenAICompatibleEmbeddingClient 类，用于组织相关数据或业务逻辑。
class OpenAICompatibleEmbeddingClient:
    # 中文注释：执行当前代码行对应的业务逻辑。
    """兼容 /v1/embeddings 的 OpenAI 风格向量模型客户端。"""

    # 中文注释：定义函数 __init__，封装一段可复用的业务逻辑。
    def __init__(self, *, base_url: str, model_name: str, api_key: str, timeout: float = 60.0) -> None:
        # Embedding 模型允许配置完整 /embeddings 地址，也允许配置 /v1 根地址。
        # 中文注释：设置变量或字段 self.base_url 的值，供后续逻辑使用。
        self.base_url = base_url.rstrip('/')
        # 当前调用的向量模型名称，对应 Embeddings 接口中的 model 参数。
        # 中文注释：设置变量或字段 self.model_name 的值，供后续逻辑使用。
        self.model_name = model_name
        # 模型服务鉴权密钥，调用时放入 Authorization 请求头。
        # 中文注释：设置变量或字段 self.api_key 的值，供后续逻辑使用。
        self.api_key = api_key
        # 请求超时时间，防止向量服务长时间无响应。
        # 中文注释：设置变量或字段 self.timeout 的值，供后续逻辑使用。
        self.timeout = timeout

    # 中文注释：定义函数 _get_embeddings_url，封装一段可复用的业务逻辑。
    def _get_embeddings_url(self) -> str:
        # 如果配置的是完整 /embeddings 接口地址，则直接使用。
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if self.base_url.endswith('/embeddings'):
            # 中文注释：返回当前函数处理后的结果。
            return self.base_url
        # 如果配置的是 /v1 根地址，则自动拼接 /embeddings。
        # 中文注释：返回当前函数处理后的结果。
        return f'{self.base_url}/embeddings'

    # 中文注释：定义函数 create_embeddings，封装一段可复用的业务逻辑。
    def create_embeddings(self, *, input_text: str | list[str]) -> dict[str, Any]:
        # 组装 OpenAI Embeddings 兼容接口请求体。
        # 中文注释：开始定义多行数据结构或多行参数。
        payload: dict[str, Any] = {
            # 中文注释：设置字典、响应体或配置项中的一个字段。
            'model': self.model_name,
            # 中文注释：设置字典、响应体或配置项中的一个字段。
            'input': input_text,
        # 中文注释：结束当前多行数据结构或多行参数。
        }
        # 将请求体编码为 UTF-8 JSON 字节串。
        # 中文注释：设置变量或字段 body 的值，供后续逻辑使用。
        body = json.dumps(payload).encode('utf-8')
        # 构造标准库 HTTP 请求对象，目标地址为 /embeddings。
        # 中文注释：设置变量或字段 request 的值，供后续逻辑使用。
        request = urllib.request.Request(
            # 中文注释：执行当前代码行对应的业务逻辑。
            self._get_embeddings_url(),
            # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
            data=body,
            # 中文注释：开始定义多行数据结构或多行参数。
            headers={
                # 使用 Bearer Token 方式传递模型服务 API Key。
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'Authorization': f'Bearer {self.api_key}',
                # 声明请求体为 JSON。
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'Content-Type': 'application/json',
                # 声明期望上游返回 JSON。
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'Accept': 'application/json',
            # 中文注释：结束当前多行数据结构或多行参数。
            },
            # 中文注释：设置变量或字段 method 的值，供后续逻辑使用。
            method='POST',
        # 中文注释：结束当前多行数据结构或多行参数。
        )

        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 打开 HTTP 连接，并一次性读取 Embedding 接口返回的 JSON 响应。
            # 中文注释：使用上下文管理器自动管理资源的创建和释放。
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                # 中文注释：设置变量或字段 text 的值，供后续逻辑使用。
                text = response.read().decode('utf-8', errors='ignore')
                # 中文注释：返回当前函数处理后的结果。
                return json.loads(text)
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except urllib.error.HTTPError as exc:
            # HTTPError 表示模型服务返回了 4xx/5xx，读取响应体作为错误详情。
            # 中文注释：设置变量或字段 detail 的值，供后续逻辑使用。
            detail = exc.read().decode('utf-8', errors='ignore')
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise LLMClientError(detail or f'向量模型服务返回 HTTP {exc.code}。') from exc
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except urllib.error.URLError as exc:
            # URLError 表示 DNS、连接拒绝、网络不可达等底层连接问题。
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise LLMClientError(f'无法连接向量模型服务：{exc.reason}') from exc
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except TimeoutError as exc:
            # TimeoutError 表示向量模型服务在指定时间内没有完成响应。
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise LLMClientError('向量模型服务响应超时。') from exc
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except json.JSONDecodeError as exc:
            # JSONDecodeError 表示上游响应不是合法 JSON。
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise LLMClientError('向量模型服务返回数据不是合法 JSON。') from exc


# 中文注释：定义 OpenAICompatibleLLMClient 类，用于组织相关数据或业务逻辑。
class OpenAICompatibleLLMClient(BaseLLMClient):
    # 中文注释：执行当前代码行对应的业务逻辑。
    """兼容 /v1/chat/completions 的 OpenAI 风格模型服务客户端。"""

    # 中文注释：定义函数 stream_chat，封装一段可复用的业务逻辑。
    def stream_chat(
        # 中文注释：执行当前代码行对应的业务逻辑。
        self,
        # 中文注释：执行当前代码行对应的业务逻辑。
        *,
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        messages: list[ChatMessage],
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        temperature: float = 0.7,
        # 中文注释：设置字典、响应体或配置项中的一个字段。
        max_tokens: int | None = None,
    # 中文注释：执行当前代码行对应的业务逻辑。
    ) -> Iterator[str]:
        # 组装 OpenAI Chat Completions 兼容接口请求体。
        # 中文注释：开始定义多行数据结构或多行参数。
        payload: dict[str, Any] = {
            # 中文注释：设置字典、响应体或配置项中的一个字段。
            'model': self.model_name,
            # 中文注释：设置字典、响应体或配置项中的一个字段。
            'messages': [{'role': message.role, 'content': message.content} for message in messages],
            # 中文注释：设置字典、响应体或配置项中的一个字段。
            'temperature': temperature,
            # 中文注释：设置字典、响应体或配置项中的一个字段。
            'stream': True,
        # 中文注释：结束当前多行数据结构或多行参数。
        }
        # max_tokens 是可选参数：未传时让模型服务使用自身默认值。
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if max_tokens is not None:
            # 中文注释：设置变量或字段 payload['max_tokens'] 的值，供后续逻辑使用。
            payload['max_tokens'] = max_tokens

        # 将请求体编码为 UTF-8 JSON 字节串。
        # 中文注释：设置变量或字段 body 的值，供后续逻辑使用。
        body = json.dumps(payload).encode('utf-8')
        # 构造标准库 HTTP 请求对象，目标地址为 /chat/completions。
        # 中文注释：设置变量或字段 request 的值，供后续逻辑使用。
        request = urllib.request.Request(
            # 中文注释：执行当前代码行对应的业务逻辑。
            f'{self.base_url}/chat/completions',
            # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
            data=body,
            # 中文注释：开始定义多行数据结构或多行参数。
            headers={
                # 使用 Bearer Token 方式传递模型服务 API Key。
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'Authorization': f'Bearer {self.api_key}',
                # 声明请求体为 JSON。
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'Content-Type': 'application/json',
                # 声明期望上游返回 SSE 流式响应。
                # 中文注释：设置字典、响应体或配置项中的一个字段。
                'Accept': 'text/event-stream',
            # 中文注释：结束当前多行数据结构或多行参数。
            },
            # 中文注释：设置变量或字段 method 的值，供后续逻辑使用。
            method='POST',
        # 中文注释：结束当前多行数据结构或多行参数。
        )

        # 中文注释：开始执行可能抛出异常的代码块。
        try:
            # 打开 HTTP 连接，并按行读取上游模型返回的流式内容。
            # 中文注释：使用上下文管理器自动管理资源的创建和释放。
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                # 中文注释：遍历集合中的每一项，并逐项执行下面的代码块。
                for raw_line in response:
                    # 将字节行解码为字符串，并忽略无法解码的异常字符。
                    # 中文注释：设置变量或字段 line 的值，供后续逻辑使用。
                    line = raw_line.decode('utf-8', errors='ignore').strip()
                    # 空行通常是 SSE 事件分隔符，这里跳过后在 yield 时统一补齐。
                    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
                    if not line:
                        # 中文注释：跳过本轮循环剩余逻辑，继续下一轮循环。
                        continue
                    # 上游若已经返回标准 SSE，保持标准结构透传；若只返回 JSON 行，则补齐 data: 前缀。
                    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
                    if line.startswith('data:'):
                        # 中文注释：生成一段结果并返回给调用方，同时保留后续继续执行的状态。
                        yield f'{line}\n\n'
                    # 中文注释：当前面条件都不成立时，执行默认分支逻辑。
                    else:
                        # 中文注释：生成一段结果并返回给调用方，同时保留后续继续执行的状态。
                        yield f'data: {line}\n\n'
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except urllib.error.HTTPError as exc:
            # HTTPError 表示模型服务返回了 4xx/5xx，读取响应体作为错误详情。
            # 中文注释：设置变量或字段 detail 的值，供后续逻辑使用。
            detail = exc.read().decode('utf-8', errors='ignore')
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise LLMClientError(detail or f'模型服务返回 HTTP {exc.code}。') from exc
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except urllib.error.URLError as exc:
            # URLError 表示 DNS、连接拒绝、网络不可达等底层连接问题。
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise LLMClientError(f'无法连接模型服务：{exc.reason}') from exc
        # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
        except TimeoutError as exc:
            # TimeoutError 表示模型服务在指定时间内没有完成响应。
            # 中文注释：主动抛出异常，将错误信息交给上层处理。
            raise LLMClientError('模型服务响应超时。') from exc
