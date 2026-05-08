# os: 用于从环境变量读取内置模型配置，避免把敏感配置散落在业务代码中。
# 中文注释：导入当前文件需要使用的 Python 模块。
import os

# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy import Select, select, update
# 中文注释：从指定模块导入当前文件需要使用的对象。
from sqlalchemy.orm import Session

# 中文注释：从指定模块导入当前文件需要使用的对象。
from .. import models, schemas

# 内置模型的默认值仍保留在这里，方便后台小白本地启动；生产环境建议使用 .env 覆盖。
# 中文注释：设置变量或字段 DEFAULT_LLM_BASE_URL 的值，供后续逻辑使用。
DEFAULT_LLM_BASE_URL = os.getenv('DEFAULT_LLM_BASE_URL', 'http://114.242.210.44:8000/v1')
# 中文注释：设置变量或字段 DEFAULT_LLM_MODEL_NAME 的值，供后续逻辑使用。
DEFAULT_LLM_MODEL_NAME = os.getenv('DEFAULT_LLM_MODEL_NAME', 'jusure-llm')
# 中文注释：设置变量或字段 DEFAULT_LLM_API_KEY 的值，供后续逻辑使用。
DEFAULT_LLM_API_KEY = os.getenv('DEFAULT_LLM_API_KEY', 'sk-ad0eca1e43bc60f825372c496f131e53')
# 中文注释：设置变量或字段 DEFAULT_EMBEDDING_BASE_URL 的值，供后续逻辑使用。
DEFAULT_EMBEDDING_BASE_URL = os.getenv('DEFAULT_EMBEDDING_BASE_URL', 'http://114.242.210.44:6300/v1/embeddings')
# 中文注释：设置变量或字段 DEFAULT_EMBEDDING_MODEL_NAME 的值，供后续逻辑使用。
DEFAULT_EMBEDDING_MODEL_NAME = os.getenv('DEFAULT_EMBEDDING_MODEL_NAME', 'qwen3-embed-4b')
# 中文注释：设置变量或字段 DEFAULT_EMBEDDING_API_KEY 的值，供后续逻辑使用。
DEFAULT_EMBEDDING_API_KEY = os.getenv('DEFAULT_EMBEDDING_API_KEY', DEFAULT_LLM_API_KEY)

# 中文注释：设置变量或字段 DEFAULT_MODEL_CONFIG 的值，供后续逻辑使用。
DEFAULT_MODEL_CONFIG = schemas.ModelConfigCreate(
    # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
    name='jusure-llm 默认模型',
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    base_url=DEFAULT_LLM_BASE_URL,
    # 中文注释：设置变量或字段 model_name 的值，供后续逻辑使用。
    model_name=DEFAULT_LLM_MODEL_NAME,
    # 中文注释：设置变量或字段 api_key 的值，供后续逻辑使用。
    api_key=DEFAULT_LLM_API_KEY,
    # 中文注释：设置变量或字段 provider 的值，供后续逻辑使用。
    provider='openai-compatible',
    # 中文注释：设置变量或字段 is_default 的值，供后续逻辑使用。
    is_default=True,
    # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
    status='enabled',
# 中文注释：结束当前多行数据结构或多行参数。
)

# 中文注释：设置变量或字段 QWEN3_EMBEDDING_MODEL_CONFIG 的值，供后续逻辑使用。
QWEN3_EMBEDDING_MODEL_CONFIG = schemas.ModelConfigCreate(
    # 中文注释：设置变量或字段 name 的值，供后续逻辑使用。
    name='Qwen3-Embedding-4B 向量模型',
    # 中文注释：设置字典、响应体或配置项中的一个字段。
    base_url=DEFAULT_EMBEDDING_BASE_URL,
    # 中文注释：设置变量或字段 model_name 的值，供后续逻辑使用。
    model_name=DEFAULT_EMBEDDING_MODEL_NAME,
    # 中文注释：设置变量或字段 api_key 的值，供后续逻辑使用。
    api_key=DEFAULT_EMBEDDING_API_KEY,
    # 中文注释：设置变量或字段 provider 的值，供后续逻辑使用。
    provider='openai-compatible-embedding',
    # 中文注释：设置变量或字段 is_default 的值，供后续逻辑使用。
    is_default=False,
    # 中文注释：设置变量或字段 status 的值，供后续逻辑使用。
    status='enabled',
# 中文注释：结束当前多行数据结构或多行参数。
)

# 中文注释：设置变量或字段 LEGACY_QWEN3_EMBEDDING_MODEL_NAMES 的值，供后续逻辑使用。
LEGACY_QWEN3_EMBEDDING_MODEL_NAMES = ('Qwen3-Embedding-4B',)


