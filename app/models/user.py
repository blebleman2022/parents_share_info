"""
用户数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(11), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=False)
    avatar_url = Column(String(255))
    city = Column(String(50))
    child_grade = Column(String(20))  # 孩子年级
    points = Column(Integer, default=100)  # 积分
    level = Column(String(20), default="新手用户")  # 用户等级
    daily_downloads = Column(Integer, default=0)  # 当日下载次数
    last_download_date = Column(Date)  # 最后下载日期
    last_signin_date = Column(Date)  # 最后签到日期
    last_grade_upgrade_year = Column(Integer)  # 最后年级升级年份
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系 - 使用字符串引用避免循环导入
    # uploaded_resources = relationship("Resource", back_populates="uploader")
    # downloads = relationship("Download", back_populates="user")
    # point_transactions = relationship("PointTransaction", back_populates="user")
    # created_bounties = relationship("Bounty", back_populates="creator")
    # won_bounties = relationship("Bounty", back_populates="winner")
    # bounty_responses = relationship("BountyResponse", back_populates="responder")
    # favorites = relationship("Favorite", back_populates="user")
    # reports_made = relationship("Report", back_populates="reporter")
    # user_actions = relationship("UserAction", back_populates="user")
