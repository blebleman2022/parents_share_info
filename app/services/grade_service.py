"""
年级管理服务
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.user import User
from app.core.config import settings


class GradeService:
    """年级管理服务类"""
    
    # 年级升级映射表
    GRADE_UPGRADE_MAP = {
        "小学1年级": "小学2年级",
        "小学2年级": "小学3年级",
        "小学3年级": "小学4年级",
        "小学4年级": "小学5年级",
        "小学5年级": "预初",
        "预初": "初中1年级",
        "初中1年级": "初中2年级",
        "初中2年级": "初中3年级",
        "初中3年级": "高中1年级",
        "高中1年级": "高中2年级",
        "高中2年级": "高中3年级",
        "高中3年级": "高中3年级"  # 高三不再升级
    }
    
    @classmethod
    def get_next_grade(cls, current_grade: str) -> str:
        """
        获取下一个年级
        
        Args:
            current_grade: 当前年级
            
        Returns:
            str: 下一个年级
        """
        return cls.GRADE_UPGRADE_MAP.get(current_grade, current_grade)
    
    @classmethod
    def should_upgrade_grade(cls) -> bool:
        """
        判断是否应该升级年级
        每年7月1日开始可以升级（暑假期间）

        Returns:
            bool: 是否应该升级
        """
        now = datetime.now()
        current_year = now.year

        # 7月1日作为升级日期（暑假开始）
        upgrade_date = date(current_year, 7, 1)
        today = date.today()

        # 如果今天是7月1日或之后，且用户的年级还没有在今年升级过
        return today >= upgrade_date
    
    @classmethod
    async def upgrade_user_grade(cls, db: AsyncSession, user: User, force: bool = False) -> bool:
        """
        升级单个用户的年级

        Args:
            db: 数据库会话
            user: 用户对象
            force: 是否强制升级（忽略时间限制）

        Returns:
            bool: 是否升级成功
        """
        if not force and not cls.should_upgrade_grade():
            return False
        
        # 检查用户是否已经在今年升级过
        current_year = datetime.now().year
        if user.last_grade_upgrade_year == current_year:
            return False
        
        # 获取下一个年级
        next_grade = cls.get_next_grade(user.child_grade)
        
        # 如果年级没有变化（如高三），则不升级
        if next_grade == user.child_grade:
            return False
        
        # 更新用户年级
        user.child_grade = next_grade
        user.last_grade_upgrade_year = current_year
        
        await db.commit()
        return True
    
    @classmethod
    async def upgrade_all_users_grade(cls, db: AsyncSession, force: bool = False) -> int:
        """
        批量升级所有用户的年级

        Args:
            db: 数据库会话
            force: 是否强制升级（忽略时间限制）

        Returns:
            int: 升级的用户数量
        """
        if not force and not cls.should_upgrade_grade():
            return 0
        
        current_year = datetime.now().year
        
        # 查询需要升级的用户（今年还没有升级过的）
        result = await db.execute(
            select(User).where(
                User.is_active == True,
                User.last_grade_upgrade_year != current_year
            )
        )
        users = result.scalars().all()
        
        upgraded_count = 0
        
        for user in users:
            next_grade = cls.get_next_grade(user.child_grade)
            
            # 如果年级有变化，则升级
            if next_grade != user.child_grade:
                user.child_grade = next_grade
                user.last_grade_upgrade_year = current_year
                upgraded_count += 1
        
        if upgraded_count > 0:
            await db.commit()
        
        return upgraded_count
    
    @classmethod
    async def check_and_upgrade_user_grade(cls, db: AsyncSession, user: User) -> Optional[str]:
        """
        检查并升级用户年级（用户登录时调用）
        
        Args:
            db: 数据库会话
            user: 用户对象
            
        Returns:
            Optional[str]: 如果升级了，返回新年级；否则返回None
        """
        if await cls.upgrade_user_grade(db, user):
            await db.refresh(user)
            return user.child_grade
        return None


# 创建全局年级服务实例
grade_service = GradeService()
