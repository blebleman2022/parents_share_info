"""
短信验证码服务
注意：这是一个基础框架，需要接入实际的短信服务商才能使用
"""
import random
import asyncio
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings


class SMSService:
    """短信服务类"""
    
    def __init__(self):
        # 在内存中存储验证码（生产环境应使用Redis）
        self._verification_codes = {}
    
    def generate_code(self, length: int = 6) -> str:
        """生成验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])
    
    async def send_verification_code(self, phone: str, code_type: str = "register") -> dict:
        """
        发送验证码
        
        Args:
            phone: 手机号
            code_type: 验证码类型（register, login, reset_password）
        
        Returns:
            dict: 发送结果
        """
        # 检查发送频率限制（60秒内只能发送一次）
        key = f"{phone}_{code_type}"
        now = datetime.now()
        
        if key in self._verification_codes:
            last_send_time = self._verification_codes[key]['send_time']
            if now - last_send_time < timedelta(seconds=60):
                remaining_time = 60 - (now - last_send_time).seconds
                return {
                    "success": False,
                    "message": f"请等待{remaining_time}秒后再试"
                }
        
        # 生成验证码
        code = self.generate_code()
        
        # 存储验证码（5分钟有效期）
        self._verification_codes[key] = {
            "code": code,
            "send_time": now,
            "expires_at": now + timedelta(minutes=5),
            "attempts": 0
        }
        
        # 这里应该调用实际的短信服务商API
        success = await self._send_sms(phone, code, code_type)
        
        if success:
            return {
                "success": True,
                "message": "验证码发送成功",
                "expires_in": 300  # 5分钟
            }
        else:
            return {
                "success": False,
                "message": "验证码发送失败，请稍后重试"
            }
    
    async def verify_code(self, phone: str, code: str, code_type: str = "register") -> dict:
        """
        验证验证码
        
        Args:
            phone: 手机号
            code: 验证码
            code_type: 验证码类型
        
        Returns:
            dict: 验证结果
        """
        key = f"{phone}_{code_type}"
        
        if key not in self._verification_codes:
            return {
                "success": False,
                "message": "验证码不存在或已过期"
            }
        
        stored_data = self._verification_codes[key]
        
        # 检查是否过期
        if datetime.now() > stored_data['expires_at']:
            del self._verification_codes[key]
            return {
                "success": False,
                "message": "验证码已过期"
            }
        
        # 检查尝试次数（最多3次）
        if stored_data['attempts'] >= 3:
            del self._verification_codes[key]
            return {
                "success": False,
                "message": "验证码错误次数过多，请重新获取"
            }
        
        # 验证码码
        if stored_data['code'] != code:
            stored_data['attempts'] += 1
            return {
                "success": False,
                "message": f"验证码错误，还可尝试{3 - stored_data['attempts']}次"
            }
        
        # 验证成功，删除验证码
        del self._verification_codes[key]
        return {
            "success": True,
            "message": "验证码验证成功"
        }
    
    async def _send_sms(self, phone: str, code: str, code_type: str) -> bool:
        """
        发送短信的具体实现
        这里需要接入实际的短信服务商API
        
        常用的短信服务商：
        - 阿里云短信服务
        - 腾讯云短信
        - 华为云短信
        - 网易云信
        """
        
        # 模拟发送过程
        print(f"[模拟短信] 发送给 {phone}: 您的验证码是 {code}，5分钟内有效。")
        
        # 在开发环境下，我们直接返回成功
        if settings.DEBUG:
            return True
        
        # 生产环境下，这里应该调用实际的短信API
        # 示例（阿里云短信）：
        # try:
        #     from alibabacloud_dysmsapi20170525.client import Client
        #     from alibabacloud_dysmsapi20170525 import models
        #     
        #     request = models.SendSmsRequest(
        #         phone_numbers=phone,
        #         sign_name="您的签名",
        #         template_code="SMS_XXXXXX",
        #         template_param=f'{{"code":"{code}"}}'
        #     )
        #     
        #     response = client.send_sms(request)
        #     return response.body.code == "OK"
        # except Exception as e:
        #     print(f"短信发送失败: {e}")
        #     return False
        
        return False


# 创建全局SMS服务实例
sms_service = SMSService()
