#!/usr/bin/env python3
"""
检查管理员账号密码
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import AsyncSessionLocal
from app.models import User
from app.core.security import verify_password, get_password_hash
from sqlalchemy import select


async def check_admin_password():
    """检查管理员账号密码"""
    async with AsyncSessionLocal() as session:
        # 获取管理员账号
        result = await session.execute(
            select(User).where(User.phone == "13901119451")
        )
        admin_user = result.scalar_one_or_none()
        
        if admin_user:
            print(f"✅ 找到管理员账号: {admin_user.nickname} ({admin_user.phone})")
            print(f"   密码哈希: {admin_user.password_hash[:50]}...")
            
            # 测试不同的密码
            test_passwords = ["admin123", "123456", "password", "admin"]
            
            for password in test_passwords:
                if verify_password(password, admin_user.password_hash):
                    print(f"✅ 正确密码: {password}")
                    return password
                else:
                    print(f"❌ 错误密码: {password}")
            
            # 如果没有找到正确密码，重置为admin123
            print("\n🔧 重置管理员密码为 'admin123'...")
            admin_user.password_hash = get_password_hash("admin123")
            await session.commit()
            print("✅ 密码重置成功")
            return "admin123"
            
        else:
            print("❌ 未找到管理员账号")
            return None


async def main():
    """主函数"""
    print("🔍 检查管理员账号密码...")
    
    try:
        password = await check_admin_password()
        if password:
            print(f"\n📋 管理员登录信息:")
            print(f"   手机号: 13901119451")
            print(f"   密码: {password}")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
