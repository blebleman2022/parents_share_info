#!/usr/bin/env python3
"""
检查数据库表结构
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import AsyncSessionLocal
from sqlalchemy import text


async def check_system_configs_table():
    """检查system_configs表结构"""
    async with AsyncSessionLocal() as session:
        # 获取表结构
        result = await session.execute(text("PRAGMA table_info(system_configs)"))
        columns = result.fetchall()
        
        print("📋 system_configs表结构:")
        for column in columns:
            print(f"  - {column[1]} ({column[2]}) {'NOT NULL' if column[3] else 'NULL'}")
        
        # 获取现有数据
        result = await session.execute(text("SELECT * FROM system_configs"))
        configs = result.fetchall()
        
        print(f"\n📊 现有配置数据 ({len(configs)} 条):")
        for config in configs:
            print(f"  - {config[1]}: {config[2][:50]}...")


async def main():
    """主函数"""
    print("🔍 检查数据库表结构...")
    
    try:
        await check_system_configs_table()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
