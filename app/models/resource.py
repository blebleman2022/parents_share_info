"""
资源数据模型
"""
from sqlalchemy import Column, Integer, String, Text, BigInteger, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Resource(Base):
    """资源模型"""
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    uploader_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # 文件大小（字节）
    file_type = Column(String(50), nullable=False)  # 文件类型
    grade = Column(String(20), nullable=False)  # 年级
    subject = Column(String(20), nullable=False)  # 科目
    resource_type = Column(String(20), nullable=False)  # 资源类型
    download_count = Column(Integer, default=0)  # 下载次数
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    uploader = relationship("User", foreign_keys=[uploader_id])
    downloads = relationship("Download", back_populates="resource")
    bounty_responses = relationship("BountyResponse", back_populates="resource")
    favorites = relationship("Favorite", back_populates="resource")
    reports = relationship("Report", back_populates="reported_resource")


class Download(Base):
    """下载记录模型"""
    __tablename__ = "downloads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    points_cost = Column(Integer, default=10)  # 消耗积分
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User")
    resource = relationship("Resource", back_populates="downloads")


class PointTransaction(Base):
    """积分变动记录模型"""
    __tablename__ = "point_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 交易类型
    points_change = Column(Integer, nullable=False)  # 积分变化
    related_resource_id = Column(Integer, ForeignKey("resources.id", ondelete="SET NULL"))
    related_bounty_id = Column(Integer)  # 关联悬赏ID
    description = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User")
    related_resource = relationship("Resource")


class Favorite(Base):
    """收藏模型"""
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User")
    resource = relationship("Resource", back_populates="favorites")
