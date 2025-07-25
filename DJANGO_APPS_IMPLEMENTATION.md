# Django应用模块详细实现

## 🔐 用户认证模块 (apps/accounts)

### 1. 用户模型 (apps/accounts/models.py)
```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from apps.common.models import TimeStampedModel

class User(AbstractUser):
    """自定义用户模型"""
    
    # 移除默认的username字段
    username = None
    
    # 手机号作为用户名
    phone_validator = RegexValidator(
        regex=r'^1[3-9]\d{9}$',
        message='请输入有效的手机号码'
    )
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name='手机号'
    )
    
    # 用户基本信息
    nickname = models.CharField(max_length=50, verbose_name='昵称')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='头像'
    )
    city = models.CharField(max_length=50, blank=True, verbose_name='城市')
    child_grade = models.CharField(max_length=20, blank=True, verbose_name='孩子年级')
    
    # 积分系统
    points = models.IntegerField(default=100, verbose_name='积分')
    level = models.IntegerField(default=1, verbose_name='等级')
    
    # 下载限制
    daily_downloads = models.IntegerField(default=0, verbose_name='今日下载次数')
    last_download_date = models.DateField(null=True, blank=True, verbose_name='最后下载日期')
    
    # 签到系统
    last_signin_date = models.DateField(null=True, blank=True, verbose_name='最后签到日期')
    consecutive_signin_days = models.IntegerField(default=0, verbose_name='连续签到天数')
    
    # 用户状态
    is_verified = models.BooleanField(default=False, verbose_name='是否验证')
    verification_code = models.CharField(max_length=6, blank=True, verbose_name='验证码')
    verification_code_expires = models.DateTimeField(null=True, blank=True, verbose_name='验证码过期时间')
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['nickname']
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'accounts_user'
    
    def __str__(self):
        return f"{self.nickname}({self.phone})"
    
    @property
    def level_name(self):
        """等级名称"""
        level_names = {
            1: '新手',
            2: '初级',
            3: '中级',
            4: '高级',
            5: '专家'
        }
        return level_names.get(self.level, '未知')
    
    def can_download_today(self):
        """检查今日是否还能下载"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_download_date != today:
            return True
        
        # 根据等级确定每日下载限制
        daily_limits = {1: 5, 2: 10, 3: 15, 4: 20, 5: 30}
        limit = daily_limits.get(self.level, 5)
        
        return self.daily_downloads < limit
    
    def update_level(self):
        """根据积分更新等级"""
        level_thresholds = {
            1: 0,
            2: 500,
            3: 1500,
            4: 3000,
            5: 6000
        }
        
        for level, threshold in sorted(level_thresholds.items(), reverse=True):
            if self.points >= threshold:
                self.level = level
                break
        
        self.save(update_fields=['level'])

class UserProfile(TimeStampedModel):
    """用户扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    school = models.CharField(max_length=100, blank=True, verbose_name='学校')
    grade_class = models.CharField(max_length=20, blank=True, verbose_name='班级')
    subjects_interested = models.JSONField(default=list, verbose_name='感兴趣的科目')
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
        db_table = 'accounts_user_profile'
```

### 2. 序列化器 (apps/accounts/serializers.py)
```python
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['phone', 'nickname', 'password', 'password_confirm', 'city', 'child_grade']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次输入的密码不一致")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=validated_data['phone'],  # Django内部需要
            password=password,
            **validated_data
        )
        
        # 创建用户资料
        UserProfile.objects.create(user=user)
        
        return user

class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    phone = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        
        if phone and password:
            user = authenticate(username=phone, password=password)
            
            if not user:
                raise serializers.ValidationError('手机号或密码错误')
            
            if not user.is_active:
                raise serializers.ValidationError('账户已被禁用')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('必须提供手机号和密码')

class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    level_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'nickname', 'avatar', 'city', 'child_grade',
            'points', 'level', 'level_name', 'daily_downloads',
            'consecutive_signin_days', 'date_joined'
        ]
        read_only_fields = ['id', 'phone', 'points', 'level', 'daily_downloads', 'date_joined']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """用户资料更新序列化器"""
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['nickname', 'avatar', 'city', 'child_grade', 'profile']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return {
                'bio': obj.profile.bio,
                'school': obj.profile.school,
                'grade_class': obj.profile.grade_class,
                'subjects_interested': obj.profile.subjects_interested
            }
        return {}
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # 更新用户基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新用户资料
        if profile_data and hasattr(instance, 'profile'):
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance
```

