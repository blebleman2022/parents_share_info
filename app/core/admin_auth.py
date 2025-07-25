"""
管理员认证中间件
"""
from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, AdminLog


# 管理员手机号（硬编码，只有这个号码可以访问管理员功能）
ADMIN_PHONE = "13901119451"


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取管理员用户
    只有特定手机号的用户才能访问管理员功能
    """
    if current_user.phone != ADMIN_PHONE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问管理员功能"
        )
    return current_user


async def log_admin_action(
    admin_phone: str,
    action_type: str,
    action_description: str,
    target_type: str = None,
    target_id: str = None,
    old_data: dict = None,
    new_data: dict = None,
    request: Request = None,
    db: AsyncSession = None
):
    """
    记录管理员操作日志
    """
    try:
        ip_address = None
        user_agent = None
        
        if request:
            # 获取真实IP地址
            ip_address = request.headers.get("X-Forwarded-For")
            if not ip_address:
                ip_address = request.headers.get("X-Real-IP")
            if not ip_address:
                ip_address = request.client.host if request.client else None
            
            # 获取用户代理
            user_agent = request.headers.get("User-Agent")
        
        admin_log = AdminLog(
            admin_phone=admin_phone,
            action_type=action_type,
            target_type=target_type,
            target_id=str(target_id) if target_id else None,
            action_description=action_description,
            old_data=old_data,
            new_data=new_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if db:
            db.add(admin_log)
            await db.commit()
            
    except Exception as e:
        # 日志记录失败不应该影响主要功能
        print(f"记录管理员操作日志失败: {e}")


def is_admin_phone(phone: str) -> bool:
    """
    检查是否为管理员手机号
    """
    return phone == ADMIN_PHONE
