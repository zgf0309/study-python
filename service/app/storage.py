# 中文注释：导入当前文件需要使用的 Python 模块。
import os
# 中文注释：导入当前文件需要使用的 Python 模块。
import re
# 中文注释：导入当前文件需要使用的 Python 模块。
import uuid
# 中文注释：从指定模块导入当前文件需要使用的对象。
from datetime import datetime, timedelta
# 中文注释：从指定模块导入当前文件需要使用的对象。
from pathlib import Path
# 中文注释：从指定模块导入当前文件需要使用的对象。
from typing import BinaryIO

# 中文注释：从指定模块导入当前文件需要使用的对象。
from fastapi import HTTPException, UploadFile


# 中文注释：设置变量或字段 MINIO_ENDPOINT 的值，供后续逻辑使用。
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', '127.0.0.1:9000')
# 中文注释：设置变量或字段 MINIO_ACCESS_KEY 的值，供后续逻辑使用。
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
# 中文注释：设置变量或字段 MINIO_SECRET_KEY 的值，供后续逻辑使用。
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
# 中文注释：设置变量或字段 MINIO_BUCKET 的值，供后续逻辑使用。
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'study-python')
# 中文注释：设置变量或字段 MINIO_SECURE 的值，供后续逻辑使用。
MINIO_SECURE = os.getenv('MINIO_SECURE', 'false').lower() in ('1', 'true', 'yes')
# 中文注释：设置变量或字段 MINIO_PUBLIC_ENDPOINT 的值，供后续逻辑使用。
MINIO_PUBLIC_ENDPOINT = os.getenv('MINIO_PUBLIC_ENDPOINT', f"{'https' if MINIO_SECURE else 'http'}://{MINIO_ENDPOINT}")


# 中文注释：定义函数 _get_minio_client，封装一段可复用的业务逻辑。
def _get_minio_client():
    # 延迟导入 MinIO SDK，避免依赖未安装时后端启动阶段直接崩溃。
    try:
        # 中文注释：从指定模块导入当前文件需要使用的对象。
        from minio import Minio
        # 中文注释：从指定模块导入当前文件需要使用的对象。
        from minio.error import S3Error
    except ImportError as exc:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=500, detail='后端缺少 minio 依赖，请先安装 requirements.txt。') from exc

    # 中文注释：返回当前函数处理后的结果。
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    ), S3Error


# 中文注释：定义函数 _safe_filename，封装一段可复用的业务逻辑。
def _safe_filename(filename: str | None) -> str:
    # 只保留文件名本身，避免前端传入 ../ 之类路径影响对象名。
    # 中文注释：设置变量或字段 raw_name 的值，供后续逻辑使用。
    raw_name = Path(filename or 'upload.bin').name
    # 中文注释：设置变量或字段 safe_name 的值，供后续逻辑使用。
    safe_name = re.sub(r'[^0-9A-Za-z._\-\u4e00-\u9fff]+', '_', raw_name).strip('._')
    # 中文注释：返回当前函数处理后的结果。
    return safe_name or 'upload.bin'


# 中文注释：定义函数 _get_file_size，封装一段可复用的业务逻辑。
def _get_file_size(file_obj: BinaryIO) -> int:
    # MinIO put_object 需要知道文件大小，因此通过 seek/tell 获取。
    # 中文注释：设置变量或字段 current 的值，供后续逻辑使用。
    current = file_obj.tell()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    file_obj.seek(0, os.SEEK_END)
    # 中文注释：设置变量或字段 size 的值，供后续逻辑使用。
    size = file_obj.tell()
    # 中文注释：调用函数或方法，执行对应的业务处理。
    file_obj.seek(current, os.SEEK_SET)
    # 中文注释：返回当前函数处理后的结果。
    return size


