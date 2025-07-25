#!/usr/bin/env python3
"""
管理员后台功能演示脚本
"""
import asyncio
import aiohttp
import json


class AdminDemo:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.token = None
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login(self):
        """管理员登录"""
        print("🔐 正在登录管理员账号...")
        login_data = {
            "phone": "13901119451",
            "password": "admin123"
        }
        
        async with self.session.post(f"{self.base_url}/auth/login", json=login_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                self.token = result["access_token"]
                print("✅ 管理员登录成功")
                return True
            else:
                error = await resp.text()
                print(f"❌ 登录失败: {error}")
                return False
    
    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    async def demo_dashboard(self):
        """演示数据概览功能"""
        print("\n📊 === 数据概览演示 ===")
        
        # 获取用户统计
        async with self.session.get(f"{self.base_url}/admin/users", headers=self.headers) as resp:
            if resp.status == 200:
                users = await resp.json()
                print(f"👥 总用户数: {len(users)}")
                active_users = [u for u in users if u['is_active']]
                print(f"✅ 活跃用户: {len(active_users)}")
        
        # 获取资源统计
        async with self.session.get(f"{self.base_url}/admin/resources", headers=self.headers) as resp:
            if resp.status == 200:
                resources = await resp.json()
                print(f"📁 总资源数: {len(resources)}")
                total_downloads = sum(r['download_count'] for r in resources)
                print(f"⬇️ 总下载次数: {total_downloads}")
    
    async def demo_config_management(self):
        """演示系统配置管理功能"""
        print("\n⚙️ === 系统配置管理演示 ===")
        
        # 获取现有配置
        async with self.session.get(f"{self.base_url}/admin/configs", headers=self.headers) as resp:
            if resp.status == 200:
                configs = await resp.json()
                print(f"📋 当前配置项数量: {len(configs)}")
                
                for config in configs:
                    print(f"   - {config['config_key']}: {config['description']}")
        
        # 演示创建新配置
        print("\n🆕 创建新的系统配置...")
        new_config = {
            "config_key": "demo_config",
            "config_value": {
                "demo_setting": True,
                "demo_value": 42,
                "demo_message": "这是一个演示配置"
            },
            "description": "演示配置项"
        }
        
        async with self.session.post(f"{self.base_url}/admin/configs", json=new_config, headers=self.headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ 配置创建成功: {result['config_key']}")
                config_id = result['id']
                
                # 演示更新配置
                print("📝 更新配置...")
                update_data = {
                    "config_value": {
                        "demo_setting": False,
                        "demo_value": 100,
                        "demo_message": "配置已更新"
                    },
                    "description": "更新后的演示配置"
                }
                
                async with self.session.put(f"{self.base_url}/admin/configs/{config_id}", json=update_data, headers=self.headers) as resp:
                    if resp.status == 200:
                        print("✅ 配置更新成功")
                    else:
                        error = await resp.text()
                        print(f"❌ 配置更新失败: {error}")
            else:
                error = await resp.text()
                print(f"❌ 配置创建失败: {error}")
    
    async def demo_user_management(self):
        """演示用户管理功能"""
        print("\n👥 === 用户管理演示 ===")
        
        # 获取用户列表
        async with self.session.get(f"{self.base_url}/admin/users", headers=self.headers) as resp:
            if resp.status == 200:
                users = await resp.json()
                print(f"📋 用户列表 ({len(users)} 个用户):")
                
                for user in users:
                    status = "✅ 正常" if user['is_active'] else "❌ 禁用"
                    print(f"   - {user['nickname']} ({user['phone']}) - {user['level']} - {user['points']}积分 - {status}")
                
                # 演示用户信息更新（如果有非管理员用户）
                non_admin_users = [u for u in users if u['phone'] != '13901119451']
                if non_admin_users:
                    demo_user = non_admin_users[0]
                    print(f"\n📝 演示更新用户: {demo_user['nickname']}")
                    
                    update_data = {
                        "points": demo_user['points'] + 50,
                        "level": "活跃用户"
                    }
                    
                    async with self.session.put(f"{self.base_url}/admin/users/{demo_user['id']}", json=update_data, headers=self.headers) as resp:
                        if resp.status == 200:
                            print("✅ 用户信息更新成功")
                        else:
                            error = await resp.text()
                            print(f"❌ 用户信息更新失败: {error}")
    
    async def demo_resource_management(self):
        """演示资源管理功能"""
        print("\n📁 === 资源管理演示 ===")
        
        # 获取资源列表
        async with self.session.get(f"{self.base_url}/admin/resources", headers=self.headers) as resp:
            if resp.status == 200:
                resources = await resp.json()
                print(f"📋 资源列表 ({len(resources)} 个资源):")
                
                for resource in resources:
                    status = "✅ 正常" if resource['is_active'] else "❌ 已删除"
                    print(f"   - {resource['title']} ({resource['file_type']}) - {resource['grade']} {resource['subject']} - 下载{resource['download_count']}次 - {status}")
                
                # 演示资源信息更新（如果有资源）
                if resources:
                    demo_resource = resources[0]
                    print(f"\n📝 演示更新资源: {demo_resource['title']}")
                    
                    update_data = {
                        "description": f"[管理员更新] {demo_resource.get('description', '')}",
                        "grade": demo_resource['grade'],
                        "subject": demo_resource['subject']
                    }
                    
                    async with self.session.put(f"{self.base_url}/admin/resources/{demo_resource['id']}", json=update_data, headers=self.headers) as resp:
                        if resp.status == 200:
                            print("✅ 资源信息更新成功")
                        else:
                            error = await resp.text()
                            print(f"❌ 资源信息更新失败: {error}")
    
    async def demo_operation_logs(self):
        """演示操作日志功能"""
        print("\n📝 === 操作日志演示 ===")
        
        async with self.session.get(f"{self.base_url}/admin/logs", headers=self.headers) as resp:
            if resp.status == 200:
                logs = await resp.json()
                print(f"📋 操作日志 ({len(logs)} 条记录):")
                
                for log in logs[:5]:  # 只显示最近5条
                    print(f"   - {log['action_type']}: {log['action_description']} ({log['created_at'][:19]})")
                
                if len(logs) > 5:
                    print(f"   ... 还有 {len(logs) - 5} 条记录")
    
    async def run_demo(self):
        """运行完整演示"""
        print("🎭 K12家校学习资料共享平台 - 管理员后台功能演示")
        print("=" * 60)
        
        # 登录
        if not await self.login():
            return
        
        # 演示各个功能模块
        await self.demo_dashboard()
        await self.demo_config_management()
        await self.demo_user_management()
        await self.demo_resource_management()
        await self.demo_operation_logs()
        
        print("\n🎉 === 演示完成 ===")
        print("\n📋 管理员后台访问信息:")
        print("   🌐 访问地址: http://localhost:8000/static/admin.html")
        print("   📱 管理员账号: 13901119451")
        print("   🔑 登录密码: admin123")
        print("\n✨ 所有功能都已正常工作，可以开始使用管理员后台了！")


async def main():
    """主函数"""
    try:
        async with AdminDemo() as demo:
            await demo.run_demo()
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
