#!/usr/bin/env python3
"""
测试资源API修复
"""
import asyncio
import aiohttp


async def test_resources_api():
    """测试资源API"""
    async with aiohttp.ClientSession() as session:
        print("🔍 测试资源API...")
        
        async with session.get('http://localhost:8000/api/v1/resources/') as resp:
            print(f'状态码: {resp.status}')
            
            if resp.status == 200:
                result = await resp.json()
                resources = result.get('items', [])
                print(f'✅ 资源数量: {len(resources)}')
                
                for resource in resources:
                    print(f'📄 资源: {resource["title"]}')
                    print(f'   年级: {resource["grade"]}')
                    print(f'   科目: {resource["subject"]}')
                    print(f'   类型: {resource["resource_type"]}')
                    print(f'   激活: {resource["is_active"]}')
                    print('---')
                    
            else:
                error = await resp.text()
                print(f'❌ 错误: {error}')


async def main():
    """主函数"""
    print("🧪 测试资源API修复")
    print("=" * 30)
    
    try:
        await test_resources_api()
        print("\n🎉 测试完成！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
