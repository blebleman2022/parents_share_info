"""
资源相关数据传输对象
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class ResourceBase(BaseModel):
    """资源基础信息"""
    title: str = Field(..., min_length=1, max_length=200, description="资源标题")
    description: str = Field(..., description="资源描述")
    grade: str = Field(..., description="年级")
    subject: str = Field(..., description="科目")
    resource_type: str = Field(..., description="资源类型")
    
    @validator('grade')
    def validate_grade(cls, v):
        # 允许空年级
        if not v or v.strip() == "":
            return v

        valid_grades = [
            "小学1年级", "小学2年级", "小学3年级", "小学4年级", "小学5年级", "预初",
            "初中1年级", "初中2年级", "初中3年级",
            "高中1年级", "高中2年级", "高中3年级"
        ]

        # 支持多选年级（逗号分隔）
        if ',' in v:
            grades = [grade.strip() for grade in v.split(',')]
            for grade in grades:
                if grade and grade not in valid_grades:
                    raise ValueError(f'年级选择不正确: {grade}')
        else:
            if v not in valid_grades:
                raise ValueError('年级选择不正确')
        return v
    
    @validator('subject')
    def validate_subject(cls, v):
        # 允许空科目
        if not v or v.strip() == "":
            return v

        valid_subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
        if v not in valid_subjects:
            raise ValueError('科目选择不正确')
        return v
    
    @validator('resource_type')
    def validate_resource_type(cls, v):
        valid_types = ['课件', '教案', '学案', '作业', '试卷', '题集', '素材', '备课包', '其他']
        if v not in valid_types:
            raise ValueError('资源类型选择不正确')
        return v


class ResourceCreate(ResourceBase):
    """创建资源请求"""
    pass


class ResourceResponse(ResourceBase):
    """资源响应"""
    id: int
    uploader_id: int
    file_name: str
    file_size: int
    file_type: str
    download_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceList(BaseModel):
    """资源列表响应"""
    items: List[ResourceResponse]
    total: int
    page: int
    size: int
    pages: int


class ResourceUpdate(BaseModel):
    """更新资源请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="资源标题")
    description: Optional[str] = Field(None, min_length=1, description="资源描述")
    grade: Optional[str] = Field(None, description="年级")
    subject: Optional[str] = Field(None, description="科目")
    resource_type: Optional[str] = Field(None, description="资源类型")
