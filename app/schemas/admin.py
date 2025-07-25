"""
管理员相关的Pydantic模型
"""
from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== 系统配置相关 ====================

class SystemConfigBase(BaseModel):
    config_key: str = Field(..., description="配置键")
    config_value: Dict[str, Any] = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")


class SystemConfigCreate(SystemConfigBase):
    pass


class SystemConfigUpdate(BaseModel):
    config_value: Optional[Dict[str, Any]] = Field(None, description="配置值")
    description: Optional[str] = Field(None, description="配置描述")


class SystemConfigResponse(SystemConfigBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 管理员日志相关 ====================

class AdminLogResponse(BaseModel):
    id: int
    admin_phone: str = Field(..., description="管理员手机号")
    action_type: str = Field(..., description="操作类型")
    target_type: Optional[str] = Field(None, description="操作目标类型")
    target_id: Optional[str] = Field(None, description="操作目标ID")
    action_description: Optional[str] = Field(None, description="操作描述")
    old_data: Optional[Dict[str, Any]] = Field(None, description="修改前数据")
    new_data: Optional[Dict[str, Any]] = Field(None, description="修改后数据")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 用户管理相关 ====================

class UserManageResponse(BaseModel):
    id: int
    phone: str
    nickname: str
    avatar_url: Optional[str]
    city: Optional[str]
    child_grade: Optional[str]
    points: int
    level: str
    daily_downloads: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    points: Optional[int] = Field(None, description="积分")
    level: Optional[str] = Field(None, description="用户等级")
    is_active: Optional[bool] = Field(None, description="是否激活")


# ==================== 资源管理相关 ====================

class ResourceManageResponse(BaseModel):
    id: int
    uploader_id: int
    title: str
    description: Optional[str]
    file_name: str
    file_size: int
    file_type: str
    grade: Optional[str]
    subject: Optional[str]
    resource_type: str
    download_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResourceUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, description="资源标题")
    description: Optional[str] = Field(None, description="资源描述")
    grade: Optional[str] = Field(None, description="年级")
    subject: Optional[str] = Field(None, description="科目")
    is_active: Optional[bool] = Field(None, description="是否激活")


# ==================== 统计数据相关 ====================

class AdminStatsResponse(BaseModel):
    total_users: int = Field(..., description="总用户数")
    active_users: int = Field(..., description="活跃用户数")
    total_resources: int = Field(..., description="总资源数")
    active_resources: int = Field(..., description="有效资源数")
    total_downloads: int = Field(..., description="总下载次数")
    today_uploads: int = Field(..., description="今日上传数")
    today_downloads: int = Field(..., description="今日下载数")
    today_registrations: int = Field(..., description="今日注册数")


# ==================== 积分规则配置 ====================

class PointRulesConfig(BaseModel):
    register_points: int = Field(100, description="注册奖励积分")
    upload_points: int = Field(20, description="上传资源奖励积分")
    download_cost: int = Field(5, description="下载资源消耗积分")
    daily_signin_points: int = Field(10, description="每日签到奖励积分")
    daily_download_limit: int = Field(10, description="每日下载次数限制")


class UserLevelConfig(BaseModel):
    levels: Dict[str, Dict[str, Any]] = Field(
        default={
            "新手用户": {"min_points": 0, "max_points": 499, "daily_downloads": 5},
            "活跃用户": {"min_points": 500, "max_points": 1999, "daily_downloads": 10},
            "资深用户": {"min_points": 2000, "max_points": 4999, "daily_downloads": 15},
            "专家用户": {"min_points": 5000, "max_points": -1, "daily_downloads": 20}
        },
        description="用户等级配置"
    )
