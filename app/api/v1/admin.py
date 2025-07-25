"""
管理员API路由
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc, and_, or_

from app.core.database import get_db
from app.core.admin_auth import get_admin_user, log_admin_action
from app.models import User, Resource, SystemConfig, AdminLog, PointTransaction
from app.schemas.admin import (
    SystemConfigResponse, SystemConfigUpdate, SystemConfigCreate,
    AdminLogResponse, UserManageResponse, ResourceManageResponse,
    UserUpdateRequest, ResourceUpdateRequest
)

router = APIRouter(prefix="/admin", tags=["管理员"])


# ==================== 系统初始化 ====================

@router.post("/init", summary="初始化系统配置")
async def init_system_configs(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """初始化系统默认配置"""
    default_configs = [
        {
            "config_key": "point_rules",
            "config_value": {
                "register_points": 100,
                "upload_points": 20,
                "download_cost": 5,
                "daily_signin_points": 10,
                "daily_download_limit": 10
            },
            "description": "积分规则配置"
        },
        {
            "config_key": "user_levels",
            "config_value": {
                "新手用户": {"min_points": 0, "max_points": 499, "daily_downloads": 5},
                "活跃用户": {"min_points": 500, "max_points": 1999, "daily_downloads": 10},
                "资深用户": {"min_points": 2000, "max_points": 4999, "daily_downloads": 15},
                "专家用户": {"min_points": 5000, "max_points": -1, "daily_downloads": 20}
            },
            "description": "用户等级配置"
        },
        {
            "config_key": "system_settings",
            "config_value": {
                "max_file_size": 52428800,  # 50MB
                "allowed_file_types": ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "jpg", "png"],
                "auto_approve_resources": True,
                "maintenance_mode": False
            },
            "description": "系统基础设置"
        }
    ]

    created_count = 0
    for config_data in default_configs:
        # 检查配置是否已存在
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.config_key == config_data["config_key"])
        )
        existing_config = result.scalar_one_or_none()

        if not existing_config:
            # 将配置值序列化为JSON字符串
            config_value_str = json.dumps(config_data["config_value"], ensure_ascii=False)
            config = SystemConfig(
                config_key=config_data["config_key"],
                config_value=config_value_str,
                description=config_data["description"]
            )
            db.add(config)
            created_count += 1

    await db.commit()

    return {
        "message": f"系统初始化完成，创建了 {created_count} 个配置项",
        "created_count": created_count
    }


# ==================== 系统配置管理 ====================

@router.get("/configs", summary="获取系统配置列表")
async def get_system_configs(
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有系统配置"""
    result = await db.execute(
        select(SystemConfig).order_by(SystemConfig.config_key)
    )
    configs = result.scalars().all()

    # 转换配置值为JSON格式
    config_list = []
    for config in configs:
        try:
            config_value = json.loads(config.config_value) if isinstance(config.config_value, str) else config.config_value
        except (json.JSONDecodeError, TypeError):
            config_value = config.config_value

        config_list.append({
            "id": config.id,
            "config_key": config.config_key,
            "config_value": config_value,
            "description": config.description,
            "is_active": True,  # 默认为True，因为表中没有这个字段
            "created_at": config.created_at,
            "updated_at": config.updated_at
        })

    return config_list


@router.post("/configs", summary="创建系统配置")
async def create_system_config(
    config_data: SystemConfigCreate,
    request: Request,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """创建新的系统配置"""
    # 检查配置键是否已存在
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.config_key == config_data.config_key)
    )
    existing_config = result.scalar_one_or_none()

    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配置键已存在"
        )

    # 将配置值序列化为JSON字符串
    config_value_str = json.dumps(config_data.config_value, ensure_ascii=False)

    config = SystemConfig(
        config_key=config_data.config_key,
        config_value=config_value_str,
        description=config_data.description
    )

    db.add(config)
    await db.commit()
    await db.refresh(config)

    # 记录操作日志
    await log_admin_action(
        admin_phone=admin_user.phone,
        action_type="create_config",
        action_description=f"创建系统配置: {config_data.config_key}",
        target_type="config",
        target_id=config.id,
        new_data=config_data.dict(),
        request=request,
        db=db
    )

    # 返回格式化的配置
    return {
        "id": config.id,
        "config_key": config.config_key,
        "config_value": config_data.config_value,
        "description": config.description,
        "is_active": True,
        "created_at": config.created_at,
        "updated_at": config.updated_at
    }


