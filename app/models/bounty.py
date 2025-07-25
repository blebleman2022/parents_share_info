"""
悬赏数据模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Bounty(Base):
    """悬赏模型"""
    __tablename__ = "bounties"
    
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    grade = Column(String(20), nullable=False)
    subject = Column(String(20), nullable=False)
    points_reward = Column(Integer, nullable=False)  # 悬赏积分
    status = Column(String(20), default="active")  # 状态：active, completed, expired
    winner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    winning_resource_id = Column(Integer, ForeignKey("resources.id", ondelete="SET NULL"))
    expires_at = Column(DateTime(timezone=True), nullable=False)  # 过期时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    creator = relationship("User", foreign_keys=[creator_id])
    winner = relationship("User", foreign_keys=[winner_id])
    winning_resource = relationship("Resource")
    responses = relationship("BountyResponse", back_populates="bounty")


class BountyResponse(Base):
    """悬赏响应模型"""
    __tablename__ = "bounty_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    bounty_id = Column(Integer, ForeignKey("bounties.id", ondelete="CASCADE"), nullable=False)
    responder_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text)  # 响应说明
    is_selected = Column(Boolean, default=False)  # 是否被选中
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    bounty = relationship("Bounty", back_populates="responses")
    responder = relationship("User")
    resource = relationship("Resource", back_populates="bounty_responses")
