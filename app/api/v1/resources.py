"""
资源相关API
"""
import os
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.resource import Resource
from app.schemas.resource import ResourceResponse, ResourceCreate, ResourceList
from app.services.point_service import add_points
from app.services.file_service import save_uploaded_file, validate_file


router = APIRouter()


@router.get("/", response_model=ResourceList, summary="获取资源列表")
async def get_resources(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（同时搜索标题和描述）"),
    grade: Optional[str] = Query(None, description="年级筛选"),
    subject: Optional[str] = Query(None, description="科目筛选"),
    resource_type: Optional[str] = Query(None, description="资源类型筛选"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    db: AsyncSession = Depends(get_db)
):
    """获取资源列表"""
    # 构建查询条件
    conditions = [Resource.is_active == True]
    
    if keyword:
        conditions.append(
            or_(
                Resource.title.ilike(f"%{keyword}%"),
                Resource.description.ilike(f"%{keyword}%")
            )
        )
    
    if grade:
        # 支持多选年级搜索：如果年级字段包含搜索的年级，或者年级字段为空
        conditions.append(
            or_(
                Resource.grade.ilike(f"%{grade}%"),  # 包含该年级
                Resource.grade == "",  # 或者年级为空
                Resource.grade.is_(None)  # 或者年级为NULL
            )
        )
    
    if subject:
        conditions.append(Resource.subject == subject)

    if resource_type:
        conditions.append(Resource.resource_type == resource_type)

    # 构建查询
    query = select(Resource).where(and_(*conditions))
    
    # 排序
    if sort_by == "download_count":
        if sort_order == "desc":
            query = query.order_by(Resource.download_count.desc())
        else:
            query = query.order_by(Resource.download_count.asc())
    else:  # 默认按创建时间排序
        if sort_order == "desc":
            query = query.order_by(Resource.created_at.desc())
        else:
            query = query.order_by(Resource.created_at.asc())
    
    # 分页
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # 执行查询
    result = await db.execute(query)
    resources = result.scalars().all()

    # 获取总数
    count_query = select(Resource).where(and_(*conditions))
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    return {
        "items": resources,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.post("/", response_model=ResourceResponse, summary="上传资源")
async def upload_resource(
    title: str = Form(..., description="资源标题"),
    resource_type: str = Form(..., description="资源类型"),
    grade: Optional[str] = Form(None, description="年级（可多选，用逗号分隔）"),
    subject: Optional[str] = Form(None, description="科目"),
    description: Optional[str] = Form(None, description="资源描述"),
    file: UploadFile = File(..., description="上传文件"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传资源"""
    # 验证文件
    validate_file(file)
    
    # 保存文件
    file_path, file_name = await save_uploaded_file(file, "resources")
    
    try:
        # 创建资源记录
        resource = Resource(
            uploader_id=current_user.id,
            title=title,
            description=description or "",
            file_name=file_name,
            file_path=file_path,
            file_size=file.size,
            file_type=file.filename.split('.')[-1].lower(),
            grade=grade or "",
            subject=subject or "",
            resource_type=resource_type
        )
        
        db.add(resource)
        await db.commit()
        await db.refresh(resource)
        
        # 添加上传奖励积分
        await add_points(
            db=db,
            user_id=current_user.id,
            points=settings.POINTS_CONFIG["upload"],
            transaction_type="upload",
            description=f"上传资源: {title}",
            related_resource_id=resource.id
        )
        
        return resource
        
    except Exception as e:
        # 如果数据库操作失败，删除已上传的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="资源上传失败"
        )


@router.get("/{resource_id}", response_model=ResourceResponse, summary="获取资源详情")
async def get_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取资源详情"""
    result = await db.execute(
        select(Resource).where(
            Resource.id == resource_id,
            Resource.is_active == True
        )
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    return resource



