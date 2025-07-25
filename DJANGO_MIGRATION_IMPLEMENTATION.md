# Django迁移详细实施指南

## 🚀 实施准备工作

### 开发环境搭建

#### 1. 创建虚拟环境
```bash
# 创建新的Python虚拟环境
python -m venv django_k12_env
source django_k12_env/bin/activate  # Linux/Mac
# django_k12_env\Scripts\activate   # Windows

# 安装Django及相关依赖
pip install -r requirements_django.txt
```

#### 2. Django项目初始化
```bash
# 创建Django项目
django-admin startproject k12_django_platform
cd k12_django_platform

# 创建应用
python manage.py startapp accounts      # 用户账户
python manage.py startapp resources    # 资源管理
python manage.py startapp downloads    # 下载管理
python manage.py startapp points       # 积分系统
python manage.py startapp bounties     # 悬赏系统
python manage.py startapp notifications # 通知系统
python manage.py startapp reports      # 举报系统
python manage.py startapp analytics    # 数据分析
```

#### 3. 项目结构规划
```
k12_django_platform/
├── k12_django_platform/          # 项目配置
│   ├── settings/                  # 分环境配置
│   │   ├── __init__.py
│   │   ├── base.py               # 基础配置
│   │   ├── development.py        # 开发环境
│   │   ├── production.py         # 生产环境
│   │   └── testing.py            # 测试环境
│   ├── urls.py
│   └── wsgi.py
├── apps/                          # 应用目录
│   ├── accounts/                  # 用户账户应用
│   ├── resources/                 # 资源管理应用
│   ├── downloads/                 # 下载管理应用
│   ├── points/                    # 积分系统应用
│   ├── bounties/                  # 悬赏系统应用
│   └── common/                    # 公共组件
│       ├── models.py             # 基础模型
│       ├── serializers.py        # 基础序列化器
│       ├── permissions.py        # 权限类
│       ├── pagination.py         # 分页类
│       └── utils.py              # 工具函数
├── static/                        # 静态文件
├── media/                         # 媒体文件
├── templates/                     # 模板文件
├── tests/                         # 测试文件
├── requirements/                  # 依赖文件
│   ├── base.txt                  # 基础依赖
│   ├── development.txt           # 开发依赖
│   └── production.txt            # 生产依赖
├── scripts/                       # 脚本文件
│   ├── migrate_data.py           # 数据迁移脚本
│   └── deploy.sh                 # 部署脚本
└── manage.py
```

## 📝 详细配置文件

### 1. 基础配置 (settings/base.py)
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 应用配置
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    'django_extensions',
    'django_celery_beat',
    'django_celery_results',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.resources',
    'apps.downloads',
    'apps.points',
    'apps.bounties',
    'apps.notifications',
    'apps.reports',
    'apps.analytics',
    'apps.common',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件配置
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.common.middleware.RequestLoggingMiddleware',  # 自定义中间件
]

ROOT_URLCONF = 'k12_django_platform.urls'

# 模板配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'k12_django.db',
    }
}

# 国际化配置
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 自定义用户模型
AUTH_USER_MODEL = 'accounts.User'

# REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'EXCEPTION_HANDLER': 'apps.common.exceptions.custom_exception_handler',
}

# JWT配置
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'your-secret-key-here',
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True

# 文件上传配置
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB

# 自定义配置
K12_SETTINGS = {
    'POINTS_CONFIG': {
        'register': 100,
        'upload': 20,
        'download': 10,
        'signin': 5,
        'download_reward': 2,
        'min_bounty': 50,
    },
    'ALLOWED_FILE_TYPES': [
        'pdf', 'doc', 'docx', 'ppt', 'pptx',
        'xls', 'xlsx', 'jpg', 'jpeg', 'png'
    ],
    'MAX_FILE_SIZE': 50 * 1024 * 1024,  # 50MB
    'GRADES': [
        '幼儿园', '小学1年级', '小学2年级', '小学3年级', '小学4年级', '小学5年级', '小学6年级',
        '初中1年级', '初中2年级', '初中3年级',
        '高中1年级', '高中2年级', '高中3年级'
    ],
    'SUBJECTS': [
        '语文', '数学', '英语', '物理', '化学', '生物',
        '历史', '地理', '政治', '音乐', '美术', '体育'
    ],
    'RESOURCE_TYPES': [
        '课件', '教案', '学案', '作业', '试卷',
        '题集', '素材', '备课包', '其他'
    ]
}

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Celery配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
```

### 2. 开发环境配置 (settings/development.py)
```python
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# 开发数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'k12_django_dev.db',
    }
}

