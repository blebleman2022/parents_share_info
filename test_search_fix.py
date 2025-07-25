#!/usr/bin/env python3
"""
测试搜索修复
"""
import asyncio
import aiohttp


async def test_search_scenarios():
    """测试各种搜索场景"""
    base_url = "http://localhost:8000/api/v1/resources/"
    
    test_cases = [
        {
            "name": "搜索小学3年级",
            "params": {"grade": "小学3年级"},
            "expected": "应该找到包含'小学2年级,小学3年级'的资源"
        },
        {
            "name": "搜索小学2年级", 
            "params": {"grade": "小学2年级"},
            "expected": "应该找到包含'小学2年级,小学3年级'的资源"
        },
        {
            "name": "搜索高中1年级",
            "params": {"grade": "高中1年级"},
            "expected": "应该找到'头脑风暴方案'资源"
        },
        {
            "name": "搜索不存在的年级",
            "params": {"grade": "小学6年级"},
            "expected": "应该没有结果"
        },
        {
            "name": "不指定年级",
            "params": {},
            "expected": "应该返回所有资源"
        },
        {
            "name": "空年级筛选",
            "params": {"grade": ""},
            "expected": "应该返回所有资源"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            print(f"\n🧪 测试: {test_case['name']}")
            print(f"📋 期望: {test_case['expected']}")
            
            try:
                async with session.get(base_url, params=test_case['params']) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        resources = result.get('items', [])
                        print(f"✅ 状态码: {resp.status}")
                        print(f"📊 结果数量: {len(resources)}")
                        
                        for resource in resources:
                            print(f"   📄 {resource['title']} (年级: {resource['grade']})")
                    else:
                        error = await resp.text()
                        print(f"❌ 状态码: {resp.status}")
                        print(f"❌ 错误: {error}")
                        
            except Exception as e:
                print(f"❌ 请求失败: {e}")
            
            print("-" * 50)


async def main():
    """主函数"""
    print("🔍 测试搜索功能修复")
    print("=" * 60)
    
    try:
        await test_search_scenarios()
        print("\n🎉 测试完成！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