# 中文注释：定义函数 list_model_configs，封装一段可复用的业务逻辑。
def list_model_configs(db: Session, *, enabled_only: bool = False) -> list[models.LLMModelConfig]:
    # 中文注释：设置变量或字段 statement: Select[tuple[models.LLMModelConfig]] 的值，供后续逻辑使用。
    statement: Select[tuple[models.LLMModelConfig]] = select(models.LLMModelConfig).order_by(
        # 中文注释：执行当前代码行对应的业务逻辑。
        models.LLMModelConfig.is_default.desc(),
        # 中文注释：执行当前代码行对应的业务逻辑。
        models.LLMModelConfig.id.asc(),
    # 中文注释：结束当前多行数据结构或多行参数。
    )
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if enabled_only:
        # 中文注释：调用函数或方法，执行对应的业务处理。
        statement = statement.where(models.LLMModelConfig.status == 'enabled')
    # 中文注释：返回当前函数处理后的结果。
    return list(db.scalars(statement))


# 中文注释：定义函数 get_model_config，封装一段可复用的业务逻辑。
def get_model_config(db: Session, config_id: int) -> models.LLMModelConfig | None:
    # 中文注释：返回当前函数处理后的结果。
    return db.get(models.LLMModelConfig, config_id)


# 中文注释：定义函数 get_default_model_config，封装一段可复用的业务逻辑。
def get_default_model_config(db: Session) -> models.LLMModelConfig | None:
    # 中文注释：返回当前函数处理后的结果。
    return db.scalar(
        # 中文注释：调用函数或方法，执行对应的业务处理。
        select(models.LLMModelConfig)
        # 中文注释：调用函数或方法，执行对应的业务处理。
        .where(models.LLMModelConfig.is_default.is_(True), models.LLMModelConfig.status == 'enabled')
        # 中文注释：调用函数或方法，执行对应的业务处理。
        .order_by(models.LLMModelConfig.id.asc())
    # 中文注释：结束当前多行数据结构或多行参数。
    )


# 中文注释：定义函数 get_default_embedding_model_config，封装一段可复用的业务逻辑。
def get_default_embedding_model_config(db: Session) -> models.LLMModelConfig | None:
    # 中文注释：返回当前函数处理后的结果。
    return db.scalar(
        # 中文注释：调用函数或方法，执行对应的业务处理。
        select(models.LLMModelConfig)
        # 中文注释：执行当前代码行对应的业务逻辑。
        .where(
            # 中文注释：执行当前代码行对应的业务逻辑。
            models.LLMModelConfig.provider == 'openai-compatible-embedding',
            # 中文注释：执行当前代码行对应的业务逻辑。
            models.LLMModelConfig.status == 'enabled',
        # 中文注释：结束当前多行数据结构或多行参数。
        )
        # 中文注释：调用函数或方法，执行对应的业务处理。
        .order_by(models.LLMModelConfig.id.asc())
    # 中文注释：结束当前多行数据结构或多行参数。
    )


# 中文注释：定义函数 create_model_config，封装一段可复用的业务逻辑。
def create_model_config(db: Session, payload: schemas.ModelConfigCreate) -> models.LLMModelConfig:
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = payload.model_dump()
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if data.get('is_default'):
        # 中文注释：设置变量或字段 db.execute(update(models.LLMModelConfig).values(is_default 的值，供后续逻辑使用。
        db.execute(update(models.LLMModelConfig).values(is_default=False))
    # 中文注释：设置变量或字段 config 的值，供后续逻辑使用。
    config = models.LLMModelConfig(**data)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.add(config)
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.commit()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    db.refresh(config)
    # 中文注释：返回当前函数处理后的结果。
    return config


# 中文注释：定义函数 ensure_model_config，封装一段可复用的业务逻辑。
def ensure_model_config(db: Session, payload: schemas.ModelConfigCreate) -> models.LLMModelConfig:
    # 根据模型名称查询配置是否已存在，避免应用重启时重复写入同一个模型。
    # 中文注释：调用函数或方法，执行对应的业务处理。
    existing = db.scalar(select(models.LLMModelConfig).where(models.LLMModelConfig.model_name == payload.model_name))
    # 如果已存在，则返回已有记录，不覆盖用户后续在数据库中调整过的配置。
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if existing:
        # 中文注释：返回当前函数处理后的结果。
        return existing
    # 如果不存在，则按内置配置创建一条新的模型记录。
    # 中文注释：返回当前函数处理后的结果。
    return create_model_config(db, payload)