# 开发环境邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 开发工具
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug Toolbar配置
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# 缓存配置（开发环境使用本地内存）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

### 3. 生产环境配置 (settings/production.py)
```python
from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# 生产数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'k12_platform'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 60,
    }
}

# 安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 静态文件配置
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# 媒体文件配置（使用云存储）
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# 日志配置
LOGGING['handlers']['file']['filename'] = '/var/log/django/k12_platform.log'
```

## 🔧 公共组件开发

### 1. 基础模型 (apps/common/models.py)
```python
from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """时间戳基础模型"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    """软删除基础模型"""
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="删除时间")
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """软删除"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def hard_delete(self, using=None, keep_parents=False):
        """硬删除"""
        super().delete(using=using, keep_parents=keep_parents)

class BaseModel(TimeStampedModel, SoftDeleteModel):
    """基础模型，包含时间戳和软删除"""
    
    class Meta:
        abstract = True
```

### 2. 自定义分页 (apps/common/pagination.py)
```python
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'items': data,
                'pagination': {
                    'total': self.page.paginator.count,
                    'page': self.page.number,
                    'size': self.page_size,
                    'pages': self.page.paginator.num_pages,
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                }
            }
        })
```

### 3. 异常处理 (apps/common/exceptions.py)
```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """自定义异常处理器"""
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'code': response.status_code,
            'message': 'error',
            'data': None,
            'errors': response.data
        }
        
        # 记录错误日志
        logger.error(f"API Error: {exc}", exc_info=True)
        
        response.data = custom_response_data
    
    return response

class BusinessException(Exception):
    """业务异常"""
    def __init__(self, message, code=400):
        self.message = message
        self.code = code
        super().__init__(self.message)
```

### 4. 权限类 (apps/common/permissions.py)
```python
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """只有所有者可以编辑"""
    
    def has_object_permission(self, request, view, obj):
        # 读权限对所有人开放
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写权限只对所有者开放
        return obj.uploader == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """只有管理员可以编辑"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_staff

class HasEnoughPoints(permissions.BasePermission):
    """检查用户积分是否足够"""
    
    def has_permission(self, request, view):
        if request.method == 'POST' and hasattr(view, 'required_points'):
            return request.user.points >= view.required_points
        return True
```

## 📊 数据迁移详细方案

