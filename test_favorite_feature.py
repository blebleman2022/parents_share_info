#!/usr/bin/env python3
"""
测试收藏功能
"""
import asyncio
import aiohttp


async def test_favorite_operations():
    """测试收藏和取消收藏操作"""
    
    # 获取登录token
    login_data = {
        "phone": "13800138000",
        "password": "123456"
    }
    
    async with aiohttp.ClientSession() as session:
        # 登录获取token
        async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as resp:
            if resp.status == 200:
                login_result = await resp.json()
                token = login_result.get("access_token")
                print(f"✅ 登录成功")
            else:
                print(f"❌ 登录失败: {resp.status}")
                return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. 获取资源列表，查看收藏状态
        print(f"\n🔍 获取资源列表...")
        async with session.get("http://localhost:8000/api/v1/resources/", headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                resources = result.get('items', [])
                print(f"✅ 获取成功! 总共 {len(resources)} 个资源")
                
                # 显示前3个资源的收藏状态
                for i, resource in enumerate(resources[:3]):
                    status = "已收藏" if resource.get('is_favorited') else "未收藏"
                    print(f"   📄 {resource['title']} - {status}")
                
                if resources:
                    test_resource = resources[0]
                    resource_id = test_resource['id']
                    is_favorited = test_resource.get('is_favorited', False)
                    
                    print(f"\n🧪 测试资源: {test_resource['title']} (ID: {resource_id})")
                    print(f"   当前状态: {'已收藏' if is_favorited else '未收藏'}")
                    
                    # 2. 测试收藏/取消收藏操作
                    if is_favorited:
                        # 测试取消收藏
                        print(f"\n🔄 测试取消收藏...")
                        async with session.delete(f"http://localhost:8000/api/v1/resources/{resource_id}/favorite", headers=headers) as resp:
                            if resp.status == 200:
                                result = await resp.json()
                                print(f"✅ 取消收藏成功: {result.get('message')}")
                            else:
                                error = await resp.text()
                                print(f"❌ 取消收藏失败: {error}")
                    else:
                        # 测试收藏
                        print(f"\n🔄 测试收藏...")
                        async with session.post(f"http://localhost:8000/api/v1/resources/{resource_id}/favorite", headers=headers) as resp:
                            if resp.status == 200:
                                result = await resp.json()
                                print(f"✅ 收藏成功: {result.get('message')}")
                            else:
                                error = await resp.text()
                                print(f"❌ 收藏失败: {error}")
                    
                    # 3. 再次获取资源列表，验证状态变化
                    print(f"\n🔍 验证状态变化...")
                    async with session.get("http://localhost:8000/api/v1/resources/", headers=headers) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            resources = result.get('items', [])
                            
                            # 找到测试资源
                            for resource in resources:
                                if resource['id'] == resource_id:
                                    new_status = "已收藏" if resource.get('is_favorited') else "未收藏"
                                    print(f"✅ 状态已更新: {resource['title']} - {new_status}")
                                    break
                        else:
                            print(f"❌ 获取资源列表失败")
                    
                    # 4. 测试收藏列表API
                    print(f"\n📋 测试收藏列表...")
                    async with session.get("http://localhost:8000/api/v1/resources/favorites/", headers=headers) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            favorites = result.get('items', [])
                            print(f"✅ 收藏列表获取成功! 共 {len(favorites)} 个收藏")
                            
                            for favorite in favorites:
                                print(f"   ⭐ {favorite['title']}")
                        else:
                            error = await resp.text()
                            print(f"❌ 获取收藏列表失败: {error}")
                            
            else:
                error = await resp.text()
                print(f"❌ 获取资源列表失败: {error}")


async def test_duplicate_operations():
    """测试重复操作的错误处理"""
    print(f"\n🧪 测试重复操作...")
    
    login_data = {
        "phone": "13800138000",
        "password": "123456"
    }
    
    async with aiohttp.ClientSession() as session:
        # 登录获取token
        async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as resp:
            login_result = await resp.json()
            token = login_result.get("access_token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取第一个资源
        async with session.get("http://localhost:8000/api/v1/resources/", headers=headers) as resp:
            result = await resp.json()
            resources = result.get('items', [])
            
            if resources:
                resource_id = resources[0]['id']
                
                # 测试重复收藏
                print(f"🔄 测试重复收藏...")
                for i in range(2):
                    async with session.post(f"http://localhost:8000/api/v1/resources/{resource_id}/favorite", headers=headers) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            print(f"✅ 第{i+1}次收藏: {result.get('message')}")
                        else:
                            error = await resp.json()
                            print(f"❌ 第{i+1}次收藏失败: {error.get('detail')}")
                
                # 测试重复取消收藏
                print(f"\n🔄 测试重复取消收藏...")
                for i in range(2):
                    async with session.delete(f"http://localhost:8000/api/v1/resources/{resource_id}/favorite", headers=headers) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            print(f"✅ 第{i+1}次取消收藏: {result.get('message')}")
                        else:
                            error = await resp.json()
                            print(f"❌ 第{i+1}次取消收藏失败: {error.get('detail')}")


async def main():
    """主函数"""
    print("🧪 测试收藏功能")
    print("=" * 60)
    
    try:
        # 测试基本收藏操作
        await test_favorite_operations()
        
        # 测试重复操作
        await test_duplicate_operations()
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
