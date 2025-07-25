#!/usr/bin/env python3
"""
清理重复的配置项，只保留管理员版本
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


async def cleanup_duplicate_configs():
    """清理重复的配置项"""
    async with AsyncSessionLocal() as session:
        print("🔄 清理重复的配置项...")
        
        # 要删除的原始配置项（保留管理员版本）
        configs_to_delete = [
            'point_rules',      # 保留 point_rules_admin
            'user_levels',      # 保留 user_levels_admin
        ]
        
        deleted_count = 0
        for config_key in configs_to_delete:
            # 查找配置项
            result = await session.execute(
                select(SystemConfig).where(SystemConfig.config_key == config_key)
            )
            config = result.scalar_one_or_none()
            
            if config:
                print(f"🗑️  删除重复配置: {config_key} - {config.description}")
                await session.delete(config)
                deleted_count += 1
            else:
                print(f"ℹ️  配置项不存在: {config_key}")
        
        # 提交删除操作
        await session.commit()
        
        print(f"\n✅ 清理完成，共删除了 {deleted_count} 个重复配置项")
        
        # 显示最终的配置项
        print("\n📋 最终的配置项:")
        result = await session.execute(select(SystemConfig))
        final_configs = result.scalars().all()
        
        for config in final_configs:
            print(f"   - {config.config_key}: {config.description}")
        
        print(f"\n📊 总计 {len(final_configs)} 个配置项")
        
        # 验证配置完整性
        expected_configs = [
            'point_rules_admin',
            'user_levels_admin',
            'system_settings_admin'
        ]
        
        existing_keys = [config.config_key for config in final_configs]
        missing_configs = [key for key in expected_configs if key not in existing_keys]
        
        if missing_configs:
            print(f"\n⚠️  缺少的配置项: {', '.join(missing_configs)}")
        else:
            print(f"\n✅ 所有必需的配置项都存在")


async def main():
    """主函数"""
    print("🔧 清理重复配置项")
    print("=" * 40)
    
    try:
        await cleanup_duplicate_configs()
        
        print("\n🎉 配置清理完成！")
        print("\n📝 最终配置结构:")
        print("   📊 point_rules_admin - 积分规则配置")
        print("   👥 user_levels_admin - 用户等级配置")
        print("   ⚙️ system_settings_admin - 系统基础设置")
        
        print("\n✨ 优化效果:")
        print("   - 删除了重复的配置项")
        print("   - 统一使用管理员版本配置")
        print("   - 配置结构更加清晰")
        print("   - 避免了配置冲突")
        
        print("\n🌐 访问管理员后台:")
        print("   地址: http://localhost:8000/static/admin.html")
        print("   账号: 13901119451")
        print("   密码: admin123")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