### 1. 数据迁移脚本 (scripts/migrate_data.py)
```python
#!/usr/bin/env python
"""
FastAPI到Django数据迁移脚本
"""
import os
import sys
import sqlite3
import django
from datetime import datetime
from django.contrib.auth.hashers import make_password

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'k12_django_platform.settings.development')
django.setup()

from apps.accounts.models import User
from apps.resources.models import Resource
from apps.points.models import PointTransaction
from apps.bounties.models import Bounty

class DataMigrator:
    def __init__(self, fastapi_db_path):
        self.fastapi_db_path = fastapi_db_path
        self.conn = sqlite3.connect(fastapi_db_path)
        self.cursor = self.conn.cursor()
    
    def migrate_users(self):
        """迁移用户数据"""
        print("开始迁移用户数据...")
        
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        
        # 获取列名
        columns = [description[0] for description in self.cursor.description]
        
        migrated_count = 0
        for user_data in users:
            user_dict = dict(zip(columns, user_data))
            
            try:
                # 检查用户是否已存在
                if User.objects.filter(phone=user_dict['phone']).exists():
                    print(f"用户 {user_dict['phone']} 已存在，跳过")
                    continue
                
                # 创建Django用户
                user = User.objects.create(
                    id=user_dict['id'],
                    phone=user_dict['phone'],
                    password=make_password(user_dict['password_hash']),  # 重新加密密码
                    nickname=user_dict.get('nickname', ''),
                    city=user_dict.get('city', ''),
                    child_grade=user_dict.get('child_grade', ''),
                    points=user_dict.get('points', 100),
                    level=user_dict.get('level', 1),
                    is_active=user_dict.get('is_active', True),
                    date_joined=datetime.fromisoformat(user_dict['created_at'].replace('Z', '+00:00')) if user_dict.get('created_at') else datetime.now(),
                )
                
                migrated_count += 1
                print(f"迁移用户: {user.phone}")
                
            except Exception as e:
                print(f"迁移用户 {user_dict['phone']} 失败: {e}")
        
        print(f"用户迁移完成，共迁移 {migrated_count} 个用户")
    
    def migrate_resources(self):
        """迁移资源数据"""
        print("开始迁移资源数据...")
        
        self.cursor.execute("SELECT * FROM resources")
        resources = self.cursor.fetchall()
        
        columns = [description[0] for description in self.cursor.description]
        
        migrated_count = 0
        for resource_data in resources:
            resource_dict = dict(zip(columns, resource_data))
            
            try:
                # 获取上传者
                uploader = User.objects.get(id=resource_dict['uploader_id'])
                
                # 创建资源
                resource = Resource.objects.create(
                    id=resource_dict['id'],
                    uploader=uploader,
                    title=resource_dict['title'],
                    description=resource_dict.get('description', ''),
                    file_name=resource_dict['file_name'],
                    file_path=resource_dict['file_path'],
                    file_size=resource_dict['file_size'],
                    file_type=resource_dict['file_type'],
                    grade=resource_dict.get('grade', ''),
                    subject=resource_dict.get('subject', ''),
                    resource_type=resource_dict.get('resource_type', '其他'),
                    download_count=resource_dict.get('download_count', 0),
                    is_active=resource_dict.get('is_active', True),
                    created_at=datetime.fromisoformat(resource_dict['created_at'].replace('Z', '+00:00')) if resource_dict.get('created_at') else datetime.now(),
                )
                
                migrated_count += 1
                print(f"迁移资源: {resource.title}")
                
            except Exception as e:
                print(f"迁移资源 {resource_dict['title']} 失败: {e}")
        
        print(f"资源迁移完成，共迁移 {migrated_count} 个资源")
    
    def migrate_point_transactions(self):
        """迁移积分交易数据"""
        print("开始迁移积分交易数据...")
        
        self.cursor.execute("SELECT * FROM point_transactions")
        transactions = self.cursor.fetchall()
        
        columns = [description[0] for description in self.cursor.description]
        
        migrated_count = 0
        for transaction_data in transactions:
            transaction_dict = dict(zip(columns, transaction_data))
            
            try:
                user = User.objects.get(id=transaction_dict['user_id'])
                
                # 获取相关资源（如果存在）
                related_resource = None
                if transaction_dict.get('related_resource_id'):
                    try:
                        related_resource = Resource.objects.get(id=transaction_dict['related_resource_id'])
                    except Resource.DoesNotExist:
                        pass
                
                # 创建积分交易记录
                transaction = PointTransaction.objects.create(
                    id=transaction_dict['id'],
                    user=user,
                    transaction_type=transaction_dict['transaction_type'],
                    points_change=transaction_dict['points_change'],
                    related_resource=related_resource,
                    description=transaction_dict['description'],
                    created_at=datetime.fromisoformat(transaction_dict['created_at'].replace('Z', '+00:00')) if transaction_dict.get('created_at') else datetime.now(),
                )
                
                migrated_count += 1
                print(f"迁移积分交易: {transaction.description}")
                
            except Exception as e:
                print(f"迁移积分交易失败: {e}")
        
        print(f"积分交易迁移完成，共迁移 {migrated_count} 条记录")
    
    def run_migration(self):
        """执行完整迁移"""
        print("开始数据迁移...")
        print(f"源数据库: {self.fastapi_db_path}")
        
        try:
            self.migrate_users()
            self.migrate_resources()
            self.migrate_point_transactions()
            
            print("数据迁移完成！")
            
        except Exception as e:
            print(f"数据迁移失败: {e}")
        finally:
            self.conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python migrate_data.py <fastapi_db_path>")
        sys.exit(1)
    
    fastapi_db_path = sys.argv[1]
    migrator = DataMigrator(fastapi_db_path)
    migrator.run_migration()
```

