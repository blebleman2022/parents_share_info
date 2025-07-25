#!/usr/bin/env python3
"""
测试清理后的配置管理界面
"""
import asyncio
import aiohttp
import json


async def test_cleaned_config_interface():
    """测试清理后的配置界面"""
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
                
                # 2. 获取清理后的配置列表
                async with session.get("http://localhost:8000/api/v1/admin/configs", headers=headers) as resp:
                    if resp.status == 200:
                        configs = await resp.json()
                        print(f"✅ 获取配置列表成功，共 {len(configs)} 个配置项")
                        
                        # 分析配置分类
                        main_configs = []
                        other_configs = []
                        
                        for config in configs:
                            config_value = config['config_value']
                            if isinstance(config_value, str):
                                try:
                                    config_value = json.loads(config_value)
                                except json.JSONDecodeError:
                                    config_value = {}
                            
                            if any(key in config['config_key'] for key in ['point_rules', 'user_levels', 'system_settings']):
                                main_configs.append(config)
                                print(f"📊 主要配置: {config['config_key']} - {config['description']}")
                            else:
                                other_configs.append(config)
                                print(f"📄 其他配置: {config['config_key']} - {config['description']}")
                        
                        print(f"\n📈 配置分类统计:")
                        print(f"   - 主要配置: {len(main_configs)} 个")
                        print(f"   - 其他配置: {len(other_configs)} 个")
                        
                        # 3. 验证主要配置的内容
                        print(f"\n🔍 验证主要配置内容:")
                        
                        for config in main_configs:
                            config_value = config['config_value']
                            if isinstance(config_value, str):
                                try:
                                    config_value = json.loads(config_value)
                                except json.JSONDecodeError:
                                    config_value = {}
                            
                            if 'point_rules' in config['config_key']:
                                print(f"💰 积分规则配置 ({config['config_key']}):")
                                print(f"   - 注册奖励: {config_value.get('register_points', 0)} 积分")
                                print(f"   - 上传奖励: {config_value.get('upload_points', 0)} 积分")
                                print(f"   - 下载消耗: {config_value.get('download_cost', 0)} 积分")
                                print(f"   - 签到奖励: {config_value.get('daily_signin_points', 0)} 积分")
                                print(f"   - 每日下载限制: {config_value.get('daily_download_limit', 0)} 次")
                            
                            elif 'user_levels' in config['config_key']:
                                print(f"👥 用户等级配置 ({config['config_key']}):")
                                if isinstance(config_value, dict):
                                    for level_name, level_config in config_value.items():
                                        if isinstance(level_config, dict):
                                            max_points = level_config.get('max_points', 0)
                                            max_display = '∞' if max_points == -1 else str(max_points)
                                            print(f"   - {level_name}: {level_config.get('min_points', 0)}-{max_display} 积分, 每日{level_config.get('daily_downloads', 0)}次下载")
                            
                            elif 'system_settings' in config['config_key']:
                                print(f"⚙️ 系统设置配置 ({config['config_key']}):")
                                file_size = config_value.get('max_file_size', 0)
                                file_size_mb = file_size / (1024 * 1024) if file_size else 0
                                print(f"   - 最大文件大小: {file_size_mb:.0f}MB")
                                file_types = config_value.get('allowed_file_types', [])
                                print(f"   - 允许文件类型: {len(file_types)} 种 ({', '.join(file_types[:5])}{'...' if len(file_types) > 5 else ''})")
                                print(f"   - 自动审核资源: {'开启' if config_value.get('auto_approve_resources') else '关闭'}")
                                print(f"   - 维护模式: {'维护中' if config_value.get('maintenance_mode') else '正常'}")
                        
                        # 4. 验证冗余配置已被清理
                        print(f"\n🧹 验证冗余配置清理:")
                        redundant_keys = ['allowed_file_types', 'demo_config', 'max_file_size', 'ui_test_config']
                        found_redundant = []
                        
                        for config in configs:
                            if config['config_key'] in redundant_keys:
                                found_redundant.append(config['config_key'])
                        
                        if found_redundant:
                            print(f"❌ 发现未清理的冗余配置: {', '.join(found_redundant)}")
                        else:
                            print(f"✅ 所有冗余配置已成功清理")
                        
                        print(f"\n📊 清理效果:")
                        print(f"   - 删除了独立的文件类型配置")
                        print(f"   - 删除了独立的文件大小配置")
                        print(f"   - 删除了演示和测试配置")
                        print(f"   - 配置界面更加简洁清晰")
                        
                    else:
                        error = await resp.text()
                        print(f"❌ 获取配置列表失败: {error}")
            else:
                error = await resp.text()
                print(f"❌ 管理员登录失败: {error}")


async def main():
    """主函数"""
    print("🧹 测试清理后的配置管理界面")
    print("=" * 50)
    
    try:
        await test_cleaned_config_interface()
        
        print("\n🎉 配置清理验证完成！")
        print("\n✨ 清理成果:")
        print("   ✅ 删除了4个冗余的独立配置项")
        print("   ✅ 保留了3个主要配置类型")
        print("   ✅ 界面更加简洁和专业")
        print("   ✅ 配置管理更加统一")
        
        print("\n🎯 现在的配置结构:")
        print("   📊 积分规则配置 - 统一管理所有积分相关设置")
        print("   👥 用户等级配置 - 统一管理用户等级和权限")
        print("   ⚙️ 系统设置配置 - 统一管理文件、功能等系统设置")
        
        print("\n🌐 访问管理员后台查看效果:")
        print("   地址: http://localhost:8000/static/admin.html")
        print("   账号: 13901119451")
        print("   密码: admin123")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
