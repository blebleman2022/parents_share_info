"""
举报和用户行为数据模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
# from sqlalchemy.dialects.postgresql import INET

from app.core.database import Base


class Report(Base):
    """举报模型"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reported_resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"))
    reported_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    report_type = Column(String(20), nullable=False)  # 举报类型
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # 状态：pending, resolved, rejected
    admin_response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    reporter = relationship("User", foreign_keys=[reporter_id])
    reported_resource = relationship("Resource", back_populates="reports")
    reported_user = relationship("User", foreign_keys=[reported_user_id])


class UserAction(Base):
    """用户行为日志模型"""
    __tablename__ = "user_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(50), nullable=False)  # 行为类型
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="SET NULL"))
    details = Column(JSON)  # 行为详情（JSON格式）
    ip_address = Column(String(45))  # 支持IPv4和IPv6
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User")
    resource = relationship("Resource")


class SystemConfig(Base):
    """系统配置模型"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