### 2. 数据验证脚本 (scripts/validate_migration.py)
```python
#!/usr/bin/env python
"""
数据迁移验证脚本
"""
import os
import sys
import sqlite3
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'k12_django_platform.settings.development')
django.setup()

from apps.accounts.models import User
from apps.resources.models import Resource
from apps.points.models import PointTransaction

class MigrationValidator:
    def __init__(self, fastapi_db_path):
        self.fastapi_db_path = fastapi_db_path
        self.conn = sqlite3.connect(fastapi_db_path)
        self.cursor = self.conn.cursor()
    
    def validate_users(self):
        """验证用户数据迁移"""
        print("验证用户数据...")
        
        # 统计原数据库用户数量
        self.cursor.execute("SELECT COUNT(*) FROM users")
        fastapi_user_count = self.cursor.fetchone()[0]
        
        # 统计Django数据库用户数量
        django_user_count = User.objects.count()
        
        print(f"FastAPI用户数量: {fastapi_user_count}")
        print(f"Django用户数量: {django_user_count}")
        
        if fastapi_user_count == django_user_count:
            print("✅ 用户数据迁移验证通过")
        else:
            print("❌ 用户数据迁移验证失败")
        
        # 抽样验证用户数据
        self.cursor.execute("SELECT phone, nickname, points FROM users LIMIT 5")
        sample_users = self.cursor.fetchall()
        
        for phone, nickname, points in sample_users:
            try:
                django_user = User.objects.get(phone=phone)
                if django_user.nickname == nickname and django_user.points == points:
                    print(f"✅ 用户 {phone} 数据一致")
                else:
                    print(f"❌ 用户 {phone} 数据不一致")
            except User.DoesNotExist:
                print(f"❌ 用户 {phone} 在Django中不存在")
    
    def validate_resources(self):
        """验证资源数据迁移"""
        print("验证资源数据...")
        
        # 统计原数据库资源数量
        self.cursor.execute("SELECT COUNT(*) FROM resources")
        fastapi_resource_count = self.cursor.fetchone()[0]
        
        # 统计Django数据库资源数量
        django_resource_count = Resource.objects.count()
        
        print(f"FastAPI资源数量: {fastapi_resource_count}")
        print(f"Django资源数量: {django_resource_count}")
        
        if fastapi_resource_count == django_resource_count:
            print("✅ 资源数据迁移验证通过")
        else:
            print("❌ 资源数据迁移验证失败")
    
    def validate_point_transactions(self):
        """验证积分交易数据迁移"""
        print("验证积分交易数据...")
        
        # 统计原数据库积分交易数量
        self.cursor.execute("SELECT COUNT(*) FROM point_transactions")
        fastapi_transaction_count = self.cursor.fetchone()[0]
        
        # 统计Django数据库积分交易数量
        django_transaction_count = PointTransaction.objects.count()
        
        print(f"FastAPI积分交易数量: {fastapi_transaction_count}")
        print(f"Django积分交易数量: {django_transaction_count}")
        
        if fastapi_transaction_count == django_transaction_count:
            print("✅ 积分交易数据迁移验证通过")
        else:
            print("❌ 积分交易数据迁移验证失败")
    
    def run_validation(self):
        """执行完整验证"""
        print("开始数据迁移验证...")
        
        try:
            self.validate_users()
            self.validate_resources()
            self.validate_point_transactions()
            
            print("数据迁移验证完成！")
            
        except Exception as e:
            print(f"数据迁移验证失败: {e}")
        finally:
            self.conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python validate_migration.py <fastapi_db_path>")
        sys.exit(1)
    
    fastapi_db_path = sys.argv[1]
    validator = MigrationValidator(fastapi_db_path)
    validator.run_validation()
```

这个详细的实施指南提供了：

1. **完整的项目结构规划**
2. **详细的配置文件模板**
3. **公共组件的具体实现**
4. **数据迁移的完整脚本**
5. **数据验证的自动化工具**

接下来我可以继续提供具体应用的详细实现代码，包括用户认证、资源管理、积分系统等模块的完整代码。您希望我继续哪个部分？