### 3. 视图集 (apps/accounts/views.py)
```python
from rest_framework import status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth import login
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer
)
from apps.points.services import PointService

class AuthViewSet(GenericViewSet):
    """认证视图集"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """用户注册"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 注册奖励积分
            PointService.add_points(
                user=user,
                points=100,
                transaction_type='register',
                description='注册奖励'
            )
            
            # 生成JWT token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'code': 201,
                'message': '注册成功',
                'data': {
                    'user': UserProfileSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '注册失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """用户登录"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # 更新最后登录时间
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # 生成JWT token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'code': 200,
                'message': '登录成功',
                'data': {
                    'user': UserProfileSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                }
            })
        
        return Response({
            'code': 400,
            'message': '登录失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """用户登出"""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'code': 200,
                'message': '登出成功'
            })
        except Exception as e:
            return Response({
                'code': 400,
                'message': '登出失败',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """获取当前用户信息"""
        serializer = UserProfileSerializer(request.user)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        """更新用户资料"""
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': UserProfileSerializer(request.user).data
            })
        
        return Response({
            'code': 400,
            'message': '更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def signin(self, request):
        """用户签到"""
        user = request.user
        today = timezone.now().date()
        
        # 检查今日是否已签到
        if user.last_signin_date == today:
            return Response({
                'code': 400,
                'message': '今日已签到'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 计算连续签到天数
        if user.last_signin_date and (today - user.last_signin_date).days == 1:
            user.consecutive_signin_days += 1
        else:
            user.consecutive_signin_days = 1
        
        user.last_signin_date = today
        user.save(update_fields=['last_signin_date', 'consecutive_signin_days'])
        
        # 签到奖励积分（连续签到有额外奖励）
        base_points = 5
        bonus_points = min(user.consecutive_signin_days - 1, 10)  # 最多额外10积分
        total_points = base_points + bonus_points
        
        PointService.add_points(
            user=user,
            points=total_points,
            transaction_type='signin',
            description=f'签到奖励（连续{user.consecutive_signin_days}天）'
        )
        
        return Response({
            'code': 200,
            'message': '签到成功',
            'data': {
                'points_earned': total_points,
                'consecutive_days': user.consecutive_signin_days,
                'total_points': user.points
            }
        })

class UserViewSet(GenericViewSet):
    """用户管理视图集"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """获取用户公开资料"""
        user = self.get_object()
        serializer = self.get_serializer(user)
        
        # 只返回公开信息
        data = serializer.data
        public_fields = ['id', 'nickname', 'avatar', 'city', 'level', 'level_name', 'date_joined']
        public_data = {k: v for k, v in data.items() if k in public_fields}
        
        return Response({
            'code': 200,
            'message': 'success',
            'data': public_data
        })
```

### 4. URL配置 (apps/accounts/urls.py)
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
```

### 5. 管理后台配置 (apps/accounts/admin.py)
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'phone', 'nickname', 'city', 'child_grade', 
        'points', 'level', 'level_name', 'is_active', 'date_joined'
    ]
    list_filter = ['level', 'city', 'child_grade', 'is_active', 'date_joined']
    search_fields = ['phone', 'nickname', 'city']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('phone', 'password', 'nickname', 'avatar')
        }),
        ('个人信息', {
            'fields': ('city', 'child_grade', 'email')
        }),
        ('积分信息', {
            'fields': ('points', 'level', 'daily_downloads', 'last_download_date')
        }),
        ('签到信息', {
            'fields': ('last_signin_date', 'consecutive_signin_days')
        }),
        ('权限信息', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('重要日期', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        ('创建用户', {
            'classes': ('wide',),
            'fields': ('phone', 'nickname', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def level_name(self, obj):
        return obj.level_name
    level_name.short_description = '等级名称'
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" />', obj.avatar.url)
        return "无头像"
    avatar_preview.short_description = '头像预览'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'grade_class', 'created_at']
    list_filter = ['school', 'grade_class', 'created_at']
    search_fields = ['user__nickname', 'user__phone', 'school']
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user',)
        }),
        ('学校信息', {
            'fields': ('school', 'grade_class')
        }),
        ('个人信息', {
            'fields': ('bio', 'subjects_interested')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
```

