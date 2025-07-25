#!/usr/bin/env python3
"""
测试上传功能修复
"""
import asyncio
import aiohttp
import os
from pathlib import Path


async def test_upload_scenarios():
    """测试各种上传场景"""
    base_url = "http://localhost:8000/api/v1/resources/"
    
    # 创建测试文件（PDF格式）
    test_file_path = "test_upload.pdf"
    # 创建一个简单的PDF文件内容（实际上是文本，但扩展名为pdf）
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("这是一个测试上传文件的内容。\n包含中文字符。")
    
    # 测试用例
    test_cases = [
        {
            "name": "完整信息上传",
            "data": {
                "title": "测试完整上传",
                "description": "这是一个完整的测试描述",
                "grade": "小学1年级",
                "subject": "数学",
                "resource_type": "其他"
            }
        },
        {
            "name": "空描述上传",
            "data": {
                "title": "测试空描述上传",
                "description": "",
                "grade": "小学2年级",
                "subject": "语文",
                "resource_type": "其他"
            }
        },
        {
            "name": "空科目上传",
            "data": {
                "title": "测试空科目上传",
                "description": "测试空科目的描述",
                "grade": "小学3年级",
                "subject": "",
                "resource_type": "其他"
            }
        },
        {
            "name": "空描述和空科目上传",
            "data": {
                "title": "测试空描述和空科目上传",
                "description": "",
                "grade": "小学4年级",
                "subject": "",
                "resource_type": "其他"
            }
        }
    ]
    
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
                print(f"✅ 登录成功，获取token")
            else:
                print(f"❌ 登录失败: {resp.status}")
                return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试各种上传场景
        for test_case in test_cases:
            print(f"\n🧪 测试: {test_case['name']}")
            
            try:
                # 准备文件和数据
                with open(test_file_path, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f, filename='test_upload.pdf', content_type='application/pdf')
                    
                    # 添加表单数据
                    for key, value in test_case['data'].items():
                        data.add_field(key, value)
                    
                    async with session.post(base_url, data=data, headers=headers) as resp:
                        print(f"📊 状态码: {resp.status}")
                        
                        if resp.status == 200:
                            result = await resp.json()
                            print(f"✅ 上传成功!")
                            print(f"   资源ID: {result.get('id')}")
                            print(f"   标题: {result.get('title')}")
                            print(f"   描述: '{result.get('description')}'")
                            print(f"   年级: {result.get('grade')}")
                            print(f"   科目: '{result.get('subject')}'")
                        else:
                            error = await resp.text()
                            print(f"❌ 上传失败: {error}")
                            
            except Exception as e:
                print(f"❌ 请求失败: {e}")
            
            print("-" * 50)
    
    # 清理测试文件
    if os.path.exists(test_file_path):
        os.remove(test_file_path)


async def test_resource_list():
    """测试资源列表API"""
    print(f"\n🔍 测试资源列表API...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/api/v1/resources/") as resp:
            print(f"📊 状态码: {resp.status}")
            
            if resp.status == 200:
                result = await resp.json()
                resources = result.get('items', [])
                print(f"✅ 资源列表获取成功!")
                print(f"📊 资源数量: {len(resources)}")
                
                for resource in resources:
                    print(f"   📄 {resource['title']}")
                    print(f"      描述: '{resource['description']}'")
                    print(f"      年级: {resource['grade']}")
                    print(f"      科目: '{resource['subject']}'")
                    print("   ---")
            else:
                error = await resp.text()
                print(f"❌ 获取失败: {error}")


async def main():
    """主函数"""
    print("🧪 测试上传功能修复")
    print("=" * 60)
    
    try:
        # 测试上传功能
        await test_upload_scenarios()
        
        # 测试资源列表
        await test_resource_list()
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
