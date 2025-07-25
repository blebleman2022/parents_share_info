# FastAPI 到 Django 完整迁移方案

## 🎯 迁移概览

### 迁移范围
- **后端框架**：FastAPI → Django + Django REST Framework
- **数据库**：SQLite保持不变（可选升级到PostgreSQL）
- **前端**：Vue.js保持不变
- **架构模式**：API优先 → Django全栈（可选保持API优先）

### 预估工作量
- **总工作量**：6-8周（1名全职开发者）
- **核心开发**：4-5周
- **测试验证**：1-2周
- **部署调试**：1周

## 📋 详细迁移清单

### 阶段一：环境准备与项目初始化（3-5天）

#### 1.1 创建Django项目结构
```bash
# 创建新的Django项目
django-admin startproject k12_django_platform
cd k12_django_platform

# 创建应用模块
python manage.py startapp authentication  # 用户认证
python manage.py startapp resources      # 资源管理
python manage.py startapp downloads      # 下载管理
python manage.py startapp bounties       # 悬赏系统
python manage.py startapp points         # 积分系统
python manage.py startapp admin_panel    # 管理后台
```

#### 1.2 依赖包安装配置
```python
# requirements.txt
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-filter==23.3
djangorestframework-simplejwt==5.3.0
django-extensions==3.2.3
Pillow==10.1.0
python-magic==0.4.27
celery==5.3.4
redis==5.0.1
drf-yasg==1.21.7  # API文档
django-storages==1.14.2  # 文件存储
```

#### 1.3 Django设置配置
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方应用
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    
    # 本地应用
    'authentication',
    'resources',
    'downloads',
    'bounties',
    'points',
    'admin_panel',
]

# DRF配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### 阶段二：数据模型迁移（5-7天）

#### 2.1 用户模型重构
```python
# authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    nickname = models.CharField(max_length=50, verbose_name="昵称")
    avatar_url = models.URLField(blank=True, verbose_name="头像URL")
    city = models.CharField(max_length=50, blank=True, verbose_name="城市")
    child_grade = models.CharField(max_length=20, blank=True, verbose_name="孩子年级")
    points = models.IntegerField(default=100, verbose_name="积分")
    level = models.IntegerField(default=1, verbose_name="等级")
    daily_downloads = models.IntegerField(default=0, verbose_name="今日下载次数")
    last_download_date = models.DateField(null=True, blank=True, verbose_name="最后下载日期")
    last_signin_date = models.DateField(null=True, blank=True, verbose_name="最后签到日期")
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['nickname']
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
```

#### 2.2 资源模型迁移
```python
# resources/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('课件', '课件'),
        ('教案', '教案'),
        ('学案', '学案'),
        ('作业', '作业'),
        ('试卷', '试卷'),
        ('题集', '题集'),
        ('素材', '素材'),
        ('备课包', '备课包'),
        ('其他', '其他'),
    ]
    
    SUBJECTS = [
        ('语文', '语文'),
        ('数学', '数学'),
        ('英语', '英语'),
        ('物理', '物理'),
        ('化学', '化学'),
        ('生物', '生物'),
        ('历史', '历史'),
        ('地理', '地理'),
        ('政治', '政治'),
    ]
    
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="上传者")
    title = models.CharField(max_length=200, verbose_name="标题")
    description = models.TextField(blank=True, verbose_name="描述")
    file = models.FileField(upload_to='resources/', verbose_name="文件")
    file_size = models.IntegerField(verbose_name="文件大小")
    file_type = models.CharField(max_length=10, verbose_name="文件类型")
    grade = models.CharField(max_length=50, blank=True, verbose_name="年级")
    subject = models.CharField(max_length=20, choices=SUBJECTS, blank=True, verbose_name="科目")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, verbose_name="资源类型")
    download_count = models.IntegerField(default=0, verbose_name="下载次数")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "学习资源"
        verbose_name_plural = "学习资源"
        ordering = ['-created_at']
```