## 📚 资源管理模块 (apps/resources)

### 1. 资源模型 (apps/resources/models.py)
```python
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.conf import settings
from apps.common.models import BaseModel
import os

User = get_user_model()

class Resource(BaseModel):
    """学习资源模型"""
    
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
        ('音乐', '音乐'),
        ('美术', '美术'),
        ('体育', '体育'),
    ]
    
    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_resources',
        verbose_name='上传者'
    )
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    
    # 文件信息
    file = models.FileField(
        upload_to='resources/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=settings.K12_SETTINGS['ALLOWED_FILE_TYPES'])],
        verbose_name='文件'
    )
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    file_type = models.CharField(max_length=10, verbose_name='文件类型')
    
    # 分类信息
    grade = models.CharField(max_length=50, blank=True, verbose_name='年级')
    subject = models.CharField(max_length=20, choices=SUBJECTS, blank=True, verbose_name='科目')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, verbose_name='资源类型')
    
    # 统计信息
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    
    # 状态信息
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')
    
    class Meta:
        verbose_name = '学习资源'
        verbose_name_plural = '学习资源'
        db_table = 'resources_resource'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['grade', 'subject']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def file_size_display(self):
        """文件大小显示"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def save(self, *args, **kwargs):
        if self.file:
            # 自动设置文件大小和类型
            self.file_size = self.file.size
            self.file_type = os.path.splitext(self.file.name)[1][1:].lower()
        super().save(*args, **kwargs)

class ResourceTag(models.Model):
    """资源标签"""
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='颜色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '资源标签'
        verbose_name_plural = '资源标签'
        db_table = 'resources_tag'
    
    def __str__(self):
        return self.name

class ResourceTagRelation(models.Model):
    """资源标签关系"""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(ResourceTag, on_delete=models.CASCADE, related_name='resources')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '资源标签关系'
        verbose_name_plural = '资源标签关系'
        db_table = 'resources_tag_relation'
        unique_together = ['resource', 'tag']

class ResourceComment(BaseModel):
    """资源评论"""
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='资源'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resource_comments',
        verbose_name='评论者'
    )
    content = models.TextField(verbose_name='评论内容')
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        null=True,
        blank=True,
        verbose_name='评分'
    )
    
    class Meta:
        verbose_name = '资源评论'
        verbose_name_plural = '资源评论'
        db_table = 'resources_comment'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.nickname} 评论 {self.resource.title}"
```

