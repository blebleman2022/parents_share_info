#!/usr/bin/env python3
"""
检查年级数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import AsyncSessionLocal
from app.models import Resource
from sqlalchemy import select


async def check_grade_data():
    """检查年级数据"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Resource))
        resources = result.scalars().all()
        
        print('📊 数据库中的年级数据:')
        for resource in resources:
            print(f'资源: {resource.title}')
            print(f'年级: "{resource.grade}"')
            print(f'包含逗号: {"," in resource.grade}')
            if ',' in resource.grade:
                grades = [g.strip() for g in resource.grade.split(',')]
                print(f'分解后: {grades}')
            print('---')


async def main():
    """主函数"""
    try:
        await check_grade_data()
    except Exception as e:
        print(f"❌ 检查失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