#### 2.3 其他模型迁移
```python
# points/models.py
class PointTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('register', '注册奖励'),
        ('upload', '上传奖励'),
        ('download', '下载消耗'),
        ('signin', '签到奖励'),
        ('download_reward', '被下载奖励'),
        ('bounty_publish', '发布悬赏'),
        ('bounty_reward', '悬赏奖励'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="交易类型")
    points_change = models.IntegerField(verbose_name="积分变化")
    related_resource = models.ForeignKey('resources.Resource', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="相关资源")
    related_bounty = models.ForeignKey('bounties.Bounty', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="相关悬赏")
    description = models.TextField(verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "积分交易"
        verbose_name_plural = "积分交易"
        ordering = ['-created_at']

# bounties/models.py
class Bounty(models.Model):
    STATUS_CHOICES = [
        ('open', '开放中'),
        ('closed', '已关闭'),
        ('completed', '已完成'),
    ]
    
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="发布者")
    title = models.CharField(max_length=200, verbose_name="标题")
    description = models.TextField(verbose_name="描述")
    points_reward = models.IntegerField(verbose_name="悬赏积分")
    grade = models.CharField(max_length=50, blank=True, verbose_name="年级要求")
    subject = models.CharField(max_length=20, blank=True, verbose_name="科目要求")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "悬赏"
        verbose_name_plural = "悬赏"
        ordering = ['-created_at']
```

#### 2.4 数据迁移脚本
```python
# management/commands/migrate_from_fastapi.py
from django.core.management.base import BaseCommand
import sqlite3
from authentication.models import User
from resources.models import Resource

class Command(BaseCommand):
    def handle(self, *args, **options):
        # 连接原FastAPI数据库
        conn = sqlite3.connect('k12_share.db')
        cursor = conn.cursor()
        
        # 迁移用户数据
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        for user_data in users:
            User.objects.create(
                id=user_data[0],
                phone=user_data[1],
                password=user_data[2],  # 需要重新加密
                nickname=user_data[3],
                # ... 其他字段映射
            )
        
        # 迁移资源数据
        cursor.execute("SELECT * FROM resources")
        resources = cursor.fetchall()
        for resource_data in resources:
            Resource.objects.create(
                id=resource_data[0],
                uploader_id=resource_data[1],
                title=resource_data[2],
                # ... 其他字段映射
            )
        
        conn.close()
        self.stdout.write("数据迁移完成")
```

### 阶段三：API接口重构（7-10天）

#### 3.1 序列化器定义
```python
# resources/serializers.py
from rest_framework import serializers
from .models import Resource

class ResourceListSerializer(serializers.ModelSerializer):
    uploader_name = serializers.CharField(source='uploader.nickname', read_only=True)
    
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'grade', 'subject', 
                 'resource_type', 'download_count', 'created_at', 'uploader_name']

class ResourceCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    
    class Meta:
        model = Resource
        fields = ['title', 'description', 'grade', 'subject', 'resource_type', 'file']
    
    def create(self, validated_data):
        validated_data['uploader'] = self.context['request'].user
        return super().create(validated_data)

class ResourceDetailSerializer(serializers.ModelSerializer):
    uploader_name = serializers.CharField(source='uploader.nickname', read_only=True)
    
    class Meta:
        model = Resource
        fields = '__all__'
```

#### 3.2 视图集重构
```python
# resources/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Resource
from .serializers import ResourceListSerializer, ResourceCreateSerializer
from .filters import ResourceFilter

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ResourceFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'download_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ResourceCreateSerializer
        elif self.action == 'list':
            return ResourceListSerializer
        return ResourceDetailSerializer
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        resource = self.get_object()
        # 下载逻辑
        return Response({'message': '下载成功'})
```

#### 3.3 过滤器定义
```python
# resources/filters.py
import django_filters
from .models import Resource

class ResourceFilter(django_filters.FilterSet):
    grade = django_filters.CharFilter(field_name='grade', lookup_expr='icontains')
    subject = django_filters.ChoiceFilter(choices=Resource.SUBJECTS)
    resource_type = django_filters.ChoiceFilter(choices=Resource.RESOURCE_TYPES)
    
    class Meta:
        model = Resource
        fields = ['grade', 'subject', 'resource_type']
```

#### 3.4 URL路由配置
```python
# urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from resources.views import ResourceViewSet
from authentication.views import AuthViewSet

router = DefaultRouter()
router.register(r'resources', ResourceViewSet)
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/', include('authentication.urls')),
]
```

### 阶段四：认证系统重构（3-5天）

#### 4.1 JWT认证配置
```python
# authentication/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'phone'
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'phone': self.user.phone,
            'nickname': self.user.nickname,
            'points': self.user.points,
        }
        return data

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
```

#### 4.2 用户注册视图
```python
# authentication/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 注册奖励积分
        from points.services import PointService
        PointService.add_points(user, 100, 'register', '注册奖励')
        
        return Response({
            'message': '注册成功',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
```

