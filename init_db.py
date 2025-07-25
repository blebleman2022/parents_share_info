#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import engine, Base
from app.models.user import User
from app.models.resource import Resource, Download, PointTransaction, Favorite
from app.models.bounty import Bounty, BountyResponse
from app.models.report import Report, UserAction, SystemConfig
from app.core.config import settings


async def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    try:
        # 创建所有表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)  # 删除所有表（开发环境）
            await conn.run_sync(Base.metadata.create_all)  # 创建所有表
        
        print("✅ 数据库表创建成功")
        
        # 插入系统配置
        await insert_system_configs()
        
        print("✅ 数据库初始化完成")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise


async def insert_system_configs():
    """插入系统配置"""
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        configs = [
            SystemConfig(
                config_key="max_file_size",
                config_value=str(settings.MAX_FILE_SIZE),
                description="最大文件大小（字节）"
            ),
            SystemConfig(
                config_key="allowed_file_types",
                config_value=",".join(settings.ALLOWED_FILE_TYPES),
                description="允许的文件类型"
            ),
            SystemConfig(
                config_key="point_rules",
                config_value=str(settings.POINTS_CONFIG),
                description="积分规则配置"
            ),
            SystemConfig(
                config_key="user_levels",
                config_value=str(settings.USER_LEVELS),
                description="用户等级配置"
            )
        ]
        
        for config in configs:
            session.add(config)
        
        await session.commit()
        print("✅ 系统配置插入成功")


async def create_test_data():
    """创建测试数据（可选）"""
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import AsyncSessionLocal
    from app.core.security import get_password_hash
    
    async with AsyncSessionLocal() as session:
        # 创建测试用户
        test_user = User(
            phone="13800138000",
            password_hash=get_password_hash("123456"),
            nickname="测试用户",
            child_grade="小学3年级",
            city="北京",
            points=1000
        )
        
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)
        
        print(f"✅ 创建测试用户: {test_user.nickname} (手机号: {test_user.phone}, 密码: 123456)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库初始化脚本")
    parser.add_argument("--with-test-data", action="store_true", help="创建测试数据")
    args = parser.parse_args()
    
    async def main():
        await init_database()
        
        if args.with_test_data:
            await create_test_data()
        
        print("🎉 数据库初始化完成！")
        print("💡 提示：")
        print("   - 使用 python start.py 启动应用")
        print("   - 访问 http://localhost:8000/static/index.html 使用前端界面")
        print("   - 访问 http://localhost:8000/docs 查看API文档")
        
        if args.with_test_data:
            print("   - 测试账号：13800138000 / 123456")
    
    asyncio.run(main())
