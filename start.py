#!/usr/bin/env python3
"""
K12家校学习资料共享平台启动脚本
"""
import os
import sys
import asyncio
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.database import engine, Base


async def create_tables():
    """创建数据库表"""
    print("正在创建数据库表...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据库表创建成功")
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        return False
    return True


def create_directories():
    """创建必要的目录"""
    print("正在创建必要的目录...")
    directories = [
        settings.UPLOAD_DIR,
        os.path.join(settings.UPLOAD_DIR, "resources"),
        os.path.join(settings.UPLOAD_DIR, "avatars"),
        "static",
        "static/js",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 创建目录: {directory}")


def check_dependencies():
    """检查依赖是否安装"""
    print("正在检查依赖...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ 核心依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def start_server():
    """启动服务器"""
    print("正在启动服务器...")
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")


async def main():
    """主函数"""
    print("🚀 K12家校学习资料共享平台启动中...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 创建目录
    create_directories()
    
    # 创建数据库表
    if not await create_tables():
        return
    
    print("=" * 50)
    print("✅ 初始化完成！")
    print(f"📱 前端界面: http://localhost:8000/static/index.html")
    print(f"📚 API文档: http://localhost:8000/docs")
    print(f"🔧 配置信息:")
    print(f"   - 数据库: {settings.DATABASE_URL}")
    print(f"   - 上传目录: {settings.UPLOAD_DIR}")
    print(f"   - 调试模式: {settings.DEBUG}")
    print("=" * 50)
    
    # 启动服务器
    start_server()


if __name__ == "__main__":
    asyncio.run(main())
