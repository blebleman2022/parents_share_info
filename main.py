"""
K12家校学习资料共享平台 - FastAPI主应用
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, users, resources, downloads, bounties, search, admin
from app.core.security import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建上传目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "resources"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "avatars"), exist_ok=True)
    
    yield
    
    # 关闭时清理资源
    await engine.dispose()


# 创建FastAPI应用
app = FastAPI(
    title="K12家校学习资料共享平台",
    description="基于积分机制的K12学习资料共享平台API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户"])
app.include_router(resources.router, prefix="/api/v1/resources", tags=["资源"])
app.include_router(downloads.router, prefix="/api/v1/downloads", tags=["下载"])
app.include_router(bounties.router, prefix="/api/v1/bounties", tags=["悬赏"])
app.include_router(search.router, prefix="/api/v1/search", tags=["搜索"])
app.include_router(admin.router, prefix="/api/v1", tags=["管理员"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "K12家校学习资料共享平台API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "服务运行正常"}


@app.get("/api/v1/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "nickname": current_user.nickname,
        "phone": current_user.phone,
        "points": current_user.points,
        "level": current_user.level,
        "child_grade": current_user.child_grade,
        "city": current_user.city
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
