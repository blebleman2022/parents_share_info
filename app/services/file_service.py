"""
文件处理服务
"""
import os
import uuid
try:
    import magic
except ImportError:
    magic = None
from typing import Tuple
from fastapi import HTTPException, status, UploadFile

from app.core.config import settings


def validate_file(file: UploadFile) -> None:
    """验证上传文件"""
    # 检查文件大小
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制（{settings.MAX_FILE_SIZE // 1024 // 1024}MB）"
        )
    
    # 检查文件扩展名
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )
    
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，支持的格式：{', '.join(settings.ALLOWED_FILE_TYPES)}"
        )


async def save_uploaded_file(file: UploadFile, subfolder: str) -> Tuple[str, str]:
    """保存上传的文件"""
    # 生成唯一文件名
    file_ext = file.filename.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    
    # 创建保存路径
    save_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(save_dir, exist_ok=True)
    
    file_path = os.path.join(save_dir, unique_filename)
    
    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return file_path, unique_filename
        
    except Exception as e:
        # 如果保存失败，删除可能创建的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件保存失败"
        )


def get_file_mime_type(file_path: str) -> str:
    """获取文件MIME类型"""
    if magic:
        try:
            mime = magic.Magic(mime=True)
            return mime.from_file(file_path)
        except:
            pass
    # 根据扩展名返回默认类型
        ext = file_path.split('.')[-1].lower()
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        return mime_types.get(ext, 'application/octet-stream')


def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except:
        return False
