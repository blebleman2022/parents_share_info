"""
应用配置
"""
import os
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """应用设置"""
    
    # 基础配置
    APP_NAME: str = "K12家校学习资料共享平台"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./k12_share.db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30天
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = [
        "pdf", "doc", "docx", "ppt", "pptx", 
        "xls", "xlsx", "jpg", "jpeg", "png"
    ]
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 积分系统配置
    POINTS_CONFIG: dict = {
        "register": 100,      # 注册奖励
        "upload": 20,         # 上传奖励
        "download": 10,       # 下载消耗
        "signin": 5,          # 签到奖励
        "download_reward": 2, # 资源被下载奖励
        "min_bounty": 50      # 最低悬赏积分
    }
    
    # 用户等级配置
    USER_LEVELS: dict = {
        "新手用户": {"min_points": 0, "max_points": 499, "daily_downloads": 5},
        "活跃用户": {"min_points": 500, "max_points": 1999, "daily_downloads": 15},
        "资深用户": {"min_points": 2000, "max_points": 4999, "daily_downloads": 30},
        "专家用户": {"min_points": 5000, "max_points": -1, "daily_downloads": -1}
    }
    
    # 年级和科目配置
    GRADES: List[str] = [
        "小学1年级", "小学2年级", "小学3年级", "小学4年级", "小学5年级", "预初",
        "初中1年级", "初中2年级", "初中3年级",
        "高中1年级", "高中2年级", "高中3年级"
    ]
    
    SUBJECTS: List[str] = [
        "语文", "数学", "英语", "物理", "化学", 
        "生物", "历史", "地理", "政治"
    ]
    
    RESOURCE_TYPES: List[str] = [
        "课件", "教案", "学案", "作业", "试卷",
        "题集", "素材", "备课包", "其他"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建设置实例
settings = Settings()