### 阶段五：管理后台开发（2-3天）

#### 5.1 Django Admin配置
```python
# resources/admin.py
from django.contrib import admin
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploader', 'grade', 'subject', 'resource_type', 'download_count', 'created_at']
    list_filter = ['grade', 'subject', 'resource_type', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'uploader__nickname']
    date_hierarchy = 'created_at'
    readonly_fields = ['download_count', 'file_size', 'file_type']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'uploader')
        }),
        ('分类信息', {
            'fields': ('grade', 'subject', 'resource_type')
        }),
        ('文件信息', {
            'fields': ('file', 'file_size', 'file_type')
        }),
        ('状态信息', {
            'fields': ('is_active', 'download_count')
        }),
    )

# authentication/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['phone', 'nickname', 'city', 'child_grade', 'points', 'level', 'is_active']
    list_filter = ['level', 'city', 'child_grade', 'is_active', 'date_joined']
    search_fields = ['phone', 'nickname']
    
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('phone', 'nickname', 'avatar_url', 'city', 'child_grade')
        }),
        ('积分信息', {
            'fields': ('points', 'level', 'daily_downloads', 'last_download_date')
        }),
    )
```

### 阶段六：服务层重构（3-4天）

#### 6.1 积分服务
```python
# points/services.py
from django.db import transaction
from .models import PointTransaction

class PointService:
    @staticmethod
    @transaction.atomic
    def add_points(user, points, transaction_type, description, related_resource=None, related_bounty=None):
        user.points += points
        user.save()
        
        PointTransaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            points_change=points,
            description=description,
            related_resource=related_resource,
            related_bounty=related_bounty
        )
    
    @staticmethod
    @transaction.atomic
    def deduct_points(user, points, transaction_type, description, related_resource=None):
        if user.points < points:
            raise ValueError("积分不足")
        
        user.points -= points
        user.save()
        
        PointTransaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            points_change=-points,
            description=description,
            related_resource=related_resource
        )
```

#### 6.2 文件处理服务
```python
# resources/services.py
import os
import uuid
from django.core.files.storage import default_storage
from django.conf import settings

class FileService:
    @staticmethod
    def save_uploaded_file(uploaded_file):
        # 生成唯一文件名
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # 保存文件
        file_path = default_storage.save(
            f"resources/{unique_filename}",
            uploaded_file
        )
        
        return {
            'file_path': file_path,
            'file_name': unique_filename,
            'file_size': uploaded_file.size,
            'file_type': file_extension[1:].lower()
        }
    
    @staticmethod
    def validate_file(uploaded_file):
        # 文件大小验证
        if uploaded_file.size > settings.MAX_FILE_SIZE:
            raise ValueError("文件大小超过限制")
        
        # 文件类型验证
        file_extension = os.path.splitext(uploaded_file.name)[1][1:].lower()
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            raise ValueError("不支持的文件类型")
        
        return True
```

### 阶段七：前端适配（2-3天）

#### 7.1 API接口适配
```javascript
// static/js/app.js - 修改API调用
const API_BASE_URL = '/api/v1';

// 资源列表API适配
async loadResources() {
    try {
        const params = new URLSearchParams();
        if (this.searchForm.keyword) params.append('search', this.searchForm.keyword);
        if (this.searchForm.grade) params.append('grade', this.searchForm.grade);
        if (this.searchForm.subject) params.append('subject', this.searchForm.subject);
        if (this.searchForm.resource_type) params.append('resource_type', this.searchForm.resource_type);
        
        const response = await axios.get(`${API_BASE_URL}/resources/?${params}`);
        this.resources = response.data.results;  // Django分页格式
        this.total = response.data.count;
    } catch (error) {
        console.error('获取资源列表失败:', error);
    }
},

// 登录API适配
async login() {
    try {
        const response = await axios.post(`${API_BASE_URL}/auth/login/`, {
            phone: this.loginForm.phone,
            password: this.loginForm.password
        });
        
        // 存储JWT token
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        
        // 设置axios默认header
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
        
        this.user = response.data.user;
        this.isLoggedIn = true;
        
        ElMessage.success('登录成功');
    } catch (error) {
        ElMessage.error('登录失败');
    }
}
```

### 阶段八：测试与部署（5-7天）

