"""
搜索相关API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.core.database import get_db
from app.models.resource import Resource
from app.schemas.resource import ResourceList
from app.core.config import settings


router = APIRouter()


@router.get("/", response_model=ResourceList, summary="搜索资源")
async def search_resources(
    q: Optional[str] = Query(None, description="搜索关键词"),
    grade: Optional[str] = Query(None, description="年级筛选"),
    subject: Optional[str] = Query(None, description="科目筛选"),
    resource_type: Optional[str] = Query(None, description="资源类型筛选"),
    sort_by: str = Query("relevance", description="排序方式：relevance, created_at, download_count"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """搜索资源"""
    # 构建查询条件
    conditions = [Resource.is_active == True]
    
    # 关键词搜索
    if q:
        conditions.append(
            or_(
                Resource.title.ilike(f"%{q}%"),
                Resource.description.ilike(f"%{q}%")
            )
        )
    
    # 筛选条件
    if grade:
        conditions.append(Resource.grade == grade)
    
    if subject:
        conditions.append(Resource.subject == subject)
    
    if resource_type:
        conditions.append(Resource.resource_type == resource_type)
    
    # 构建查询
    query = select(Resource).where(and_(*conditions))
    
    # 排序
    if sort_by == "download_count":
        query = query.order_by(Resource.download_count.desc())
    elif sort_by == "created_at":
        query = query.order_by(Resource.created_at.desc())
    else:  # relevance - 简单的相关性排序
        if q:
            # 标题匹配优先，然后是下载量
            query = query.order_by(
                Resource.title.ilike(f"%{q}%").desc(),
                Resource.download_count.desc()
            )
        else:
            query = query.order_by(Resource.download_count.desc())
    
    # 分页
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # 执行查询
    result = await db.execute(query)
    resources = result.scalars().all()
    
    # 获取总数
    count_query = select(func.count(Resource.id)).where(and_(*conditions))
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return {
        "items": resources,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get("/hot", summary="获取热门资源")
async def get_hot_resources(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    db: AsyncSession = Depends(get_db)
):
    """获取热门资源（基于下载量）"""
    query = (
        select(Resource)
        .where(Resource.is_active == True)
        .order_by(Resource.download_count.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    resources = result.scalars().all()
    
    return {
        "resources": resources,
        "total": len(resources)
    }


@router.get("/categories", summary="获取分类统计")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """获取各分类的资源统计"""
    # 年级统计
    grade_stats = await db.execute(
        select(Resource.grade, func.count(Resource.id))
        .where(Resource.is_active == True)
        .group_by(Resource.grade)
        .order_by(Resource.grade)
    )
    
    # 科目统计
    subject_stats = await db.execute(
        select(Resource.subject, func.count(Resource.id))
        .where(Resource.is_active == True)
        .group_by(Resource.subject)
        .order_by(func.count(Resource.id).desc())
    )
    
    # 资源类型统计
    type_stats = await db.execute(
        select(Resource.resource_type, func.count(Resource.id))
        .where(Resource.is_active == True)
        .group_by(Resource.resource_type)
        .order_by(func.count(Resource.id).desc())
    )
    
    return {
        "grades": [{"name": grade, "count": count} for grade, count in grade_stats.all()],
        "subjects": [{"name": subject, "count": count} for subject, count in subject_stats.all()],
        "types": [{"name": type_name, "count": count} for type_name, count in type_stats.all()]
    }


@router.get("/suggestions", summary="获取搜索建议")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=20, description="建议数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取搜索建议"""
    # 基于标题的建议
    title_suggestions = await db.execute(
        select(Resource.title)
        .where(
            Resource.is_active == True,
            Resource.title.ilike(f"%{q}%")
        )
        .distinct()
        .limit(limit)
    )
    
    suggestions = [title for title, in title_suggestions.all()]
    
    return {
        "suggestions": suggestions[:limit]
    }
