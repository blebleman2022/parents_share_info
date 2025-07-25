"""
认证相关数据传输对象
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
import re


class UserRegister(BaseModel):
    """用户注册请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    confirm_password: str = Field(..., min_length=6, max_length=20, description="确认密码")
    nickname: str = Field(..., min_length=2, max_length=20, description="昵称")
    child_grade: str = Field(..., description="孩子年级")

    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    @validator('child_grade')
    def validate_grade(cls, v):
        valid_grades = [
            "小学1年级", "小学2年级", "小学3年级", "小学4年级", "小学5年级", "预初",
            "初中1年级", "初中2年级", "初中3年级",
            "高中1年级", "高中2年级", "高中3年级"
        ]
        if v not in valid_grades:
            raise ValueError('年级选择不正确')
        return v

    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v


class UserLogin(BaseModel):
    """用户登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")
    
    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class Token(BaseModel):
    """访问令牌响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