# 中文注释：定义函数 upload_file_to_minio，封装一段可复用的业务逻辑。
def upload_file_to_minio(file: UploadFile) -> dict[str, object]:
    # 将 FastAPI 接收到的上传文件保存到本地 Docker MinIO。
    # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
    if not file.filename:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=400, detail='请选择要上传的文件。')

    # 中文注释：设置变量或字段 client 的值，供后续逻辑使用。
    client, s3_error = _get_minio_client()
    # 中文注释：设置变量或字段 safe_name 的值，供后续逻辑使用。
    safe_name = _safe_filename(file.filename)
    # 中文注释：设置变量或字段 today 的值，供后续逻辑使用。
    today = datetime.now().strftime('%Y/%m/%d')
    # 中文注释：设置变量或字段 object_name 的值，供后续逻辑使用。
    object_name = f'uploads/{today}/{uuid.uuid4().hex}_{safe_name}'
    # 中文注释：设置变量或字段 content_type 的值，供后续逻辑使用。
    content_type = file.content_type or 'application/octet-stream'

    # 中文注释：开始执行可能抛出异常的代码块。
    try:
        # 中文注释：判断条件是否成立，并在成立时执行下面的代码块。
        if not client.bucket_exists(MINIO_BUCKET):
            # 中文注释：调用函数或方法，执行对应的业务处理。
            client.make_bucket(MINIO_BUCKET)

        # 中文注释：调用函数或方法，执行对应的业务处理。
        file.file.seek(0)
        # 中文注释：设置变量或字段 file_size 的值，供后续逻辑使用。
        file_size = _get_file_size(file.file)
        # 中文注释：调用函数或方法，执行对应的业务处理。
        file.file.seek(0)
        # 中文注释：调用函数或方法，执行对应的业务处理。
        client.put_object(
            MINIO_BUCKET,
            object_name,
            file.file,
            length=file_size,
            content_type=content_type,
        )
        # 中文注释：设置变量或字段 presigned_url 的值，供后续逻辑使用。
        presigned_url = client.presigned_get_object(MINIO_BUCKET, object_name, expires=timedelta(hours=1))
    # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
    except s3_error as exc:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=502, detail=f'MinIO 上传失败：{exc}') from exc
    # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
    except OSError as exc:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=500, detail=f'读取上传文件失败：{exc}') from exc
    # 中文注释：捕获指定异常，并执行对应的错误处理逻辑。
    except Exception as exc:
        # 中文注释：主动抛出异常，将错误信息交给上层处理。
        raise HTTPException(status_code=502, detail=f'无法连接或写入 MinIO：{exc}') from exc

    # 中文注释：返回当前函数处理后的结果。
    return {
        'bucket': MINIO_BUCKET,
        'object_name': object_name,
        'filename': safe_name,
        'content_type': content_type,
        'size': file_size,
        'public_url': f'{MINIO_PUBLIC_ENDPOINT.rstrip("/")}/{MINIO_BUCKET}/{object_name}',
        'presigned_url': presigned_url,
    }


def download_file_from_minio(object_name: str, bucket: str | None = None) -> dict[str, object]:
    # 从 MinIO 读取对象内容，供后续文件切片和向量化使用。
    if not object_name:
        raise HTTPException(status_code=400, detail='object_name 不能为空。')

    client, s3_error = _get_minio_client()
    target_bucket = bucket or MINIO_BUCKET
    response = None
    try:
        response = client.get_object(target_bucket, object_name)
        data = response.read()
        stat = client.stat_object(target_bucket, object_name)
    except s3_error as exc:
        raise HTTPException(status_code=502, detail=f'MinIO 读取失败：{exc}') from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f'无法连接或读取 MinIO：{exc}') from exc
    finally:
        if response is not None:
            response.close()
            response.release_conn()

    return {
        'bucket': target_bucket,
        'object_name': object_name,
        'filename': Path(object_name).name.split('_', 1)[-1] or Path(object_name).name,
        'content_type': stat.content_type or 'application/octet-stream',
        'size': int(stat.size or len(data)),
        'data': data,
    }


def get_presigned_file_url(object_name: str, bucket: str | None = None, *, hours: int = 1) -> str:
    # 为已保存的 MinIO 对象生成临时访问链接，供前端图片/音频/视频/文档预览使用。
    if not object_name:
        raise HTTPException(status_code=400, detail='object_name 不能为空。')

    client, s3_error = _get_minio_client()
    target_bucket = bucket or MINIO_BUCKET
    try:
        return client.presigned_get_object(target_bucket, object_name, expires=timedelta(hours=hours))
    except s3_error as exc:
        raise HTTPException(status_code=502, detail=f'MinIO 生成访问链接失败：{exc}') from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f'无法连接 MinIO：{exc}') from exc
