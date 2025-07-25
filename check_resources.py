#!/usr/bin/env python3
"""
检查资源显示问题
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import AsyncSessionLocal
from app.models import Resource, User
from sqlalchemy import select


async def check_resources_and_users():
    """检查资源和用户数据"""
    async with AsyncSessionLocal() as session:
        print("🔍 检查数据库中的资源和用户数据...")
        
        # 查看所有资源
        result = await session.execute(select(Resource))
        resources = result.scalars().all()
        
        print(f"\n📊 数据库中的资源总数: {len(resources)}")
        
        if resources:
            for resource in resources:
                print(f"\n📄 资源详情:")
                print(f"   ID: {resource.id}")
                print(f"   标题: {resource.title}")
                print(f"   描述: {resource.description}")
                print(f"   上传者ID: {resource.uploader_id}")
                print(f"   年级: {resource.grade}")
                print(f"   科目: {resource.subject}")
                print(f"   资源类型: {resource.resource_type}")
                print(f"   文件名: {resource.file_name}")
                print(f"   文件路径: {resource.file_path}")
                print(f"   文件大小: {resource.file_size}")
                print(f"   下载次数: {resource.download_count}")
                print(f"   是否激活: {resource.is_active}")
                print(f"   创建时间: {resource.created_at}")
                print(f"   更新时间: {resource.updated_at}")
        else:
            print("❌ 没有找到任何资源")
        
        # 查看所有用户
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print(f"\n👥 数据库中的用户总数: {len(users)}")
        
        if users:
            for user in users:
                print(f"\n👤 用户详情:")
                print(f"   ID: {user.id}")
                print(f"   手机号: {user.phone}")
                print(f"   昵称: {user.nickname}")
                print(f"   积分: {user.points}")
                print(f"   等级: {user.level}")
                print(f"   是否激活: {user.is_active}")
                print(f"   创建时间: {user.created_at}")
        else:
            print("❌ 没有找到任何用户")
        
        # 检查资源与用户的关联
        if resources and users:
            print(f"\n🔗 检查资源与用户的关联:")
            for resource in resources:
                uploader = None
                for user in users:
                    if user.id == resource.uploader_id:
                        uploader = user
                        break
                
                if uploader:
                    print(f"   资源 '{resource.title}' 的上传者: {uploader.nickname} ({uploader.phone})")
                else:
                    print(f"   ⚠️ 资源 '{resource.title}' 的上传者ID {resource.uploader_id} 未找到对应用户")


async def test_api_access():
    """测试API访问"""
    import aiohttp
    
    print(f"\n🌐 测试API访问...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # 测试获取资源列表
            async with session.get("http://localhost:8000/api/v1/resources/") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    resources = result.get('items', [])
                    print(f"✅ API返回资源数量: {len(resources)}")
                    
                    for resource in resources:
                        print(f"   📄 {resource['title']} - 激活状态: {resource.get('is_active', 'unknown')}")
                else:
                    print(f"❌ API请求失败: {resp.status}")
                    error_text = await resp.text()
                    print(f"   错误信息: {error_text}")
    
    except Exception as e:
        print(f"❌ API测试失败: {e}")


async def main():
    """主函数"""
    print("🔍 检查资源显示问题")
    print("=" * 50)
    
    try:
        # 检查数据库数据
        await check_resources_and_users()
        
        # 测试API访问
        await test_api_access()
        
        print(f"\n📋 可能的问题原因:")
        print(f"1. 资源的 is_active 字段为 False")
        print(f"2. 前端筛选条件过滤了资源")
        print(f"3. 用户权限问题")
        print(f"4. API返回数据格式问题")
        print(f"5. 前端JavaScript错误")
        
        print(f"\n🔧 建议检查:")
        print(f"1. 打开浏览器开发者工具查看网络请求")
        print(f"2. 检查控制台是否有JavaScript错误")
        print(f"3. 确认登录用户是否正确")
        print(f"4. 检查搜索筛选条件是否为空")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
