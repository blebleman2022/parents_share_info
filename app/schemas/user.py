"""
用户相关数据传输对象
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class UserBase(BaseModel):
    """用户基础信息"""
    nickname: str = Field(..., description="昵称")
    child_grade: Optional[str] = Field(None, description="孩子年级")
    city: Optional[str] = Field(None, description="所在城市")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    phone: str
    nickname: str
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    child_grade: Optional[str] = None
    points: int
    level: str
    daily_downloads: int
    last_signin_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """用户信息更新"""
    nickname: Optional[str] = Field(None, min_length=2, max_length=20, description="昵称")
    child_grade: Optional[str] = Field(None, description="孩子年级")
    city: Optional[str] = Field(None, max_length=50, description="所在城市")


class UserStats(BaseModel):
    """用户统计信息"""
    total_uploads: int = Field(..., description="总上传数")
    total_downloads: int = Field(..., description="总下载数")
    total_points_earned: int = Field(..., description="总获得积分")
    total_points_spent: int = Field(..., description="总消耗积分")
    bounties_created: int = Field(..., description="创建的悬赏数")
    bounties_won: int = Field(..., description="获胜的悬赏数")
