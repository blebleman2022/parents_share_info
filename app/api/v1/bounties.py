"""
悬赏相关API
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.bounty import Bounty, BountyResponse
from app.models.resource import Resource
from app.schemas.bounty import BountyCreate, BountyResponse as BountyResponseSchema, BountyList
from app.services.point_service import deduct_points, transfer_points


router = APIRouter()


@router.get("/", response_model=BountyList, summary="获取悬赏列表")
async def get_bounties(
    status_filter: Optional[str] = Query(None, description="状态筛选：active, completed, expired"),
    grade: Optional[str] = Query(None, description="年级筛选"),
    subject: Optional[str] = Query(None, description="科目筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取悬赏列表"""
    # 构建查询条件
    conditions = []
    
    if status_filter:
        conditions.append(Bounty.status == status_filter)
    
    if grade:
        conditions.append(Bounty.grade == grade)
    
    if subject:
        conditions.append(Bounty.subject == subject)
    
    # 构建查询
    query = select(Bounty)
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Bounty.created_at.desc())
    
    # 分页
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    # 执行查询
    result = await db.execute(query)
    bounties = result.scalars().all()
    
    # 获取总数
    count_query = select(Bounty)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    return {
        "items": bounties,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.post("/", response_model=BountyResponseSchema, summary="创建悬赏")
async def create_bounty(
    bounty_data: BountyCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建悬赏"""
    # 检查积分是否足够
    if current_user.points < bounty_data.points_reward:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="积分不足"
        )
    
    # 检查最低悬赏积分
    if bounty_data.points_reward < settings.POINTS_CONFIG["min_bounty"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"悬赏积分不能少于{settings.POINTS_CONFIG['min_bounty']}积分"
        )
    
    try:
        # 扣除悬赏积分
        await deduct_points(
            db=db,
            user_id=current_user.id,
            points=bounty_data.points_reward,
            transaction_type="bounty_create",
            description=f"创建悬赏: {bounty_data.title}"
        )
        
        # 创建悬赏
        bounty = Bounty(
            creator_id=current_user.id,
            title=bounty_data.title,
            description=bounty_data.description,
            grade=bounty_data.grade,
            subject=bounty_data.subject,
            points_reward=bounty_data.points_reward,
            expires_at=datetime.utcnow() + timedelta(days=7)  # 7天后过期
        )
        
        db.add(bounty)
        await db.commit()
        await db.refresh(bounty)
        
        return bounty
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建悬赏失败"
        )


@router.get("/{bounty_id}", response_model=BountyResponseSchema, summary="获取悬赏详情")
async def get_bounty(
    bounty_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取悬赏详情"""
    result = await db.execute(select(Bounty).where(Bounty.id == bounty_id))
    bounty = result.scalar_one_or_none()
    
    if not bounty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="悬赏不存在"
        )
    
    return bounty


@router.post("/{bounty_id}/respond", summary="响应悬赏")
async def respond_to_bounty(
    bounty_id: int,
    resource_id: int,
    message: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """响应悬赏"""
    # 检查悬赏是否存在且有效
    bounty_result = await db.execute(select(Bounty).where(Bounty.id == bounty_id))
    bounty = bounty_result.scalar_one_or_none()
    
    if not bounty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="悬赏不存在"
        )
    
    if bounty.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="悬赏已结束"
        )
    
    if bounty.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="悬赏已过期"
        )
    
    if bounty.creator_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能响应自己的悬赏"
        )
    
    # 检查资源是否存在且属于当前用户
    resource_result = await db.execute(
        select(Resource).where(
            Resource.id == resource_id,
            Resource.uploader_id == current_user.id,
            Resource.is_active == True
        )
    )
    resource = resource_result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="资源不存在或不属于您"
        )
    
    # 检查是否已经响应过
    existing_response = await db.execute(
        select(BountyResponse).where(
            BountyResponse.bounty_id == bounty_id,
            BountyResponse.responder_id == current_user.id
        )
    )
    
    if existing_response.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已经响应过该悬赏"
        )
    
    # 创建响应记录
    response = BountyResponse(
        bounty_id=bounty_id,
        responder_id=current_user.id,
        resource_id=resource_id,
        message=message
    )
    
    db.add(response)
    await db.commit()
    
    return {"message": "响应成功，等待悬赏发布者确认"}


@router.post("/{bounty_id}/select/{response_id}", summary="选择悬赏响应")
async def select_bounty_response(
    bounty_id: int,
    response_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """选择悬赏响应（悬赏发布者操作）"""
    # 检查悬赏是否存在且属于当前用户
    bounty_result = await db.execute(
        select(Bounty).where(
            Bounty.id == bounty_id,
            Bounty.creator_id == current_user.id
        )
    )
    bounty = bounty_result.scalar_one_or_none()
    
    if not bounty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="悬赏不存在或不属于您"
        )
    
    if bounty.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="悬赏已结束"
        )
    
    # 检查响应是否存在
    response_result = await db.execute(
        select(BountyResponse).where(
            BountyResponse.id == response_id,
            BountyResponse.bounty_id == bounty_id
        )
    )
    response = response_result.scalar_one_or_none()
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="响应不存在"
        )
    
    try:
        # 标记响应为选中
        response.is_selected = True
        
        # 更新悬赏状态
        bounty.status = "completed"
        bounty.winner_id = response.responder_id
        bounty.winning_resource_id = response.resource_id
        
        # 将积分转移给响应者（积分已在创建悬赏时扣除，这里是从系统转移给响应者）
        await transfer_points(
            db=db,
            from_user_id=current_user.id,  # 实际上积分已经扣除，这里只是记录
            to_user_id=response.responder_id,
            points=bounty.points_reward,
            transaction_type="bounty_reward",
            description=f"悬赏奖励: {bounty.title}",
            related_bounty_id=bounty_id
        )
        
        await db.commit()
        
        return {"message": "悬赏完成，积分已转移给响应者"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="操作失败"
        )


@router.get("/{bounty_id}/responses", summary="获取悬赏响应列表")
async def get_bounty_responses(
    bounty_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取悬赏响应列表（仅悬赏发布者可查看）"""
    # 检查悬赏是否存在且属于当前用户
    bounty_result = await db.execute(
        select(Bounty).where(
            Bounty.id == bounty_id,
            Bounty.creator_id == current_user.id
        )
    )
    bounty = bounty_result.scalar_one_or_none()
    
    if not bounty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="悬赏不存在或无权限查看"
        )
    
    # 获取响应列表
    responses_result = await db.execute(
        select(BountyResponse, Resource)
        .join(Resource, BountyResponse.resource_id == Resource.id)
        .where(BountyResponse.bounty_id == bounty_id)
        .order_by(BountyResponse.created_at.desc())
    )
    
    responses = []
    for response, resource in responses_result.all():
        responses.append({
            "id": response.id,
            "responder_id": response.responder_id,
            "resource": {
                "id": resource.id,
                "title": resource.title,
                "description": resource.description,
                "file_type": resource.file_type,
                "file_size": resource.file_size
            },
            "message": response.message,
            "is_selected": response.is_selected,
            "created_at": response.created_at
        })
    
    return {
        "bounty_id": bounty_id,
        "responses": responses,
        "total": len(responses)
    }
