"""
认证相关API
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_user
)
from app.schemas.auth import UserRegister, UserLogin, Token
from app.schemas.user import UserResponse
from app.crud.user import get_user_by_phone, create_user
from app.services.point_service import add_points
from app.services.sms_service import sms_service
from app.services.grade_service import grade_service


router = APIRouter()


@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 检查手机号是否已存在
    existing_user = await get_user_by_phone(db, phone=user_data.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已被注册"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    user = await create_user(
        db=db,
        phone=user_data.phone,
        password_hash=hashed_password,
        nickname=user_data.nickname,
        child_grade=user_data.child_grade
    )
    
    # 添加注册奖励积分
    await add_points(
        db=db,
        user_id=user.id,
        points=settings.POINTS_CONFIG["register"],
        transaction_type="register",
        description="新用户注册奖励"
    )
    
    return user


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    user = await get_user_by_phone(db, phone=user_data.phone)
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )

    # 检查并升级用户年级
    upgraded_grade = await grade_service.check_and_upgrade_user_grade(db, user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

    # 如果年级升级了，添加提示信息
    if upgraded_grade:
        response_data["grade_upgraded"] = True
        response_data["new_grade"] = upgraded_grade
        response_data["message"] = f"您孩子的年级已自动升级为：{upgraded_grade}"
    
    return response_data


@router.post("/token", response_model=Token, summary="OAuth2兼容登录")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """OAuth2兼容的登录接口"""
    user = await get_user_by_phone(db, phone=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/send-code", summary="发送验证码")
async def send_verification_code(
    phone: str,
    code_type: str = "register",
    db: AsyncSession = Depends(get_db)
):
    """
    发送手机验证码

    Args:
        phone: 手机号
        code_type: 验证码类型（register, login, reset_password）
    """
    # 验证手机号格式
    import re
    if not re.match(r'^1[3-9]\d{9}$', phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )

    # 如果是注册验证码，检查手机号是否已存在
    if code_type == "register":
        from app.crud.user import get_user_by_phone
        existing_user = await get_user_by_phone(db, phone=phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )

    # 发送验证码
    result = await sms_service.send_verification_code(phone, code_type)

    if result["success"]:
        return {
            "message": result["message"],
            "expires_in": result.get("expires_in", 300)
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(current_user = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user
