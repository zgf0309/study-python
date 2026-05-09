# 中文注释：导入当前文件需要使用的 Python 模块。
import json
import re
import zipfile
from io import BytesIO
from typing import Any
from xml.etree import ElementTree

# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi import APIRouter, Body, File, HTTPException, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

# 中文注释：从指定模块导入当前文件需要使用的对象。
from .. import crud, models
from ..database import SessionLocal
from ..llm import LLMClientError, OpenAICompatibleEmbeddingClient
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..response import api_response
# 中文注释：从指定模块导入当前文件需要使用的对象。
from ..storage import download_file_from_minio, get_presigned_file_url, upload_file_to_minio
from .model_configs import split_text_into_chunks

# 中文注释：设置变量或字段 files_router 的值，供后续逻辑使用。
files_router = APIRouter()

IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg')
AUDIO_EXTS = ('.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac')
VIDEO_EXTS = ('.mp4', '.webm', '.mov', '.m4v', '.avi', '.mkv')


def _natural_xml_path_key(path: str) -> tuple[str, int]:
    # 让 slide2.xml 排在 slide10.xml 前面，保证 PPTX 页顺序稳定。
    match = re.search(r'(\d+)\.xml$', path)
    return path.rsplit('/', 1)[0], int(match.group(1)) if match else 0


def _extract_text_from_xml(xml_data: bytes, text_tag: str) -> list[str]:
    # 从 OpenXML 中按段落提取文本，兼容 PPTX 的 a:t 和 DOCX 的 w:t。
    root = ElementTree.fromstring(xml_data)
    paragraphs: list[str] = []
    for paragraph in root.iter():
        if not paragraph.tag.endswith('}p'):
            continue
        texts = [node.text or '' for node in paragraph.iter() if node.tag.endswith(text_tag)]
        line = ''.join(texts).strip()
        if line:
            paragraphs.append(line)
    if paragraphs:
        return paragraphs

    # 某些 XML 没有标准段落结构时，退化为提取所有文本节点。
    texts = [node.text or '' for node in root.iter() if node.tag.endswith(text_tag)]
    line = ' '.join(item.strip() for item in texts if item.strip())
    return [line] if line else []


def _extract_docx_text(data: bytes) -> str:
    # 使用标准库从 docx 的 word/document.xml 中提取正文文本。
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            xml_data = archive.read('word/document.xml')
    except Exception as exc:
        raise HTTPException(status_code=400, detail='暂不支持读取该 DOCX 文件内容。') from exc

    return '\n'.join(_extract_text_from_xml(xml_data, '}t'))


def _extract_pptx_text(data: bytes) -> str:
    # 使用标准库从 PPTX 的 ppt/slides/slide*.xml 中提取每页文本，避免把 zip 二进制误解码为乱码。
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            slide_paths = sorted(
                [name for name in archive.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', name)],
                key=_natural_xml_path_key,
            )
            if not slide_paths:
                raise HTTPException(status_code=400, detail='该 PPTX 未找到可读取的幻灯片内容。')

            slides: list[str] = []
            for index, path in enumerate(slide_paths, start=1):
                paragraphs = _extract_text_from_xml(archive.read(path), '}t')
                if paragraphs:
                    slides.append(f'第 {index} 页\n' + '\n'.join(paragraphs))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail='暂不支持读取该 PPTX 文件内容。') from exc

    text = '\n\n'.join(slides).strip()
    if not text:
        raise HTTPException(status_code=400, detail='PPTX 中未提取到可切片文本。')
    return text


def _extract_pdf_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise HTTPException(status_code=500, detail='当前服务未安装 PDF 解析依赖 pypdf，请先安装后重试。') from exc

    try:
        reader = PdfReader(BytesIO(data))
        pages: list[str] = []
        for index, page in enumerate(reader.pages, start=1):
            page_text = (page.extract_text() or '').strip()
            if page_text:
                pages.append(f'第 {index} 页\n{page_text}')
    except Exception as exc:
        raise HTTPException(status_code=400, detail='暂不支持读取该 PDF 文件内容，请确认文件未加密且格式正常。') from exc

    text = '\n\n'.join(pages).strip()
    if not text:
        raise HTTPException(status_code=400, detail='PDF 中未提取到可切片文本；如果是扫描件或图片型 PDF，请先进行 OCR 后再上传。')
    return text


def _get_media_kind(filename: str, content_type: str) -> str | None:
    lower_name = filename.lower()
    lower_type = content_type.lower()
    if lower_type.startswith('image/') or lower_name.endswith(IMAGE_EXTS):
        return '图片'
    if lower_type.startswith('audio/') or lower_name.endswith(AUDIO_EXTS):
        return '音频'
    if lower_type.startswith('video/') or lower_name.endswith(VIDEO_EXTS):
        return '视频'
    return None


