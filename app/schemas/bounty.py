"""
悬赏相关数据传输对象
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class BountyBase(BaseModel):
    """悬赏基础信息"""
    title: str = Field(..., min_length=1, max_length=200, description="悬赏标题")
    description: str = Field(..., min_length=1, description="悬赏描述")
    grade: str = Field(..., description="年级")
    subject: str = Field(..., description="科目")
    points_reward: int = Field(..., ge=50, description="悬赏积分")
    
    @validator('grade')
    def validate_grade(cls, v):
        valid_grades = [
            "小学1年级", "小学2年级", "小学3年级", "小学4年级", "小学5年级", "预初",
            "初中1年级", "初中2年级", "初中3年级",
            "高中1年级", "高中2年级", "高中3年级"
        ]
        if v not in valid_grades:
            raise ValueError('年级选择不正确')
        return v
    
    @validator('subject')
    def validate_subject(cls, v):
        valid_subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
        if v not in valid_subjects:
            raise ValueError('科目选择不正确')
        return v


class BountyCreate(BountyBase):
    """创建悬赏请求"""
    pass


class BountyResponse(BountyBase):
    """悬赏响应"""
    id: int
    creator_id: int
    status: str
    winner_id: Optional[int] = None
    winning_resource_id: Optional[int] = None
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BountyList(BaseModel):
    """悬赏列表响应"""
    items: List[BountyResponse]
    total: int
    page: int
    size: int
    pages: int


class BountyResponseCreate(BaseModel):
    """悬赏响应创建请求"""
    resource_id: int = Field(..., description="资源ID")
    message: Optional[str] = Field(None, max_length=500, description="响应说明")


class BountyResponseInfo(BaseModel):
    """悬赏响应信息"""
    id: int
    bounty_id: int
    responder_id: int
    resource_id: int
    message: Optional[str] = None
    is_selected: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