# 中文注释：定义函数 ensure_qwen3_embedding_model_config，封装一段可复用的业务逻辑。
def ensure_qwen3_embedding_model_config(db: Session) -> models.LLMModelConfig:
    # 兼容旧版本曾写入的 Qwen3-Embedding-4B 名称，避免升级后产生不可用的旧配置。
    # 中文注释：设置变量或字段 model_names 的值，供后续逻辑使用。
    model_names = (QWEN3_EMBEDDING_MODEL_CONFIG.model_name, *LEGACY_QWEN3_EMBEDDING_MODEL_NAMES)
    # 中文注释：设置变量或字段 existing 的值，供后续逻辑使用。
    existing = db.scalar(select(models.LLMModelConfig).where(models.LLMModelConfig.model_name.in_(model_names)))
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not existing:
        # 中文注释：返回当前函数处理后的结果。
        return create_model_config(db, QWEN3_EMBEDDING_MODEL_CONFIG)

    # 找到已有记录后，将 base_url、model_name、api_key、provider 等字段修正为当前可用配置。
    # 中文注释：设置变量或字段 changed 的值，供后续逻辑使用。
    changed = False
    # 中文注释：设置变量或字段 data 的值，供后续逻辑使用。
    data = QWEN3_EMBEDDING_MODEL_CONFIG.model_dump()
    # 中文注释：设置变量或字段 data['is_default'] 的值，供后续逻辑使用。
    data['is_default'] = False
    # 中文注释：遍历集合中的每一项，并逐项执行下面的代码块。
    for key, value in data.items():
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if getattr(existing, key) != value:
            # 中文注释：调用函数或方法，执行对应的业务处理。
            setattr(existing, key, value)
            # 中文注释：设置变量或字段 changed 的值，供后续逻辑使用。
            changed = True
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if changed:
        # 中文注释：调用函数或方法，执行对应的业务处理。
        db.commit()
        # 中文注释：调用函数或方法，执行对应的业务处理。
        db.refresh(existing)
    # 中文注释：返回当前函数处理后的结果。
    return existing


# 中文注释：定义函数 ensure_default_model_config，封装一段可复用的业务逻辑。
def ensure_default_model_config(db: Session) -> models.LLMModelConfig:
    # 根据默认模型名称查询数据库中是否已经存在该模型配置，避免应用每次启动都重复插入。
    # 中文注释：设置变量或字段 existing 的值，供后续逻辑使用。
    existing = db.scalar(
        # 中文注释：调用函数或方法，执行对应的业务处理。
        select(models.LLMModelConfig).where(models.LLMModelConfig.model_name == DEFAULT_MODEL_CONFIG.model_name)
    # 中文注释：结束当前多行数据结构或多行参数。
    )
    # 如果默认模型配置已经存在，则只修正必要字段，不创建新记录。
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if existing:
        # 标记本次检查过程中是否修改了数据库字段，用于决定是否提交事务。
        # 中文注释：设置变量或字段 changed 的值，供后续逻辑使用。
        changed = False
        # 如果当前记录还不是默认模型，则先取消其他模型的默认状态，再把当前记录设为默认。
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if not existing.is_default:
            # 中文注释：调用函数或方法，执行对应的业务处理。
            db.execute(update(models.LLMModelConfig).where(models.LLMModelConfig.id != existing.id).values(is_default=False))
            # 中文注释：设置变量或字段 existing.is_default 的值，供后续逻辑使用。
            existing.is_default = True
            # 中文注释：设置变量或字段 changed 的值，供后续逻辑使用。
            changed = True
        # 如果默认模型被禁用，则自动恢复为启用状态，保证系统启动后可直接使用。
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if existing.status != 'enabled':
            # 中文注释：设置变量或字段 existing.status 的值，供后续逻辑使用。
            existing.status = 'enabled'
            # 中文注释：设置变量或字段 changed 的值，供后续逻辑使用。
            changed = True
        # 只有在字段发生变化时才提交事务，避免不必要的数据库写入。
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if changed:
            # 中文注释：调用函数或方法，执行对应的业务处理。
            db.commit()
            # 提交后刷新 ORM 对象，确保返回的数据与数据库最新状态一致。
            # 中文注释：调用函数或方法，执行对应的业务处理。
            db.refresh(existing)
        # 中文注释：返回当前函数处理后的结果。
        return existing
    # 如果数据库中不存在默认模型配置，则创建一条默认模型记录。
    # 中文注释：返回当前函数处理后的结果。
    return create_model_config(db, DEFAULT_MODEL_CONFIG)


# 中文注释：定义函数 ensure_builtin_model_configs，封装一段可复用的业务逻辑。
def ensure_builtin_model_configs(db: Session) -> None:
    # 确保默认对话模型存在，并保持默认、启用状态。
    # 中文注释：调用函数或方法，执行对应的业务处理。
    ensure_default_model_config(db)
    # 确保 Qwen3-Embedding-4B 向量模型存在，但不设置为默认对话模型。
    # 中文注释：调用函数或方法，执行对应的业务处理。
    ensure_qwen3_embedding_model_config(db)