### 2. 资源序列化器 (apps/resources/serializers.py)
```python
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Resource, ResourceTag, ResourceComment

User = get_user_model()

class ResourceTagSerializer(serializers.ModelSerializer):
    """资源标签序列化器"""
    class Meta:
        model = ResourceTag
        fields = ['id', 'name', 'color']

class ResourceListSerializer(serializers.ModelSerializer):
    """资源列表序列化器"""
    uploader_name = serializers.CharField(source='uploader.nickname', read_only=True)
    file_size_display = serializers.ReadOnlyField()
    tags = ResourceTagSerializer(many=True, read_only=True)

    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'description', 'grade', 'subject', 'resource_type',
            'file_type', 'file_size_display', 'download_count', 'view_count',
            'uploader_name', 'tags', 'is_featured', 'created_at'
        ]

class ResourceDetailSerializer(serializers.ModelSerializer):
    """资源详情序列化器"""
    uploader_name = serializers.CharField(source='uploader.nickname', read_only=True)
    uploader_id = serializers.IntegerField(source='uploader.id', read_only=True)
    file_size_display = serializers.ReadOnlyField()
    tags = ResourceTagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'description', 'grade', 'subject', 'resource_type',
            'file', 'file_type', 'file_size_display', 'download_count', 'view_count',
            'uploader_name', 'uploader_id', 'tags', 'comments_count', 'average_rating',
            'is_featured', 'created_at', 'updated_at'
        ]

    def get_comments_count(self, obj):
        return obj.comments.filter(is_deleted=False).count()

    def get_average_rating(self, obj):
        comments = obj.comments.filter(is_deleted=False, rating__isnull=False)
        if comments.exists():
            return round(comments.aggregate(avg=models.Avg('rating'))['avg'], 1)
        return None

class ResourceCreateSerializer(serializers.ModelSerializer):
    """资源创建序列化器"""
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Resource
        fields = [
            'title', 'description', 'grade', 'subject', 'resource_type',
            'file', 'tags'
        ]

    def validate_file(self, value):
        """验证文件"""
        from django.conf import settings

        # 检查文件大小
        if value.size > settings.K12_SETTINGS['MAX_FILE_SIZE']:
            raise serializers.ValidationError('文件大小超过限制')

        # 检查文件类型
        file_extension = value.name.split('.')[-1].lower()
        if file_extension not in settings.K12_SETTINGS['ALLOWED_FILE_TYPES']:
            raise serializers.ValidationError('不支持的文件类型')

        return value

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        validated_data['uploader'] = self.context['request'].user

        resource = Resource.objects.create(**validated_data)

        # 处理标签
        for tag_name in tags_data:
            tag, created = ResourceTag.objects.get_or_create(name=tag_name)
            resource.tags.create(tag=tag)

        return resource

class ResourceCommentSerializer(serializers.ModelSerializer):
    """资源评论序列化器"""
    user_name = serializers.CharField(source='user.nickname', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)

    class Meta:
        model = ResourceComment
        fields = [
            'id', 'content', 'rating', 'user_name', 'user_avatar',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['resource_id'] = self.context['resource_id']
        return super().create(validated_data)
```

### 3. 资源视图集 (apps/resources/views.py)
```python
from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
from django.utils import timezone
from .models import Resource, ResourceComment
from .serializers import (
    ResourceListSerializer,
    ResourceDetailSerializer,
    ResourceCreateSerializer,
    ResourceCommentSerializer
)
from .filters import ResourceFilter
from apps.common.permissions import IsOwnerOrReadOnly
from apps.points.services import PointService

class ResourceViewSet(viewsets.ModelViewSet):
    """资源管理视图集"""
    queryset = Resource.objects.filter(is_active=True, is_deleted=False)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ResourceFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'download_count', 'view_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ResourceCreateSerializer
        elif self.action == 'list':
            return ResourceListSerializer
        return ResourceDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """创建资源"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource = serializer.save()

        # 上传奖励积分
        PointService.add_points(
            user=request.user,
            points=20,
            transaction_type='upload',
            description=f'上传资源：{resource.title}',
            related_resource=resource
        )

        return Response({
            'code': 201,
            'message': '资源上传成功',
            'data': ResourceDetailSerializer(resource).data
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """获取资源详情"""
        instance = self.get_object()

        # 增加查看次数
        Resource.objects.filter(id=instance.id).update(view_count=F('view_count') + 1)
        instance.refresh_from_db()

        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def download(self, request, pk=None):
        """下载资源"""
        resource = self.get_object()
        user = request.user

        # 检查是否是自己上传的资源
        if resource.uploader == user:
            return Response({
                'code': 400,
                'message': '不能下载自己上传的资源'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 检查今日下载次数
        if not user.can_download_today():
            return Response({
                'code': 400,
                'message': '今日下载次数已达上限'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 检查积分是否足够
        download_cost = 10
        if user.points < download_cost:
            return Response({
                'code': 400,
                'message': '积分不足'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 扣除积分
        PointService.deduct_points(
            user=user,
            points=download_cost,
            transaction_type='download',
            description=f'下载资源：{resource.title}',
            related_resource=resource
        )

        # 给上传者奖励积分
        PointService.add_points(
            user=resource.uploader,
            points=2,
            transaction_type='download_reward',
            description=f'资源被下载：{resource.title}',
            related_resource=resource
        )

        # 更新下载统计
        Resource.objects.filter(id=resource.id).update(download_count=F('download_count') + 1)

        # 更新用户下载统计
        today = timezone.now().date()
        if user.last_download_date != today:
            user.daily_downloads = 1
            user.last_download_date = today
        else:
            user.daily_downloads += 1
        user.save(update_fields=['daily_downloads', 'last_download_date'])

        # 记录下载记录
        from apps.downloads.models import DownloadRecord
        DownloadRecord.objects.create(
            user=user,
            resource=resource,
            points_cost=download_cost
        )

        return Response({
            'code': 200,
            'message': '下载成功',
            'data': {
                'download_url': resource.file.url,
                'points_remaining': user.points,
                'daily_downloads_remaining': user.can_download_today()
            }
        })

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """获取资源评论"""
        resource = self.get_object()
        comments = resource.comments.filter(is_deleted=False).order_by('-created_at')

        # 分页
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = ResourceCommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ResourceCommentSerializer(comments, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_comment(self, request, pk=None):
        """添加评论"""
        resource = self.get_object()

        # 检查是否已经评论过
        if resource.comments.filter(user=request.user, is_deleted=False).exists():
            return Response({
                'code': 400,
                'message': '您已经评论过这个资源了'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResourceCommentSerializer(
            data=request.data,
            context={'request': request, 'resource_id': resource.id}
        )

        if serializer.is_valid():
            comment = serializer.save()
            return Response({
                'code': 201,
                'message': '评论成功',
                'data': ResourceCommentSerializer(comment).data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'code': 400,
            'message': '评论失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """获取推荐资源"""
        featured_resources = self.get_queryset().filter(is_featured=True)[:10]
        serializer = ResourceListSerializer(featured_resources, many=True)

        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """获取热门资源"""
        popular_resources = self.get_queryset().order_by('-download_count', '-view_count')[:20]
        serializer = ResourceListSerializer(popular_resources, many=True)

        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })
```