def _format_file_size(size: int) -> str:
    units = ['B', 'KB', 'MB', 'GB']
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f'{value:.2f} {unit}' if unit != 'B' else f'{int(value)} {unit}'
        value /= 1024
    return f'{size} B'


def _build_media_knowledge_text(file_info: dict[str, object]) -> str:
    filename = str(file_info.get('filename') or '')
    content_type = str(file_info.get('content_type') or 'application/octet-stream')
    kind = _get_media_kind(filename, content_type) or '多媒体文件'
    size = int(file_info.get('size') or 0)
    bucket = str(file_info.get('bucket') or '')
    object_name = str(file_info.get('object_name') or '')

    return '\n'.join([
        f'{kind}基础解析结果',
        f'文件名：{filename}',
        f'文件类型：{content_type}',
        f'文件大小：{_format_file_size(size)}',
        f'存储位置：{bucket}/{object_name}',
        '解析说明：当前未接入专用多模态理解模型，系统已保存媒体文件的基础元信息作为知识点，并可用于后续检索和详情展示。',
    ])


def _decode_file_text(filename: str, content_type: str, data: bytes) -> str:
    # 根据文件类型提取可向量化文本；避免把 Office/图片/音视频等二进制内容按 latin-1 强行解码成乱码。
    lower_name = filename.lower()
    lower_type = content_type.lower()
    text_exts = ('.txt', '.md', '.markdown', '.csv', '.json', '.html', '.htm', '.xml', '.yaml', '.yml', '.log')

    if lower_name.endswith('.docx') or 'wordprocessingml.document' in lower_type:
        return _extract_docx_text(data)
    if lower_name.endswith('.pptx') or 'presentationml.presentation' in lower_type:
        return _extract_pptx_text(data)
    if lower_name.endswith('.pdf') or lower_type == 'application/pdf':
        return _extract_pdf_text(data)
    if lower_name.endswith(('.ppt', '.doc', '.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail='暂不支持该 Office 文件格式，请转换为 docx 或 pptx 后重试。')
    if _get_media_kind(filename, content_type):
        raise HTTPException(status_code=400, detail='图片、音频、视频暂不支持按原文切片，请使用多模态解析结果生成知识点。')

    is_declared_text = lower_type.startswith('text/') or any(lower_name.endswith(ext) for ext in text_exts)
    if not is_declared_text and lower_type not in ('application/octet-stream', ''):
        raise HTTPException(status_code=400, detail='当前文件类型暂不支持文本切片。')

    for encoding in ('utf-8', 'utf-8-sig', 'gb18030'):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise HTTPException(status_code=400, detail='文件内容无法按文本解码，请确认文件格式或编码。')


def _rebuild_original_content_from_chunks(chunks: list[models.KnowledgeFileChunk]) -> str:
    original_content = ''
    current_end = 0
    for item in chunks:
        if item.start < current_end:
            original_content += item.content[max(0, current_end - item.start):]
        else:
            original_content += item.content
        current_end = max(current_end, item.end)
    return original_content


def _read_original_content_from_minio(record: models.KnowledgeFile) -> str:
    file_info = download_file_from_minio(record.object_name, bucket=record.bucket)
    if _get_media_kind(str(file_info['filename']), str(file_info['content_type'])):
        return _build_media_knowledge_text(file_info)
    return _decode_file_text(
        str(file_info['filename']),
        str(file_info['content_type']),
        file_info['data'],
    )


def _serialize_file(record: models.KnowledgeFile, *, include_chunks: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        'id': record.id,
        'bucket': record.bucket,
        'object_name': record.object_name,
        'filename': record.filename,
        'knowledge_base_id': record.knowledge_base_id,
        'knowledge_base_name': record.knowledge_base.name if record.knowledge_base else '',
        'content_type': record.content_type,
        'size': record.size,
        'chunk_size': record.chunk_size,
        'chunk_overlap': record.chunk_overlap,
        'chunk_count': record.chunk_count,
        'embedding_model': record.embedding_model,
        'status': record.status,
        'error_message': record.error_message,
        'created_at': record.created_at.isoformat() if record.created_at else '',
    }
    try:
        payload['presigned_url'] = get_presigned_file_url(record.object_name, bucket=record.bucket)
    except HTTPException:
        payload['presigned_url'] = ''

    if include_chunks:
        chunks = sorted(record.chunks, key=lambda chunk: chunk.chunk_index)
        payload['chunks'] = [
            {
                'index': item.chunk_index,
                'content': item.content,
                'start': item.start,
                'end': item.end,
                'length': item.length,
                'embedding': json.loads(item.embedding or '[]'),
                'embedding_dim': item.embedding_dim,
            }
            for item in chunks
        ]
        try:
            payload['original_content'] = _read_original_content_from_minio(record)
            payload['original_content_source'] = 'minio'
        except HTTPException:
            payload['original_content'] = _rebuild_original_content_from_chunks(chunks)
            payload['original_content_source'] = 'chunks'
    return payload


def _serialize_knowledge_base(record: models.KnowledgeBase) -> dict[str, Any]:
    return {
        'id': record.id,
        'name': record.name,
        'description': record.description or '',
        'status': record.status,
        'created_at': record.created_at.isoformat() if record.created_at else '',
    }


def _get_or_create_default_knowledge_base(db) -> models.KnowledgeBase:
    record = db.scalar(select(models.KnowledgeBase).where(models.KnowledgeBase.name == '默认知识库'))
    if record is not None:
        return record
    record = models.KnowledgeBase(name='默认知识库', description='系统默认知识库', status='enabled')
    db.add(record)
    db.flush()
    return record


@files_router.get('/knowledge-bases')
def list_knowledge_bases():
    with SessionLocal() as db:
        _get_or_create_default_knowledge_base(db)
        db.commit()
        records = list(db.scalars(select(models.KnowledgeBase).order_by(models.KnowledgeBase.id.asc())))
        payload = [_serialize_knowledge_base(record) for record in records]
    return api_response(data=payload)


@files_router.post('/knowledge-bases', status_code=status.HTTP_201_CREATED)
def create_knowledge_base(data: dict[str, Any] | None = Body(default=None)):
    data = data or {}
    name = str(data.get('name') or '').strip()
    description = str(data.get('description') or '').strip()
    if not name:
        raise HTTPException(status_code=400, detail='知识库名称不能为空。')

    with SessionLocal() as db:
        existing = db.scalar(select(models.KnowledgeBase).where(models.KnowledgeBase.name == name))
        if existing is not None:
            raise HTTPException(status_code=400, detail='知识库名称已存在。')
        record = models.KnowledgeBase(name=name, description=description or None, status='enabled')
        db.add(record)
        db.commit()
        db.refresh(record)
        payload = _serialize_knowledge_base(record)
    return api_response(data=payload, message='知识库已新增。')


# 中文注释：使用装饰器为下面的函数或方法绑定额外行为。
@files_router.post('/files/upload', status_code=status.HTTP_201_CREATED)
# 中文注释：定义函数 upload_file，封装一段可复用的业务逻辑。
def upload_file(file: UploadFile = File(...)):
    # 接收前端上传的文件，并保存到本地 Docker MinIO。
    # 中文注释：设置变量或字段 payload 的值，供后续逻辑使用。
    payload = upload_file_to_minio(file)
    # 中文注释：返回当前函数处理后的结果。
    return api_response(data=payload, message='文件已上传到 MinIO。')


@files_router.get('/files')
def list_vectorized_files():
    # 查询已经切片并向量化保存到数据库的文件列表。
    with SessionLocal() as db:
        records = list(db.scalars(
            select(models.KnowledgeFile)
            .options(selectinload(models.KnowledgeFile.knowledge_base))
            .order_by(models.KnowledgeFile.id.desc())
        ))
        payload = [_serialize_file(record) for record in records]
    return api_response(data=payload)


@files_router.get('/files/{file_id}')
def get_vectorized_file(file_id: int):
    # 查询单个文件详情，包含切片内容和临时预览地址。
    with SessionLocal() as db:
        record = db.scalar(
            select(models.KnowledgeFile)
            .options(selectinload(models.KnowledgeFile.chunks), selectinload(models.KnowledgeFile.knowledge_base))
            .where(models.KnowledgeFile.id == file_id)
        )
        if record is None:
            raise HTTPException(status_code=404, detail='文件不存在。')
        payload = _serialize_file(record, include_chunks=True)
    return api_response(data=payload)


@files_router.post('/files/vectorize-minio', status_code=status.HTTP_201_CREATED)
def vectorize_minio_file(data: dict[str, Any] | None = Body(default=None)):
    # 从 MinIO 读取文件，根据切片长度和重叠长度生成切片、调用向量模型，并将文件列表及切片向量保存到数据库。
    data = data or {}
    bucket = str(data.get('bucket') or '').strip() or None
    object_name = str(data.get('object_name') or '').strip()
    model_id = int(data.get('model_id') or 0)
    knowledge_base_id = int(data.get('knowledge_base_id') or 0)
    chunk_size = int(data.get('chunk_size') or 500)
    chunk_overlap = int(data.get('chunk_overlap') or 80)

    if not object_name:
        raise HTTPException(status_code=400, detail='object_name 不能为空。')
    if chunk_size <= 0 or chunk_size > 5000:
        raise HTTPException(status_code=400, detail='chunk_size 必须在 1 到 5000 之间。')
    if chunk_overlap < 0:
        raise HTTPException(status_code=400, detail='chunk_overlap 不能小于 0。')
    if chunk_overlap >= chunk_size:
        raise HTTPException(status_code=400, detail='chunk_overlap 必须小于 chunk_size。')
    if knowledge_base_id <= 0:
        raise HTTPException(status_code=400, detail='请选择知识库。')

    file_info = download_file_from_minio(object_name, bucket=bucket)
    media_kind = _get_media_kind(str(file_info['filename']), str(file_info['content_type']))
    if media_kind:
        text = _build_media_knowledge_text(file_info)
    else:
        text = _decode_file_text(
            str(file_info['filename']),
            str(file_info['content_type']),
            file_info['data'],
        ).strip()
    if not text:
        raise HTTPException(status_code=400, detail='文件内容为空，无法切片向量化。')

    chunks = [
        {
            'index': 0,
            'content': text,
            'start': 0,
            'end': len(text),
            'length': len(text),
        }
    ] if media_kind else split_text_into_chunks(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if not chunks:
        raise HTTPException(status_code=400, detail='切片结果为空。')

    with SessionLocal() as db:
        knowledge_base = db.get(models.KnowledgeBase, knowledge_base_id)
        if knowledge_base is None or knowledge_base.status != 'enabled':
            raise HTTPException(status_code=404, detail='知识库不存在或未启用。')
        config = crud.get_model_config(db, model_id) if model_id > 0 else crud.get_default_embedding_model_config(db)
        if not config or config.status != 'enabled':
            raise HTTPException(status_code=404, detail='向量模型配置不存在或未启用。')
        if config.provider != 'openai-compatible-embedding':
            raise HTTPException(status_code=400, detail='当前接口只能调用向量模型，请选择 openai-compatible-embedding 模型。')
        client = OpenAICompatibleEmbeddingClient(
            base_url=config.base_url,
            model_name=config.model_name,
            api_key=config.api_key,
        )
        embedding_model = config.model_name

    try:
        response_data = client.create_embeddings(input_text=[str(chunk['content']) for chunk in chunks])
    except LLMClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    embeddings_by_index = {
        int(item.get('index', 0)): item.get('embedding', [])
        for item in response_data.get('data', [])
        if isinstance(item, dict)
    }

    with SessionLocal() as db:
        # 同一 MinIO 对象重新处理时，先删除旧记录，确保文件列表只保留最新切片参数和向量。
        existing_ids = list(db.scalars(select(models.KnowledgeFile.id).where(
            models.KnowledgeFile.bucket == str(file_info['bucket']),
            models.KnowledgeFile.object_name == object_name,
        )))
        if existing_ids:
            db.execute(delete(models.KnowledgeFileChunk).where(models.KnowledgeFileChunk.file_id.in_(existing_ids)))
            db.execute(delete(models.KnowledgeFile).where(models.KnowledgeFile.id.in_(existing_ids)))

        record = models.KnowledgeFile(
            bucket=str(file_info['bucket']),
            object_name=object_name,
            filename=str(file_info['filename']),
            knowledge_base_id=knowledge_base_id,
            content_type=str(file_info['content_type']),
            size=int(file_info['size']),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunk_count=len(chunks),
            embedding_model=embedding_model,
            status='completed',
        )
        db.add(record)
        db.flush()
        for chunk in chunks:
            embedding = embeddings_by_index.get(int(chunk['index']), [])
            db.add(models.KnowledgeFileChunk(
                file_id=record.id,
                chunk_index=int(chunk['index']),
                content=str(chunk['content']),
                start=int(chunk['start']),
                end=int(chunk['end']),
                length=int(chunk['length']),
                embedding=json.dumps(embedding, ensure_ascii=False),
                embedding_dim=len(embedding),
            ))
        db.commit()
        saved = db.scalar(
            select(models.KnowledgeFile)
            .options(selectinload(models.KnowledgeFile.chunks), selectinload(models.KnowledgeFile.knowledge_base))
            .where(models.KnowledgeFile.id == record.id)
        )
        if saved is None:
            raise HTTPException(status_code=500, detail='文件向量记录保存失败。')
        payload = _serialize_file(saved, include_chunks=True)

    payload['model'] = response_data.get('model', embedding_model)
    payload['usage'] = response_data.get('usage', {})
    return api_response(data=payload, message='MinIO 文件已切片、向量化并保存到数据库。')