#### 8.1 单元测试
```python
# resources/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Resource

User = get_user_model()

class ResourceAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone='13800138000',
            password='testpass123',
            nickname='测试用户'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_resource(self):
        data = {
            'title': '测试资源',
            'description': '测试描述',
            'grade': '小学1年级',
            'subject': '数学',
            'resource_type': '课件'
        }
        response = self.client.post('/api/v1/resources/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_resources(self):
        response = self.client.get('/api/v1/resources/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

#### 8.2 部署配置
```python
# settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# 数据库配置（可选升级到PostgreSQL）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'k12_platform',
        'USER': 'postgres',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 静态文件配置
STATIC_ROOT = '/var/www/static/'
MEDIA_ROOT = '/var/www/media/'

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## 📊 迁移风险评估

### 高风险项
- **数据迁移**：用户密码重新加密，数据完整性验证
- **文件路径**：上传文件路径可能需要调整
- **API兼容性**：前端调用需要全面测试

### 中风险项
- **性能差异**：Django可能比FastAPI性能略低
- **部署差异**：从Uvicorn切换到Gunicorn/uWSGI

### 低风险项
- **功能完整性**：Django生态更成熟，功能实现更简单
- **管理后台**：Django Admin提供开箱即用的管理界面

## 🎯 迁移建议

### 推荐迁移策略
1. **并行开发**：保持FastAPI版本运行，并行开发Django版本
2. **分阶段迁移**：先迁移核心功能，再迁移辅助功能
3. **数据同步**：使用数据迁移脚本确保数据一致性
4. **灰度发布**：小范围测试后再全面切换

### 迁移时间线
```
第1-2周：环境准备 + 数据模型迁移
第3-4周：API接口重构 + 认证系统
第5-6周：业务逻辑 + 管理后台 + 前端适配
第7-8周：测试验证 + 部署上线
```

### 关键里程碑
- **第2周末**：完成数据模型定义和数据迁移
- **第4周末**：完成核心API接口开发
- **第6周末**：完成功能开发和前端适配
- **第8周末**：完成测试并正式上线

### 人力资源需求
- **后端开发**：1名全职开发者（6-8周）
- **前端适配**：0.5名开发者（1-2周）
- **测试验证**：0.5名测试人员（1-2周）
- **运维部署**：0.5名运维人员（1周）

### 成本效益分析

**迁移成本**：
- 开发人力：6-8人周
- 测试成本：1-2人周
- 部署成本：0.5人周
- **总成本**：约7.5-10.5人周

**预期收益**：
- **开发效率提升**：Django Admin减少管理功能开发时间50%
- **维护成本降低**：成熟生态减少bug修复时间30%
- **功能扩展便利**：丰富的第三方包加速新功能开发
- **团队技能匹配**：Django学习曲线更平缓

### 风险缓解措施

**数据安全**：
- 完整备份现有数据库
- 编写数据验证脚本
- 实施分批迁移策略

**业务连续性**：
- 保持FastAPI版本并行运行
- 实施蓝绿部署策略
- 准备快速回滚方案

**质量保证**：
- 编写完整的单元测试
- 进行压力测试验证性能
- 实施用户验收测试

## 📋 迁移检查清单

### 开发阶段
- [ ] Django项目初始化完成
- [ ] 所有数据模型定义完成
- [ ] 数据迁移脚本编写完成
- [ ] 核心API接口开发完成
- [ ] 用户认证系统重构完成
- [ ] 管理后台配置完成
- [ ] 业务服务层重构完成
- [ ] 前端API调用适配完成

### 测试阶段
- [ ] 单元测试覆盖率达到80%+
- [ ] API接口测试全部通过
- [ ] 数据迁移验证完成
- [ ] 性能测试达到预期
- [ ] 用户验收测试通过

### 部署阶段
- [ ] 生产环境配置完成
- [ ] 数据库迁移执行完成
- [ ] 静态文件部署完成
- [ ] 监控和日志配置完成
- [ ] 备份和恢复方案验证完成

## 🎉 总结

完整迁移到Django架构是一个系统性工程，需要：

**时间投入**：6-8周全职开发
**主要工作**：
- 重构所有数据模型和API接口
- 重写业务逻辑和服务层
- 适配前端API调用
- 完善测试和部署

**核心价值**：
- 获得成熟的Django生态系统
- 零代码的管理后台
- 更好的长期维护性
- 团队技能标准化

**建议**：考虑到当前FastAPI架构运行良好，建议评估业务需求的紧迫性。如果管理后台需求强烈且团队更熟悉Django，则值得进行迁移；否则可以考虑在FastAPI基础上集成管理工具来解决痛点。
