"""
用户CRUD操作
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.resource import Resource, Download, PointTransaction
from app.models.bounty import Bounty
from app.core.config import settings


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
    """根据手机号获取用户"""
    result = await db.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    phone: str,
    password_hash: str,
    nickname: str,
    child_grade: str
) -> User:
    """创建用户"""
    user = User(
        phone=phone,
        password_hash=password_hash,
        nickname=nickname,
        child_grade=child_grade,
        points=settings.POINTS_CONFIG["register"]
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession,
    user_id: int,
    **kwargs
) -> Optional[User]:
    """更新用户信息"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_level(db: AsyncSession, user: User) -> User:
    """更新用户等级"""
    points = user.points
    
    for level_name, level_config in settings.USER_LEVELS.items():
        min_points = level_config["min_points"]
        max_points = level_config["max_points"]
        
        if max_points == -1:  # 无上限
            if points >= min_points:
                user.level = level_name
                break
        else:
            if min_points <= points <= max_points:
                user.level = level_name
                break
    
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_stats(db: AsyncSession, user_id: int) -> dict:
    """获取用户统计信息"""
    # 总上传数
    upload_count = await db.execute(
        select(func.count(Resource.id)).where(Resource.uploader_id == user_id)
    )
    total_uploads = upload_count.scalar() or 0
    
    # 总下载数
    download_count = await db.execute(
        select(func.count(Download.id)).where(Download.user_id == user_id)
    )
    total_downloads = download_count.scalar() or 0
    
    # 总获得积分
    earned_points = await db.execute(
        select(func.sum(PointTransaction.points_change))
        .where(
            PointTransaction.user_id == user_id,
            PointTransaction.points_change > 0
        )
    )
    total_points_earned = earned_points.scalar() or 0
    
    # 总消耗积分
    spent_points = await db.execute(
        select(func.sum(PointTransaction.points_change))
        .where(
            PointTransaction.user_id == user_id,
            PointTransaction.points_change < 0
        )
    )
    total_points_spent = abs(spent_points.scalar() or 0)
    
    # 创建的悬赏数
    created_bounties = await db.execute(
        select(func.count(Bounty.id)).where(Bounty.creator_id == user_id)
    )
    bounties_created = created_bounties.scalar() or 0
    
    # 获胜的悬赏数
    won_bounties = await db.execute(
        select(func.count(Bounty.id)).where(Bounty.winner_id == user_id)
    )
    bounties_won = won_bounties.scalar() or 0
    
    return {
        "total_uploads": total_uploads,
        "total_downloads": total_downloads,
        "total_points_earned": total_points_earned,
        "total_points_spent": total_points_spent,
        "bounties_created": bounties_created,
        "bounties_won": bounties_won
    }
