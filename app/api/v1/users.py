"""
用户相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserResponse, UserUpdate, UserStats
from app.crud.user import update_user, get_user_stats
from app.services.point_service import add_points
from app.core.config import settings


router = APIRouter()


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(current_user = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse, summary="更新用户信息")
async def update_me(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    updated_user = await update_user(
        db=db,
        user_id=current_user.id,
        **user_update.dict(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return updated_user


@router.post("/signin", summary="每日签到")
async def daily_signin(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """每日签到获取积分"""
    today = date.today()
    
    # 检查是否已经签到
    if current_user.last_signin_date == today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="今日已签到"
        )
    
    # 添加签到积分
    await add_points(
        db=db,
        user_id=current_user.id,
        points=settings.POINTS_CONFIG["signin"],
        transaction_type="signin",
        description="每日签到奖励"
    )
    
    # 更新签到日期
    current_user.last_signin_date = today
    await db.commit()
    
    return {
        "message": "签到成功",
        "points_earned": settings.POINTS_CONFIG["signin"]
    }


@router.get("/stats", response_model=UserStats, summary="获取用户统计信息")
async def get_user_statistics(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户统计信息"""
    stats = await get_user_stats(db, current_user.id)
    return stats
