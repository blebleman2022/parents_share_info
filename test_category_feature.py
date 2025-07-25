#!/usr/bin/env python3
"""
测试类别功能
"""
import asyncio
import aiohttp
import os


async def test_upload_with_categories():
    """测试不同类别的上传"""
    base_url = "http://localhost:8000/api/v1/resources/"
    
    # 创建测试文件
    test_file_path = "test_category.pdf"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("测试类别功能的文件内容")
    
    # 测试不同类别的上传
    categories = ['课件', '教案', '学案', '作业', '试卷', '题集', '素材', '备课包', '其他']
    
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
        
        # 测试每个类别的上传
        for i, category in enumerate(categories):
            print(f"\n🧪 测试上传类别: {category}")
            
            try:
                with open(test_file_path, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f, filename=f'test_{category}.pdf', content_type='application/pdf')
                    data.add_field('title', f'测试{category}资源')
                    data.add_field('description', f'这是一个{category}类型的测试资源')
                    data.add_field('grade', '小学1年级')
                    data.add_field('subject', '数学')
                    data.add_field('resource_type', category)
                    
                    async with session.post(base_url, data=data, headers=headers) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            print(f"✅ 上传成功! 资源ID: {result.get('id')}")
                            print(f"   类别: {result.get('resource_type')}")
                        else:
                            error = await resp.text()
                            print(f"❌ 上传失败: {error}")
                            
            except Exception as e:
                print(f"❌ 请求失败: {e}")
    
    # 清理测试文件
    if os.path.exists(test_file_path):
        os.remove(test_file_path)


async def test_search_by_category():
    """测试按类别搜索"""
    print(f"\n🔍 测试按类别搜索功能...")
    
    categories_to_test = ['课件', '教案', '试卷', '其他']
    
    async with aiohttp.ClientSession() as session:
        for category in categories_to_test:
            print(f"\n🔍 搜索类别: {category}")
            
            try:
                params = {"resource_type": category}
                async with session.get("http://localhost:8000/api/v1/resources/", params=params) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        resources = result.get('items', [])
                        print(f"✅ 搜索成功! 找到 {len(resources)} 个{category}资源")
                        
                        for resource in resources:
                            print(f"   📄 {resource['title']} (类别: {resource['resource_type']})")
                    else:
                        error = await resp.text()
                        print(f"❌ 搜索失败: {error}")
                        
            except Exception as e:
                print(f"❌ 请求失败: {e}")


async def test_all_resources():
    """测试获取所有资源"""
    print(f"\n📊 测试获取所有资源...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8000/api/v1/resources/") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    resources = result.get('items', [])
                    print(f"✅ 获取成功! 总共 {len(resources)} 个资源")
                    
                    # 按类别统计
                    category_count = {}
                    for resource in resources:
                        category = resource.get('resource_type', '未分类')
                        category_count[category] = category_count.get(category, 0) + 1
                    
                    print(f"\n📈 类别统计:")
                    for category, count in category_count.items():
                        print(f"   {category}: {count} 个")
                        
                else:
                    error = await resp.text()
                    print(f"❌ 获取失败: {error}")
                    
        except Exception as e:
            print(f"❌ 请求失败: {e}")


async def main():
    """主函数"""
    print("🧪 测试类别功能")
    print("=" * 60)
    
    try:
        # 测试上传不同类别
        await test_upload_with_categories()
        
        # 测试按类别搜索
        await test_search_by_category()
        
        # 测试获取所有资源
        await test_all_resources()
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
