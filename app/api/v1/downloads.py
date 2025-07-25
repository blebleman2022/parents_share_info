"""
下载相关API
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.resource import Resource, Download
from app.services.point_service import deduct_points, add_points, check_daily_download_limit, increment_daily_downloads
from app.services.file_service import get_file_mime_type


router = APIRouter()


@router.post("/{resource_id}", summary="下载资源")
async def download_resource(
    resource_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """下载资源"""
    # 检查资源是否存在
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
    
    # 检查是否是自己上传的资源（自己的资源免费下载）
    if resource.uploader_id == current_user.id:
        download_url = f"/uploads/resources/{os.path.basename(resource.file_path)}"
        return {
            "message": "下载成功（自己的资源免费）",
            "download_url": download_url
        }
    
    # 检查是否已经下载过（避免重复扣积分）
    existing_download = await db.execute(
        select(Download).where(
            Download.user_id == current_user.id,
            Download.resource_id == resource_id
        )
    )
    
    if existing_download.scalar_one_or_none():
        download_url = f"/uploads/resources/{os.path.basename(resource.file_path)}"
        return {
            "message": "下载成功（已购买过的资源）",
            "download_url": download_url
        }
    
    # 检查每日下载限制
    if not await check_daily_download_limit(db, current_user):
        level_config = settings.USER_LEVELS.get(current_user.level, {})
        daily_limit = level_config.get("daily_downloads", 5)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"已达到每日下载限制（{daily_limit}次），请明天再试或提升用户等级"
        )
    
    # 检查积分是否足够
    download_cost = settings.POINTS_CONFIG["download"]
    if current_user.points < download_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"积分不足，需要{download_cost}积分"
        )
    
    try:
        # 扣除下载积分
        await deduct_points(
            db=db,
            user_id=current_user.id,
            points=download_cost,
            transaction_type="download",
            description=f"下载资源: {resource.title}",
            related_resource_id=resource_id
        )
        
        # 给上传者奖励积分
        await add_points(
            db=db,
            user_id=resource.uploader_id,
            points=settings.POINTS_CONFIG["download_reward"],
            transaction_type="download_reward",
            description=f"资源被下载: {resource.title}",
            related_resource_id=resource_id
        )
        
        # 创建下载记录
        download_record = Download(
            user_id=current_user.id,
            resource_id=resource_id,
            points_cost=download_cost
        )
        db.add(download_record)
        
        # 增加资源下载次数
        resource.download_count += 1
        
        # 增加用户每日下载次数
        await increment_daily_downloads(db, current_user)
        
        await db.commit()
        
        # 返回下载链接
        download_url = f"/uploads/resources/{os.path.basename(resource.file_path)}"
        
        return {
            "message": "下载成功",
            "download_url": download_url,
            "points_cost": download_cost
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="下载失败，请重试"
        )


@router.get("/file/{resource_id}", summary="直接下载文件")
async def download_file(
    resource_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """直接下载文件（需要先通过下载接口获得权限）"""
    # 检查资源是否存在
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
    
    # 检查下载权限（是否是上传者或已购买）
    if resource.uploader_id != current_user.id:
        existing_download = await db.execute(
            select(Download).where(
                Download.user_id == current_user.id,
                Download.resource_id == resource_id
            )
        )
        
        if not existing_download.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限下载该资源，请先购买"
            )
    
    # 检查文件是否存在
    if not os.path.exists(resource.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 获取文件MIME类型
    media_type = get_file_mime_type(resource.file_path)
    
    # 返回文件
    return FileResponse(
        path=resource.file_path,
        filename=resource.file_name,
        media_type=media_type
    )


@router.get("/history", summary="获取下载历史")
async def get_download_history(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户下载历史"""
    result = await db.execute(
        select(Download, Resource)
        .join(Resource, Download.resource_id == Resource.id)
        .where(Download.user_id == current_user.id)
        .order_by(Download.created_at.desc())
    )
    
    downloads = []
    for download, resource in result.all():
        downloads.append({
            "id": download.id,
            "resource_id": resource.id,
            "resource_title": resource.title,
            "resource_type": resource.resource_type,
            "grade": resource.grade,
            "subject": resource.subject,
            "points_cost": download.points_cost,
            "download_time": download.created_at
        })
    
    return {
        "downloads": downloads,
        "total": len(downloads)
    }
