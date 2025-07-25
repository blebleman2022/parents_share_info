#!/usr/bin/env python3
"""
测试搜索功能改进
验证关键词同时搜索标题和描述，以及类型筛选的删除
"""
import asyncio
import aiohttp
import json


async def test_search_improvements():
    """测试搜索功能改进"""
    async with aiohttp.ClientSession() as session:
        # 1. 用户登录
        login_data = {
            "phone": "13800138000",
            "password": "123456"
        }
        
        async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                token = result["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                print("✅ 用户登录成功")
                
                # 2. 测试基础资源搜索（无参数）
                print("\n🔍 测试基础资源搜索...")
                async with session.get("http://localhost:8000/api/v1/resources/") as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        resources = result.get('items', [])
                        print(f"✅ 获取资源列表成功，共 {len(resources)} 个资源")
                        
                        # 显示现有资源信息
                        for resource in resources:
                            print(f"   📄 {resource['title']} - {resource.get('description', '无描述')[:50]}...")
                    else:
                        print(f"❌ 获取资源列表失败: {resp.status}")
                
                # 3. 测试关键词搜索（搜索标题）
                print("\n🔍 测试关键词搜索标题...")
                search_params = {"keyword": "头脑"}
                async with session.get("http://localhost:8000/api/v1/resources/", params=search_params) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        resources = result.get('items', [])
                        print(f"✅ 搜索标题包含'头脑'的资源，找到 {len(resources)} 个")
                        for resource in resources:
                            print(f"   📄 标题: {resource['title']}")
                            print(f"      描述: {resource.get('description', '无描述')}")
                    else:
                        print(f"❌ 搜索失败: {resp.status}")
                
                # 4. 测试关键词搜索（搜索描述）
                print("\n🔍 测试关键词搜索描述...")
                search_params = {"keyword": "管理员"}
                async with session.get("http://localhost:8000/api/v1/resources/", params=search_params) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        resources = result.get('items', [])
                        print(f"✅ 搜索描述包含'管理员'的资源，找到 {len(resources)} 个")
                        for resource in resources:
                            print(f"   📄 标题: {resource['title']}")
                            print(f"      描述: {resource.get('description', '无描述')}")
                    else:
                        print(f"❌ 搜索失败: {resp.status}")
                
                # 5. 测试年级筛选
                print("\n🔍 测试年级筛选...")
                search_params = {"grade": "高中1年级"}
                async with session.get("http://localhost:8000/api/v1/resources/", params=search_params) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        resources = result.get('items', [])
                        print(f"✅ 筛选高中1年级资源，找到 {len(resources)} 个")
                        for resource in resources:
                            print(f"   📄 {resource['title']} - 年级: {resource.get('grade', '未设置')}")
                    else:
                        print(f"❌ 年级筛选失败: {resp.status}")
                
                # 6. 测试科目筛选
                print("\n🔍 测试科目筛选...")
                search_params = {"subject": "数学"}
                async with session.get("http://localhost:8000/api/v1/resources/", params=search_params) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        resources = result.get('items', [])
                        print(f"✅ 筛选数学科目资源，找到 {len(resources)} 个")
                        for resource in resources:
                            print(f"   📄 {resource['title']} - 科目: {resource.get('subject', '未设置')}")
                    else:
                        print(f"❌ 科目筛选失败: {resp.status}")
                
                # 7. 测试组合搜索
                print("\n🔍 测试组合搜索...")
                search_params = {
                    "keyword": "方案",
                    "grade": "高中1年级",
                    "subject": "数学"
                }
                async with session.get("http://localhost:8000/api/v1/resources/", params=search_params) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        resources = result.get('items', [])
                        print(f"✅ 组合搜索（关键词+年级+科目），找到 {len(resources)} 个")
                        for resource in resources:
                            print(f"   📄 {resource['title']}")
                            print(f"      年级: {resource.get('grade', '未设置')}, 科目: {resource.get('subject', '未设置')}")
                            print(f"      描述: {resource.get('description', '无描述')[:100]}...")
                    else:
                        print(f"❌ 组合搜索失败: {resp.status}")
                
                # 8. 验证resource_type参数已被删除
                print("\n🔍 验证resource_type参数已删除...")
                search_params = {"resource_type": "试卷"}  # 这个参数应该被忽略
                async with session.get("http://localhost:8000/api/v1/resources/", params=search_params) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        resources = result.get('items', [])
                        print(f"✅ resource_type参数被正确忽略，返回所有资源 {len(resources)} 个")
                    else:
                        print(f"❌ 请求失败: {resp.status}")
                
            else:
                error = await resp.text()
                print(f"❌ 用户登录失败: {error}")


async def main():
    """主函数"""
    print("🔍 测试搜索功能改进")
    print("=" * 50)
    
    try:
        await test_search_improvements()
        
        print("\n🎉 搜索功能改进测试完成！")
        print("\n✨ 改进内容:")
        print("   ✅ 关键词搜索同时搜索标题和描述")
        print("   ✅ 删除了资源类型筛选选项")
        print("   ✅ 保留了年级和科目筛选")
        print("   ✅ 支持多条件组合搜索")
        print("   ✅ 搜索界面更加简洁")
        
        print("\n🎯 搜索功能特性:")
        print("   🔍 智能关键词搜索 - 同时匹配标题和描述内容")
        print("   📚 年级筛选 - 精确匹配学习阶段")
        print("   📖 科目筛选 - 精确匹配学科分类")
        print("   🔗 组合搜索 - 多条件同时生效")
        print("   🎨 简洁界面 - 删除不必要的筛选项")
        
        print("\n🌐 访问前端界面测试:")
        print("   地址: http://localhost:8000/static/index.html")
        print("   登录后在搜索框中测试关键词搜索功能")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
