#!/usr/bin/env python3
"""
测试新的配置管理界面功能
"""
import asyncio
import aiohttp
import json


async def test_config_management():
    """测试配置管理功能"""
    async with aiohttp.ClientSession() as session:
        # 1. 管理员登录
        login_data = {
            "phone": "13901119451",
            "password": "admin123"
        }
        
        async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                token = result["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                print("✅ 管理员登录成功")
                
                # 2. 测试获取配置列表
                async with session.get("http://localhost:8000/api/v1/admin/configs", headers=headers) as resp:
                    if resp.status == 200:
                        configs = await resp.json()
                        print(f"✅ 获取配置列表成功，共 {len(configs)} 个配置项")
                        
                        # 显示配置分类
                        point_rules = None
                        user_levels = None
                        system_settings = None
                        other_configs = []
                        
                        for config in configs:
                            # 确保config_value是字典格式
                            config_value = config['config_value']
                            if isinstance(config_value, str):
                                try:
                                    config_value = json.loads(config_value)
                                except json.JSONDecodeError:
                                    config_value = {}

                            if 'point_rules' in config['config_key']:
                                point_rules = config
                                print(f"📊 积分规则配置: {config['config_key']}")
                                print(f"   - 注册奖励: {config_value.get('register_points', 0)} 积分")
                                print(f"   - 上传奖励: {config_value.get('upload_points', 0)} 积分")
                                print(f"   - 下载消耗: {config_value.get('download_cost', 0)} 积分")
                            elif 'user_levels' in config['config_key']:
                                user_levels = config
                                print(f"👥 用户等级配置: {config['config_key']}")
                                if isinstance(config_value, dict):
                                    for level_name, level_config in config_value.items():
                                        if isinstance(level_config, dict):
                                            print(f"   - {level_name}: {level_config.get('min_points', 0)}-{level_config.get('max_points', 0)} 积分")
                            elif 'system_settings' in config['config_key']:
                                system_settings = config
                                print(f"⚙️ 系统设置配置: {config['config_key']}")
                                print(f"   - 最大文件大小: {config_value.get('max_file_size', 0)} 字节")
                                print(f"   - 允许文件类型: {len(config_value.get('allowed_file_types', []))} 种")
                            else:
                                other_configs.append(config)
                                print(f"📄 其他配置: {config['config_key']} - {config['description']}")
                        
                        # 3. 测试更新积分规则配置
                        if point_rules:
                            print("\n🔧 测试更新积分规则配置...")
                            new_point_rules = {
                                "config_value": {
                                    "register_points": 150,  # 增加注册奖励
                                    "upload_points": 25,     # 增加上传奖励
                                    "download_cost": 3,      # 减少下载消耗
                                    "daily_signin_points": 15,
                                    "daily_download_limit": 12
                                },
                                "description": point_rules['description']
                            }
                            
                            async with session.put(f"http://localhost:8000/api/v1/admin/configs/{point_rules['id']}", 
                                                  json=new_point_rules, headers=headers) as resp:
                                if resp.status == 200:
                                    print("✅ 积分规则配置更新成功")
                                else:
                                    error = await resp.text()
                                    print(f"❌ 积分规则配置更新失败: {error}")
                        
                        # 4. 测试创建新的自定义配置
                        print("\n🆕 测试创建新的自定义配置...")
                        new_config = {
                            "config_key": "ui_test_config",
                            "config_value": {
                                "theme": "light",
                                "language": "zh-CN",
                                "features": {
                                    "dark_mode": True,
                                    "notifications": True,
                                    "auto_save": False
                                }
                            },
                            "description": "UI测试配置项"
                        }
                        
                        async with session.post("http://localhost:8000/api/v1/admin/configs", 
                                               json=new_config, headers=headers) as resp:
                            if resp.status == 200:
                                result = await resp.json()
                                print("✅ 新配置创建成功")
                                print(f"   配置ID: {result['id']}")
                                print(f"   配置键: {result['config_key']}")
                            else:
                                error = await resp.text()
                                print(f"❌ 新配置创建失败: {error}")
                        
                        # 5. 再次获取配置列表验证更新
                        print("\n🔍 验证配置更新...")
                        async with session.get("http://localhost:8000/api/v1/admin/configs", headers=headers) as resp:
                            if resp.status == 200:
                                updated_configs = await resp.json()
                                print(f"✅ 配置列表更新成功，现在共 {len(updated_configs)} 个配置项")
                                
                                # 查找更新后的积分规则配置
                                for config in updated_configs:
                                    if config['id'] == point_rules['id']:
                                        config_value = config['config_value']
                                        if isinstance(config_value, str):
                                            try:
                                                config_value = json.loads(config_value)
                                            except json.JSONDecodeError:
                                                config_value = {}

                                        print(f"📊 更新后的积分规则:")
                                        print(f"   - 注册奖励: {config_value.get('register_points', 0)} 积分")
                                        print(f"   - 上传奖励: {config_value.get('upload_points', 0)} 积分")
                                        print(f"   - 下载消耗: {config_value.get('download_cost', 0)} 积分")
                                        break
                    else:
                        error = await resp.text()
                        print(f"❌ 获取配置列表失败: {error}")
            else:
                error = await resp.text()
                print(f"❌ 管理员登录失败: {error}")


async def main():
    """主函数"""
    print("🎨 测试新的可视化配置管理界面")
    print("=" * 50)
    
    try:
        await test_config_management()
        
        print("\n🎉 配置管理功能测试完成！")
        print("\n📋 新功能特性:")
        print("✨ 可视化配置卡片 - 直观显示配置内容")
        print("✨ 专门的编辑表单 - 友好的配置编辑界面")
        print("✨ 分类管理 - 积分规则、用户等级、系统设置分别管理")
        print("✨ 实时预览 - 配置值实时显示在卡片中")
        print("✨ 表单验证 - 确保配置数据的正确性")
        
        print("\n🌐 访问管理员后台:")
        print("   地址: http://localhost:8000/static/admin.html")
        print("   账号: 13901119451")
        print("   密码: admin123")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
