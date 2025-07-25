"""
管理员相关数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class AdminLog(Base):
    """管理员操作日志模型"""
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_phone = Column(String(11), nullable=False)  # 管理员手机号
    action_type = Column(String(50), nullable=False)  # 操作类型
    target_type = Column(String(50))  # 操作目标类型（user/resource/config等）
    target_id = Column(String(50))  # 操作目标ID
    action_description = Column(Text)  # 操作描述
    old_data = Column(JSON)  # 修改前的数据
    new_data = Column(JSON)  # 修改后的数据
    ip_address = Column(String(45))  # IP地址
    user_agent = Column(String(500))  # 用户代理
    created_at = Column(DateTime(timezone=True), server_default=func.now())
