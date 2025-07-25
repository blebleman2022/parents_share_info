#!/usr/bin/env python3
"""
测试管理员功能的脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import AsyncSessionLocal
from app.models import User, SystemConfig, AdminLog
from app.core.security import get_password_hash
from sqlalchemy import select


async def init_admin_account():
    """初始化管理员账号"""
    async with AsyncSessionLocal() as session:
        # 检查管理员账号是否存在
        result = await session.execute(
            select(User).where(User.phone == "13901119451")
        )
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            # 创建管理员账号
            admin_user = User(
                phone="13901119451",
                password_hash=get_password_hash("admin123"),
                nickname="系统管理员",
                child_grade="小学1年级",
                points=10000,
                level="专家用户"
            )
            session.add(admin_user)
            await session.commit()
            print("✅ 管理员账号创建成功")
            print("   手机号: 13901119451")
            print("   密码: admin123")
        else:
            print("✅ 管理员账号已存在")
            print("   手机号: 13901119451")


async def init_system_configs():
    """初始化系统配置"""
    import json

    async with AsyncSessionLocal() as session:
        default_configs = [
            {
                "config_key": "point_rules_admin",
                "config_value": {
                    "register_points": 100,
                    "upload_points": 20,
                    "download_cost": 5,
                    "daily_signin_points": 10,
                    "daily_download_limit": 10
                },
                "description": "积分规则配置（管理员版）"
            },
            {
                "config_key": "user_levels_admin",
                "config_value": {
                    "新手用户": {"min_points": 0, "max_points": 499, "daily_downloads": 5},
                    "活跃用户": {"min_points": 500, "max_points": 1999, "daily_downloads": 10},
                    "资深用户": {"min_points": 2000, "max_points": 4999, "daily_downloads": 15},
                    "专家用户": {"min_points": 5000, "max_points": -1, "daily_downloads": 20}
                },
                "description": "用户等级配置（管理员版）"
            },
            {
                "config_key": "system_settings_admin",
                "config_value": {
                    "max_file_size": 52428800,  # 50MB
                    "allowed_file_types": ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "jpg", "png"],
                    "auto_approve_resources": True,
                    "maintenance_mode": False
                },
                "description": "系统基础设置（管理员版）"
            }
        ]

        created_count = 0
        for config_data in default_configs:
            # 检查配置是否已存在
            result = await session.execute(
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
                session.add(config)
                created_count += 1

        await session.commit()
        print(f"✅ 系统配置初始化完成，创建了 {created_count} 个配置项")


async def main():
    """主函数"""
    print("🔧 正在初始化管理员功能...")
    
    try:
        await init_admin_account()
        await init_system_configs()
        
        print("\n🎉 管理员功能初始化完成！")
        print("\n📋 使用说明:")
        print("1. 访问管理员后台: http://localhost:8000/static/admin.html")
        print("2. 使用管理员账号登录:")
        print("   - 手机号: 13901119451")
        print("   - 密码: admin123")
        print("3. 登录后可以管理系统配置、用户和资源")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