## 🎯 积分系统模块 (apps/points)

### 1. 积分模型 (apps/points/models.py)
```python
from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import TimeStampedModel

User = get_user_model()

class PointTransaction(TimeStampedModel):
    """积分交易记录"""

    TRANSACTION_TYPES = [
        ('register', '注册奖励'),
        ('upload', '上传奖励'),
        ('download', '下载消耗'),
        ('signin', '签到奖励'),
        ('download_reward', '被下载奖励'),
        ('bounty_publish', '发布悬赏'),
        ('bounty_reward', '悬赏奖励'),
        ('admin_adjust', '管理员调整'),
        ('refund', '退款'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='point_transactions',
        verbose_name='用户'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        verbose_name='交易类型'
    )
    points_change = models.IntegerField(verbose_name='积分变化')
    points_before = models.IntegerField(verbose_name='交易前积分')
    points_after = models.IntegerField(verbose_name='交易后积分')

    # 关联对象
    related_resource = models.ForeignKey(
        'resources.Resource',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='相关资源'
    )
    related_bounty = models.ForeignKey(
        'bounties.Bounty',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='相关悬赏'
    )

    description = models.TextField(verbose_name='描述')

    class Meta:
        verbose_name = '积分交易'
        verbose_name_plural = '积分交易'
        db_table = 'points_transaction'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        return f"{self.user.nickname} {self.get_transaction_type_display()} {self.points_change}"

class PointRule(models.Model):
    """积分规则"""
    name = models.CharField(max_length=50, verbose_name='规则名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='规则代码')
    points = models.IntegerField(verbose_name='积分数量')
    description = models.TextField(blank=True, verbose_name='规则描述')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '积分规则'
        verbose_name_plural = '积分规则'
        db_table = 'points_rule'

    def __str__(self):
        return f"{self.name} ({self.points}积分)"
```

这个详细的Django应用实现包含了：

1. **用户认证模块的完整实现**：
   - 自定义用户模型（支持手机号登录）
   - 完整的序列化器（注册、登录、资料更新）
   - 功能丰富的视图集（认证、签到、资料管理）
   - Django Admin管理界面配置

2. **资源管理模块的详细实现**：
   - 资源模型（支持文件上传、标签、评论）
   - 多种序列化器（列表、详情、创建）
   - 功能完整的视图集（CRUD、下载、评论、推荐）

3. **积分系统模块的开始**：
   - 积分交易记录模型
   - 积分规则配置模型

接下来我可以继续完善：
- 积分系统的服务层和视图
- 悬赏系统模块
- 下载管理模块
- 通知系统模块
- 完整的测试用例
- 部署和运维脚本

您希望我继续哪个部分的实现？
