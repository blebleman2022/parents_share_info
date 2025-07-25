#!/usr/bin/env python3
"""
测试空年级资源
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
import aiohttp


async def create_empty_grade_resource():
    """创建一个没有年级信息的测试资源"""
    async with AsyncSessionLocal() as session:
        # 创建测试资源
        resource = Resource(
            uploader_id=3,  # 使用现有用户ID
            title="测试空年级资源",
            description="这是一个没有年级信息的测试资源",
            file_name="test_empty_grade.txt",
            file_path="uploads/resources/test_empty_grade.txt",
            file_size=100,
            file_type="txt",
            grade="",  # 空年级
            subject="数学",
            resource_type="其他"
        )
        
        session.add(resource)
        await session.commit()
        await session.refresh(resource)
        
        print(f"✅ 创建了空年级资源: {resource.title} (ID: {resource.id})")
        return resource.id


async def test_empty_grade_search():
    """测试空年级资源的搜索"""
    base_url = "http://localhost:8000/api/v1/resources/"
    
    test_cases = [
        {
            "name": "搜索小学1年级（应该包含空年级资源）",
            "params": {"grade": "小学1年级"}
        },
        {
            "name": "搜索高中2年级（应该包含空年级资源）",
            "params": {"grade": "高中2年级"}
        },
        {
            "name": "不指定年级（应该包含所有资源）",
            "params": {}
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            print(f"\n🧪 测试: {test_case['name']}")
            
            try:
                async with session.get(base_url, params=test_case['params']) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        resources = result.get('items', [])
                        print(f"✅ 状态码: {resp.status}")
                        print(f"📊 结果数量: {len(resources)}")
                        
                        empty_grade_found = False
                        for resource in resources:
                            print(f"   📄 {resource['title']} (年级: '{resource['grade']}')")
                            if resource['title'] == "测试空年级资源":
                                empty_grade_found = True
                        
                        if test_case['params'].get('grade') and empty_grade_found:
                            print("   ✅ 空年级资源被正确包含在搜索结果中")
                        elif not test_case['params'].get('grade'):
                            print("   ✅ 无筛选条件，显示所有资源")
                            
                    else:
                        error = await resp.text()
                        print(f"❌ 状态码: {resp.status}")
                        print(f"❌ 错误: {error}")
                        
            except Exception as e:
                print(f"❌ 请求失败: {e}")


async def cleanup_test_resource(resource_id):
    """清理测试资源"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Resource).where(Resource.id == resource_id)
        )
        resource = result.scalar_one_or_none()
        
        if resource:
            await session.delete(resource)
            await session.commit()
            print(f"🗑️ 清理了测试资源: {resource.title}")


async def main():
    """主函数"""
    print("🧪 测试空年级资源搜索")
    print("=" * 40)
    
    resource_id = None
    try:
        # 创建测试资源
        resource_id = await create_empty_grade_resource()
        
        # 测试搜索
        await test_empty_grade_search()
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        # 清理测试资源
        if resource_id:
            await cleanup_test_resource(resource_id)


if __name__ == "__main__":
    asyncio.run(main())
