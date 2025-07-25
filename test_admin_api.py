#!/usr/bin/env python3
"""
测试管理员API的脚本
"""
import asyncio
import aiohttp
import json


async def test_admin_login():
    """测试管理员登录"""
    async with aiohttp.ClientSession() as session:
        # 1. 登录管理员账号
        login_data = {
            "phone": "13901119451",
            "password": "admin123"
        }
        
        async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as resp:
            if resp.status == 200:
                login_result = await resp.json()
                token = login_result["access_token"]
                print("✅ 管理员登录成功")
                print(f"   Token: {token[:50]}...")
                
                # 2. 测试获取当前用户信息
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get("http://localhost:8000/api/v1/auth/me", headers=headers) as resp:
                    if resp.status == 200:
                        user_info = await resp.json()
                        print("✅ 获取用户信息成功")
                        print(f"   用户: {user_info['nickname']} ({user_info['phone']})")
                        
                        # 3. 测试获取系统配置
                        async with session.get("http://localhost:8000/api/v1/admin/configs", headers=headers) as resp:
                            if resp.status == 200:
                                configs = await resp.json()
                                print("✅ 获取系统配置成功")
                                print(f"   配置数量: {len(configs)}")
                                for config in configs:
                                    print(f"   - {config['config_key']}: {config['description']}")
                            else:
                                error_text = await resp.text()
                                print(f"❌ 获取系统配置失败: {resp.status} - {error_text}")
                        
                        # 4. 测试获取用户列表
                        async with session.get("http://localhost:8000/api/v1/admin/users", headers=headers) as resp:
                            if resp.status == 200:
                                users = await resp.json()
                                print("✅ 获取用户列表成功")
                                print(f"   用户数量: {len(users)}")
                                for user in users[:3]:  # 只显示前3个用户
                                    print(f"   - {user['nickname']} ({user['phone']}) - {user['level']}")
                            else:
                                error_text = await resp.text()
                                print(f"❌ 获取用户列表失败: {resp.status} - {error_text}")
                        
                        # 5. 测试获取资源列表
                        async with session.get("http://localhost:8000/api/v1/admin/resources", headers=headers) as resp:
                            if resp.status == 200:
                                resources = await resp.json()
                                print("✅ 获取资源列表成功")
                                print(f"   资源数量: {len(resources)}")
                                for resource in resources[:3]:  # 只显示前3个资源
                                    print(f"   - {resource['title']} ({resource['file_type']}) - 下载{resource['download_count']}次")
                            else:
                                error_text = await resp.text()
                                print(f"❌ 获取资源列表失败: {resp.status} - {error_text}")
                        
                        # 6. 测试获取操作日志
                        async with session.get("http://localhost:8000/api/v1/admin/logs", headers=headers) as resp:
                            if resp.status == 200:
                                logs = await resp.json()
                                print("✅ 获取操作日志成功")
                                print(f"   日志数量: {len(logs)}")
                                for log in logs[:3]:  # 只显示前3条日志
                                    print(f"   - {log['action_type']}: {log['action_description']}")
                            else:
                                error_text = await resp.text()
                                print(f"❌ 获取操作日志失败: {resp.status} - {error_text}")
                        
                    else:
                        error_text = await resp.text()
                        print(f"❌ 获取用户信息失败: {resp.status} - {error_text}")
                
            else:
                error_text = await resp.text()
                print(f"❌ 管理员登录失败: {resp.status} - {error_text}")


async def test_non_admin_access():
    """测试非管理员用户访问管理员功能"""
    async with aiohttp.ClientSession() as session:
        # 使用普通用户登录
        login_data = {
            "phone": "13800138000",
            "password": "123456"
        }
        
        async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as resp:
            if resp.status == 200:
                login_result = await resp.json()
                token = login_result["access_token"]
                print("✅ 普通用户登录成功")
                
                # 尝试访问管理员功能
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get("http://localhost:8000/api/v1/admin/configs", headers=headers) as resp:
                    if resp.status == 403:
                        print("✅ 普通用户无法访问管理员功能（正确）")
                    else:
                        print(f"❌ 普通用户可以访问管理员功能（错误）: {resp.status}")
            else:
                print("ℹ️  普通用户不存在，跳过权限测试")


async def main():
    """主函数"""
    print("🧪 开始测试管理员API功能...")
    print()
    
    try:
        await test_admin_login()
        print()
        await test_non_admin_access()
        
        print()
        print("🎉 管理员API测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
