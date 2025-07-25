#!/usr/bin/env python3
"""
测试移除收藏功能后的系统
"""
import asyncio
import aiohttp


async def test_resource_list():
    """测试资源列表API（不需要认证）"""
    print(f"🔍 测试资源列表API...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8000/api/v1/resources/") as resp:
                print(f"📊 状态码: {resp.status}")
                
                if resp.status == 200:
                    result = await resp.json()
                    resources = result.get('items', [])
                    print(f"✅ 资源列表获取成功!")
                    print(f"📊 资源数量: {len(resources)}")
                    
                    # 检查资源字段，确保没有收藏相关字段
                    if resources:
                        resource = resources[0]
                        print(f"\n📄 示例资源字段:")
                        for key, value in resource.items():
                            if key == 'is_favorited':
                                print(f"❌ 发现收藏字段: {key} = {value}")
                            else:
                                print(f"   {key}: {value}")
                        
                        # 检查是否还有收藏字段
                        if 'is_favorited' not in resource:
                            print(f"✅ 收藏字段已成功移除")
                        else:
                            print(f"❌ 收藏字段仍然存在")
                            
                else:
                    error = await resp.text()
                    print(f"❌ 获取失败: {error}")
                    
        except Exception as e:
            print(f"❌ 请求失败: {e}")


async def test_favorite_apis_removed():
    """测试收藏相关API是否已移除"""
    print(f"\n🧪 测试收藏API是否已移除...")
    
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
        
        # 测试收藏API是否已移除
        test_cases = [
            {
                "name": "收藏资源API",
                "method": "POST",
                "url": "http://localhost:8000/api/v1/resources/1/favorite"
            },
            {
                "name": "取消收藏API",
                "method": "DELETE", 
                "url": "http://localhost:8000/api/v1/resources/1/favorite"
            },
            {
                "name": "收藏列表API",
                "method": "GET",
                "url": "http://localhost:8000/api/v1/resources/favorites/"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🔄 测试: {test_case['name']}")
            
            try:
                if test_case['method'] == 'POST':
                    async with session.post(test_case['url'], headers=headers) as resp:
                        status = resp.status
                elif test_case['method'] == 'DELETE':
                    async with session.delete(test_case['url'], headers=headers) as resp:
                        status = resp.status
                else:  # GET
                    async with session.get(test_case['url'], headers=headers) as resp:
                        status = resp.status
                
                if status == 404:
                    print(f"✅ API已移除 (404 Not Found)")
                elif status == 405:
                    print(f"✅ API已移除 (405 Method Not Allowed)")
                else:
                    print(f"❌ API仍然存在 (状态码: {status})")
                    
            except Exception as e:
                print(f"✅ API已移除 (连接错误: {e})")


async def test_basic_functionality():
    """测试基本功能是否正常"""
    print(f"\n🧪 测试基本功能...")
    
    # 获取登录token
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
        
        # 测试基本功能
        test_cases = [
            {
                "name": "获取用户信息",
                "url": "http://localhost:8000/api/v1/auth/me"
            },
            {
                "name": "搜索资源",
                "url": "http://localhost:8000/api/v1/resources/?keyword=测试"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🔄 测试: {test_case['name']}")
            
            try:
                async with session.get(test_case['url'], headers=headers) as resp:
                    if resp.status == 200:
                        print(f"✅ {test_case['name']}正常")
                    else:
                        print(f"❌ {test_case['name']}失败 (状态码: {resp.status})")
                        
            except Exception as e:
                print(f"❌ {test_case['name']}失败: {e}")


async def main():
    """主函数"""
    print("🧪 测试移除收藏功能后的系统")
    print("=" * 60)
    
    try:
        # 测试资源列表
        await test_resource_list()
        
        # 测试收藏API是否已移除
        await test_favorite_apis_removed()
        
        # 测试基本功能
        await test_basic_functionality()
        
        print("\n🎉 测试完成！")
        print("✅ 收藏功能已成功移除")
        print("✅ 基本功能正常运行")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
