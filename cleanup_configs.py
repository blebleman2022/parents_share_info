#!/usr/bin/env python3
"""
清理冗余的系统配置项
删除那些应该整合到主要配置中的独立配置项
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import AsyncSessionLocal
from app.models import SystemConfig
from sqlalchemy import select, delete


async def cleanup_redundant_configs():
    """清理冗余的配置项"""
    async with AsyncSessionLocal() as session:
        # 要删除的配置键列表
        configs_to_delete = [
            'allowed_file_types',  # 应该在system_settings中
            'demo_config',         # 演示配置，可以删除
            'max_file_size',       # 应该在system_settings中
            'ui_test_config'       # 测试配置，可以删除
        ]
        
        print("🧹 开始清理冗余的系统配置项...")
        
        deleted_count = 0
        for config_key in configs_to_delete:
            # 查找配置项
            result = await session.execute(
                select(SystemConfig).where(SystemConfig.config_key == config_key)
            )
            config = result.scalar_one_or_none()
            
            if config:
                print(f"🗑️  删除配置项: {config_key} - {config.description}")
                await session.delete(config)
                deleted_count += 1
            else:
                print(f"ℹ️  配置项不存在: {config_key}")
        
        # 提交删除操作
        await session.commit()
        
        print(f"\n✅ 清理完成，共删除了 {deleted_count} 个冗余配置项")
        
        # 显示剩余的配置项
        print("\n📋 剩余的配置项:")
        result = await session.execute(select(SystemConfig))
        remaining_configs = result.scalars().all()
        
        for config in remaining_configs:
            print(f"   - {config.config_key}: {config.description}")
        
        print(f"\n📊 总计剩余 {len(remaining_configs)} 个配置项")


async def verify_main_configs():
    """验证主要配置项是否存在"""
    async with AsyncSessionLocal() as session:
        print("\n🔍 验证主要配置项...")
        
        main_configs = [
            'point_rules_admin',
            'user_levels_admin', 
            'system_settings_admin'
        ]
        
        for config_key in main_configs:
            result = await session.execute(
                select(SystemConfig).where(SystemConfig.config_key == config_key)
            )
            config = result.scalar_one_or_none()
            
            if config:
                print(f"✅ {config_key}: 存在")
            else:
                print(f"❌ {config_key}: 不存在")


async def main():
    """主函数"""
    print("🔧 系统配置清理工具")
    print("=" * 50)
    
    try:
        # 清理冗余配置
        await cleanup_redundant_configs()
        
        # 验证主要配置
        await verify_main_configs()
        
        print("\n🎉 配置清理完成！")
        print("\n📝 说明:")
        print("   - 删除了独立的文件类型、文件大小等配置")
        print("   - 这些设置现在统一在'系统设置'中管理")
        print("   - 删除了演示和测试用的配置项")
        print("   - 配置管理界面将更加简洁")
        
        print("\n🌐 访问管理员后台查看效果:")
        print("   地址: http://localhost:8000/static/admin.html")
        print("   账号: 13901119451")
        print("   密码: admin123")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
