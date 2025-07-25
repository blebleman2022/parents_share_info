"""
积分服务
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.resource import PointTransaction
from app.crud.user import update_user_level


async def add_points(
    db: AsyncSession,
    user_id: int,
    points: int,
    transaction_type: str,
    description: Optional[str] = None,
    related_resource_id: Optional[int] = None,
    related_bounty_id: Optional[int] = None
) -> PointTransaction:
    """添加积分"""
    # 获取用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError("用户不存在")
    
    # 更新用户积分
    user.points += points
    
    # 创建积分变动记录
    transaction = PointTransaction(
        user_id=user_id,
        transaction_type=transaction_type,
        points_change=points,
        description=description,
        related_resource_id=related_resource_id,
        related_bounty_id=related_bounty_id
    )
    
    db.add(transaction)
    await db.commit()
    
    # 更新用户等级
    await update_user_level(db, user)
    
    await db.refresh(transaction)
    return transaction


async def deduct_points(
    db: AsyncSession,
    user_id: int,
    points: int,
    transaction_type: str,
    description: Optional[str] = None,
    related_resource_id: Optional[int] = None,
    related_bounty_id: Optional[int] = None
) -> PointTransaction:
    """扣除积分"""
    # 获取用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError("用户不存在")
    
    if user.points < points:
        raise ValueError("积分不足")
    
    # 更新用户积分
    user.points -= points
    
    # 创建积分变动记录
    transaction = PointTransaction(
        user_id=user_id,
        transaction_type=transaction_type,
        points_change=-points,
        description=description,
        related_resource_id=related_resource_id,
        related_bounty_id=related_bounty_id
    )
    
    db.add(transaction)
    await db.commit()
    
    # 更新用户等级
    await update_user_level(db, user)
    
    await db.refresh(transaction)
    return transaction


async def transfer_points(
    db: AsyncSession,
    from_user_id: int,
    to_user_id: int,
    points: int,
    transaction_type: str,
    description: Optional[str] = None,
    related_bounty_id: Optional[int] = None
) -> tuple[PointTransaction, PointTransaction]:
    """转移积分"""
    # 扣除发送方积分
    deduct_transaction = await deduct_points(
        db=db,
        user_id=from_user_id,
        points=points,
        transaction_type=transaction_type,
        description=f"转出积分: {description}",
        related_bounty_id=related_bounty_id
    )
    
    # 添加接收方积分
    add_transaction = await add_points(
        db=db,
        user_id=to_user_id,
        points=points,
        transaction_type=transaction_type,
        description=f"收到积分: {description}",
        related_bounty_id=related_bounty_id
    )
    
    return deduct_transaction, add_transaction


async def check_daily_download_limit(db: AsyncSession, user: User) -> bool:
    """检查每日下载限制"""
    from app.core.config import settings
    from datetime import date
    
    # 如果不是今天，重置下载次数
    today = date.today()
    if user.last_download_date != today:
        user.daily_downloads = 0
        user.last_download_date = today
        await db.commit()
    
    # 获取用户等级的下载限制
    level_config = settings.USER_LEVELS.get(user.level, {})
    daily_limit = level_config.get("daily_downloads", 5)
    
    # -1表示无限制
    if daily_limit == -1:
        return True
    
    return user.daily_downloads < daily_limit


async def increment_daily_downloads(db: AsyncSession, user: User):
    """增加每日下载次数"""
    from datetime import date
    
    today = date.today()
    if user.last_download_date != today:
        user.daily_downloads = 1
        user.last_download_date = today
    else:
        user.daily_downloads += 1
    
    await db.commit()
