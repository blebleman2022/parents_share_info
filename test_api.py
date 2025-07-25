#!/usr/bin/env python3
"""
API功能测试脚本
"""
import asyncio
import aiohttp
import json
import os
from pathlib import Path


class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def register_user(self, phone, password, nickname, child_grade, city=None):
        """测试用户注册"""
        print(f"📝 测试用户注册: {nickname}")
        
        data = {
            "phone": phone,
            "password": password,
            "nickname": nickname,
            "child_grade": child_grade,
            "city": city
        }
        
        async with self.session.post(f"{self.base_url}/api/v1/auth/register", json=data) as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✅ 注册成功: {result['nickname']}")
                return True
            else:
                print(f"❌ 注册失败: {result.get('detail', '未知错误')}")
                return False
    
    async def login_user(self, phone, password):
        """测试用户登录"""
        print(f"🔐 测试用户登录: {phone}")
        
        data = {
            "phone": phone,
            "password": password
        }
        
        async with self.session.post(f"{self.base_url}/api/v1/auth/login", json=data) as resp:
            result = await resp.json()
            if resp.status == 200:
                self.token = result["access_token"]
                print(f"✅ 登录成功，获得token")
                return True
            else:
                print(f"❌ 登录失败: {result.get('detail', '未知错误')}")
                return False
    
    async def get_user_info(self):
        """测试获取用户信息"""
        print("👤 测试获取用户信息")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.get(f"{self.base_url}/api/v1/auth/me", headers=headers) as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✅ 用户信息: {result['nickname']}, 积分: {result['points']}")
                return result
            else:
                print(f"❌ 获取用户信息失败: {result.get('detail', '未知错误')}")
                return None
    
    async def daily_signin(self):
        """测试每日签到"""
        print("📅 测试每日签到")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with self.session.post(f"{self.base_url}/api/v1/users/signin", headers=headers) as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✅ 签到成功: {result['message']}")
                return True
            else:
                print(f"❌ 签到失败: {result.get('detail', '未知错误')}")
                return False
    
    async def upload_resource(self, title, grade, subject, resource_type, description):
        """测试资源上传"""
        print(f"📤 测试资源上传: {title}")
        
        # 创建一个测试文件
        test_file_path = "test_resource.txt"
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("这是一个测试资源文件\n包含一些学习内容...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        data = aiohttp.FormData()
        data.add_field('title', title)
        data.add_field('grade', grade)
        data.add_field('subject', subject)
        data.add_field('resource_type', resource_type)
        data.add_field('description', description)
        data.add_field('file', open(test_file_path, 'rb'), filename='test_resource.txt')
        
        try:
            async with self.session.post(f"{self.base_url}/api/v1/resources/", headers=headers, data=data) as resp:
                result = await resp.json()
                if resp.status == 200:
                    print(f"✅ 资源上传成功: ID {result['id']}")
                    return result['id']
                else:
                    print(f"❌ 资源上传失败: {result.get('detail', '未知错误')}")
                    return None
        finally:
            # 清理测试文件
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    async def get_resources(self):
        """测试获取资源列表"""
        print("📚 测试获取资源列表")
        
        async with self.session.get(f"{self.base_url}/api/v1/resources/") as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✅ 获取资源列表成功: 共 {result['total']} 个资源")
                return result['items']
            else:
                print(f"❌ 获取资源列表失败: {result.get('detail', '未知错误')}")
                return []
    
    async def search_resources(self, keyword):
        """测试搜索资源"""
        print(f"🔍 测试搜索资源: {keyword}")
        
        params = {"q": keyword}
        
        async with self.session.get(f"{self.base_url}/api/v1/search/", params=params) as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✅ 搜索成功: 找到 {result['total']} 个相关资源")
                return result['items']
            else:
                print(f"❌ 搜索失败: {result.get('detail', '未知错误')}")
                return []
    
    async def create_bounty(self, title, description, grade, subject, points_reward):
        """测试创建悬赏"""
        print(f"💰 测试创建悬赏: {title}")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        data = {
            "title": title,
            "description": description,
            "grade": grade,
            "subject": subject,
            "points_reward": points_reward
        }
        
        async with self.session.post(f"{self.base_url}/api/v1/bounties/", headers=headers, json=data) as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✅ 悬赏创建成功: ID {result['id']}")
                return result['id']
            else:
                print(f"❌ 悬赏创建失败: {result.get('detail', '未知错误')}")
                return None
    
    async def get_bounties(self):
        """测试获取悬赏列表"""
        print("💰 测试获取悬赏列表")
        
        async with self.session.get(f"{self.base_url}/api/v1/bounties/") as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✅ 获取悬赏列表成功: 共 {result['total']} 个悬赏")
                return result['items']
            else:
                print(f"❌ 获取悬赏列表失败: {result.get('detail', '未知错误')}")
                return []


async def run_tests():
    """运行所有测试"""
    print("🚀 开始API功能测试")
    print("=" * 50)
    
    async with APITester() as tester:
        # 测试用户注册
        success = await tester.register_user(
            phone="13900139001",
            password="123456",
            nickname="测试用户1",
            child_grade="小学3年级",
            city="北京"
        )
        
        if not success:
            print("❌ 用户注册失败，跳过后续测试")
            return
        
        # 测试用户登录
        success = await tester.login_user("13900139001", "123456")
        if not success:
            print("❌ 用户登录失败，跳过后续测试")
            return
        
        # 测试获取用户信息
        user_info = await tester.get_user_info()
        if not user_info:
            return
        
        # 测试每日签到
        await tester.daily_signin()
        
        # 测试资源上传
        resource_id = await tester.upload_resource(
            title="小学数学练习题",
            grade="小学3年级",
            subject="数学",
            resource_type="试卷",
            description="这是一套小学三年级数学练习题，包含加减乘除等基础运算。"
        )
        
        # 测试获取资源列表
        resources = await tester.get_resources()
        
        # 测试搜索资源
        await tester.search_resources("数学")
        
        # 测试创建悬赏
        bounty_id = await tester.create_bounty(
            title="寻找小学英语单词卡片",
            description="需要小学三年级英语单词卡片，包含图片和发音。",
            grade="小学3年级",
            subject="英语",
            points_reward=100
        )
        
        # 测试获取悬赏列表
        await tester.get_bounties()
        
        print("=" * 50)
        print("✅ 所有测试完成！")
        print("💡 提示：")
        print("   - 访问 http://localhost:8000/static/index.html 使用前端界面")
        print("   - 访问 http://localhost:8000/docs 查看API文档")
        print("   - 测试账号：13900139001 / 123456")


if __name__ == "__main__":
    asyncio.run(run_tests())