@router.put("/configs/{config_id}", summary="更新系统配置")
async def update_system_config(
    config_id: int,
    config_data: SystemConfigUpdate,
    request: Request,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """更新系统配置"""
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )

    # 保存旧数据用于日志
    try:
        old_config_value = json.loads(config.config_value) if isinstance(config.config_value, str) else config.config_value
    except (json.JSONDecodeError, TypeError):
        old_config_value = config.config_value

    old_data = {
        "config_value": old_config_value,
        "description": config.description
    }

    # 更新配置
    update_data = config_data.dict(exclude_unset=True)
    if "config_value" in update_data:
        config.config_value = json.dumps(update_data["config_value"], ensure_ascii=False)
    if "description" in update_data:
        config.description = update_data["description"]

    await db.commit()
    await db.refresh(config)

    # 记录操作日志
    await log_admin_action(
        admin_phone=admin_user.phone,
        action_type="update_config",
        action_description=f"更新系统配置: {config.config_key}",
        target_type="config",
        target_id=config.id,
        old_data=old_data,
        new_data=update_data,
        request=request,
        db=db
    )

    # 返回格式化的配置
    try:
        config_value = json.loads(config.config_value) if isinstance(config.config_value, str) else config.config_value
    except (json.JSONDecodeError, TypeError):
        config_value = config.config_value

    return {
        "id": config.id,
        "config_key": config.config_key,
        "config_value": config_value,
        "description": config.description,
        "is_active": True,
        "created_at": config.created_at,
        "updated_at": config.updated_at
    }


# ==================== 用户管理 ====================

@router.get("/users", response_model=List[UserManageResponse], summary="获取用户列表")
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（手机号或昵称）"),
    grade: Optional[str] = Query(None, description="年级筛选"),
    level: Optional[str] = Query(None, description="等级筛选"),
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（分页）"""
    query = select(User).where(User.is_active == True)
    
    # 搜索条件
    if keyword:
        query = query.where(
            or_(
                User.phone.contains(keyword),
                User.nickname.contains(keyword)
            )
        )
    
    if grade:
        query = query.where(User.child_grade == grade)
    
    if level:
        query = query.where(User.level == level)
    
    # 分页
    offset = (page - 1) * size
    query = query.order_by(desc(User.created_at)).offset(offset).limit(size)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users


@router.put("/users/{user_id}", response_model=UserManageResponse, summary="更新用户信息")
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    request: Request,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 保存旧数据
    old_data = {
        "points": user.points,
        "level": user.level,
        "is_active": user.is_active
    }
    
    # 更新用户信息
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    # 记录操作日志
    await log_admin_action(
        admin_phone=admin_user.phone,
        action_type="update_user",
        action_description=f"更新用户信息: {user.nickname}({user.phone})",
        target_type="user",
        target_id=user.id,
        old_data=old_data,
        new_data=update_data,
        request=request,
        db=db
    )
    
    return user


# ==================== 资源管理 ====================

@router.get("/resources", response_model=List[ResourceManageResponse], summary="获取资源列表")
async def get_resources(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    grade: Optional[str] = Query(None, description="年级筛选"),
    subject: Optional[str] = Query(None, description="科目筛选"),
    status: Optional[bool] = Query(None, description="状态筛选"),
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取资源列表（分页）"""
    query = select(Resource)
    
    # 搜索条件
    if keyword:
        query = query.where(
            or_(
                Resource.title.contains(keyword),
                Resource.description.contains(keyword)
            )
        )
    
    if grade:
        query = query.where(Resource.grade.contains(grade))
    
    if subject:
        query = query.where(Resource.subject == subject)
    
    if status is not None:
        query = query.where(Resource.is_active == status)
    
    # 分页
    offset = (page - 1) * size
    query = query.order_by(desc(Resource.created_at)).offset(offset).limit(size)
    
    result = await db.execute(query)
    resources = result.scalars().all()
    
    return resources


@router.put("/resources/{resource_id}", response_model=ResourceManageResponse, summary="更新资源信息")
async def update_resource(
    resource_id: int,
    resource_data: ResourceUpdateRequest,
    request: Request,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """更新资源信息"""
    result = await db.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    # 保存旧数据
    old_data = {
        "title": resource.title,
        "description": resource.description,
        "grade": resource.grade,
        "subject": resource.subject,
        "is_active": resource.is_active
    }
    
    # 更新资源信息
    update_data = resource_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
    
    await db.commit()
    await db.refresh(resource)
    
    # 记录操作日志
    await log_admin_action(
        admin_phone=admin_user.phone,
        action_type="update_resource",
        action_description=f"更新资源信息: {resource.title}",
        target_type="resource",
        target_id=resource.id,
        old_data=old_data,
        new_data=update_data,
        request=request,
        db=db
    )
    
    return resource


@router.delete("/resources/{resource_id}", summary="删除资源")
async def delete_resource(
    resource_id: int,
    request: Request,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """删除资源（软删除）"""
    result = await db.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在"
        )
    
    # 软删除
    resource.is_active = False
    await db.commit()
    
    # 记录操作日志
    await log_admin_action(
        admin_phone=admin_user.phone,
        action_type="delete_resource",
        action_description=f"删除资源: {resource.title}",
        target_type="resource",
        target_id=resource.id,
        old_data={"is_active": True},
        new_data={"is_active": False},
        request=request,
        db=db
    )
    
    return {"message": "资源删除成功"}


# ==================== 操作日志 ====================

@router.get("/logs", response_model=List[AdminLogResponse], summary="获取操作日志")
async def get_admin_logs(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    action_type: Optional[str] = Query(None, description="操作类型筛选"),
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """获取管理员操作日志"""
    query = select(AdminLog)
    
    if action_type:
        query = query.where(AdminLog.action_type == action_type)
    
    # 分页
    offset = (page - 1) * size
    query = query.order_by(desc(AdminLog.created_at)).offset(offset).limit(size)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return logs
