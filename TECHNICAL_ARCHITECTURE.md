# K12家校学习资料共享平台 - 技术架构

## 🏗️ 整体架构

本项目采用**前后端分离**的现代Web应用架构，基于**FastAPI + SQLite + Vue.js**技术栈构建。

```
┌─────────────────────────────────────────────────────────────┐
│                    前端层 (Frontend)                        │
├─────────────────────────────────────────────────────────────┤
│  Vue.js 3 + Element Plus + Axios                          │
│  • 用户界面 (index.html)                                   │
│  • 管理后台 (admin.html)                                   │
│  • 响应式设计 + 组件化开发                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                         HTTP/HTTPS
                              │
┌─────────────────────────────────────────────────────────────┐
│                    API网关层 (API Gateway)                  │
├─────────────────────────────────────────────────────────────┤
│  FastAPI + Uvicorn                                        │
│  • RESTful API设计                                         │
│  • 自动API文档生成                                         │
│  • 请求验证 + 响应序列化                                    │
│  • CORS跨域处理                                           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    业务逻辑层 (Business Logic)              │
├─────────────────────────────────────────────────────────────┤
│  • 用户认证与授权 (JWT)                                     │
│  • 资源管理 (上传/下载/搜索)                                │
│  • 积分系统 (获取/消耗/等级)                                │
│  • 悬赏系统 (发布/响应/结算)                                │
│  • 文件处理 (验证/存储/访问)                                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    数据访问层 (Data Access)                 │
├─────────────────────────────────────────────────────────────┤
│  SQLAlchemy ORM + Async Support                           │
│  • 模型定义 (Models)                                       │
│  • 数据验证 (Schemas)                                      │
│  • CRUD操作 (Create/Read/Update/Delete)                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    数据存储层 (Data Storage)                │
├─────────────────────────────────────────────────────────────┤
│  SQLite数据库 + 文件系统                                    │
│  • 关系型数据存储                                          │
│  • 文件上传存储                                            │
│  • 数据持久化                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ 技术栈详解

### **后端技术栈**

| 技术 | 版本 | 用途 | 特点 |
|------|------|------|------|
| **FastAPI** | 0.104.1 | Web框架 | 高性能、自动文档、类型提示 |
| **Uvicorn** | 0.24.0 | ASGI服务器 | 异步支持、高并发 |
| **SQLAlchemy** | 2.0.23 | ORM框架 | 异步支持、类型安全 |
| **SQLite** | - | 数据库 | 轻量级、零配置、适合中小型应用 |
| **Pydantic** | 2.5.0 | 数据验证 | 类型验证、序列化/反序列化 |
| **JWT** | 3.3.0 | 身份认证 | 无状态认证、安全可靠 |
| **Passlib** | 1.7.4 | 密码加密 | BCrypt加密、安全存储 |
| **Aiofiles** | 23.2.1 | 异步文件操作 | 高性能文件处理 |

### **前端技术栈**

| 技术 | 版本 | 用途 | 特点 |
|------|------|------|------|
| **Vue.js** | 3.x | 前端框架 | 响应式、组件化、易学易用 |
| **Element Plus** | - | UI组件库 | 丰富组件、美观界面 |
| **Axios** | - | HTTP客户端 | Promise支持、请求拦截 |
| **JavaScript ES6+** | - | 编程语言 | 现代语法、异步支持 |

## 📁 项目结构

```
k12_share_platform/
├── app/                          # 后端应用目录
│   ├── api/                      # API路由层
│   │   └── v1/                   # API版本1
│   │       ├── auth.py           # 认证相关API
│   │       ├── users.py          # 用户管理API
│   │       ├── resources.py      # 资源管理API
│   │       ├── downloads.py      # 下载管理API
│   │       ├── bounties.py       # 悬赏系统API
│   │       ├── search.py         # 搜索功能API
│   │       └── admin.py          # 管理员API
│   ├── core/                     # 核心配置
│   │   ├── config.py             # 应用配置
│   │   ├── database.py           # 数据库配置
│   │   ├── security.py           # 安全认证
│   │   └── admin_auth.py         # 管理员认证
│   ├── models/                   # 数据模型
│   │   ├── user.py               # 用户模型
│   │   ├── resource.py           # 资源模型
│   │   ├── bounty.py             # 悬赏模型
│   │   ├── report.py             # 举报模型
│   │   └── admin.py              # 管理员模型
│   ├── schemas/                  # 数据验证模式
│   │   ├── auth.py               # 认证相关Schema
│   │   ├── user.py               # 用户Schema
│   │   ├── resource.py           # 资源Schema
│   │   ├── bounty.py             # 悬赏Schema
│   │   └── admin.py              # 管理员Schema
│   ├── services/                 # 业务服务层
│   │   ├── file_service.py       # 文件处理服务
│   │   ├── point_service.py      # 积分系统服务
│   │   ├── grade_service.py      # 年级管理服务
│   │   └── sms_service.py        # 短信服务
│   ├── crud/                     # 数据访问层
│   │   └── user.py               # 用户CRUD操作
│   └── tasks/                    # 后台任务
│       └── grade_upgrade_task.py # 年级升级任务
├── static/                       # 前端静态文件
│   ├── index.html                # 用户主界面
│   ├── admin.html                # 管理员界面
│   └── js/                       # JavaScript文件
│       ├── app.js                # 主应用逻辑
│       └── admin.js              # 管理员逻辑
├── uploads/                      # 文件上传目录
│   ├── resources/                # 资源文件
│   └── avatars/                  # 用户头像
├── main.py                       # 应用入口
├── requirements.txt              # Python依赖
└── k12_share.db                  # SQLite数据库
```

## 🗄️ 数据库设计

### **核心数据表**

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    phone VARCHAR(11) UNIQUE,           -- 手机号（登录账号）
    password_hash VARCHAR(255),         -- 密码哈希
    nickname VARCHAR(50),               -- 昵称
    city VARCHAR(50),                   -- 城市
    child_grade VARCHAR(20),            -- 孩子年级
    points INTEGER DEFAULT 100,         -- 积分
    level INTEGER DEFAULT 1,            -- 等级
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 资源表
CREATE TABLE resources (
    id INTEGER PRIMARY KEY,
    uploader_id INTEGER,                -- 上传者ID
    title VARCHAR(200),                 -- 资源标题
    description TEXT,                   -- 资源描述
    file_name VARCHAR(255),             -- 文件名
    file_path VARCHAR(500),             -- 文件路径
    file_size INTEGER,                  -- 文件大小
    file_type VARCHAR(10),              -- 文件类型
    grade VARCHAR(50),                  -- 适用年级
    subject VARCHAR(20),                -- 科目
    resource_type VARCHAR(20),          -- 资源类型
    download_count INTEGER DEFAULT 0,   -- 下载次数
    is_active BOOLEAN DEFAULT TRUE,     -- 是否激活
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 积分交易表
CREATE TABLE point_transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,                    -- 用户ID
    transaction_type VARCHAR(20),       -- 交易类型
    points_change INTEGER,              -- 积分变化
    related_resource_id INTEGER,        -- 相关资源ID
    description TEXT,                   -- 描述
    created_at TIMESTAMP
);

-- 悬赏表
CREATE TABLE bounties (
    id INTEGER PRIMARY KEY,
    publisher_id INTEGER,              -- 发布者ID
    title VARCHAR(200),                -- 悬赏标题
    description TEXT,                  -- 悬赏描述
    points_reward INTEGER,             -- 悬赏积分
    grade VARCHAR(50),                 -- 年级要求
    subject VARCHAR(20),               -- 科目要求
    status VARCHAR(20) DEFAULT 'open', -- 状态
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## 🔐 安全架构

### **认证与授权**

```python
# JWT Token认证流程
1. 用户登录 → 验证手机号密码
2. 生成JWT Token → 包含用户ID、过期时间
3. 前端存储Token → localStorage
4. API请求携带Token → Authorization Header
5. 后端验证Token → 解析用户信息
6. 权限检查 → 基于用户角色
```

### **数据安全**

- **密码加密**：使用BCrypt进行密码哈希存储
- **SQL注入防护**：SQLAlchemy ORM参数化查询
- **文件上传安全**：文件类型验证、大小限制、路径检查
- **CORS配置**：跨域请求控制
- **输入验证**：Pydantic模型验证所有输入数据

## 🚀 性能优化

### **后端优化**

- **异步编程**：FastAPI + SQLAlchemy异步支持
- **数据库优化**：索引设计、查询优化
- **文件处理**：异步文件操作、流式传输
- **缓存策略**：静态文件缓存、API响应缓存

### **前端优化**

- **组件化设计**：Vue.js组件复用
- **懒加载**：按需加载资源
- **CDN加速**：静态资源CDN分发
- **压缩优化**：JavaScript/CSS压缩

## 🔄 API设计

### **RESTful API规范**

```
GET    /api/v1/resources/          # 获取资源列表
POST   /api/v1/resources/          # 上传资源
GET    /api/v1/resources/{id}      # 获取单个资源
PUT    /api/v1/resources/{id}      # 更新资源
DELETE /api/v1/resources/{id}      # 删除资源

GET    /api/v1/users/me            # 获取当前用户信息
PUT    /api/v1/users/me            # 更新用户信息

POST   /api/v1/auth/login          # 用户登录
POST   /api/v1/auth/register       # 用户注册
POST   /api/v1/auth/logout         # 用户登出
```

### **统一响应格式**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "size": 20
    }
}
```

## 📊 监控与日志

### **应用监控**

- **性能监控**：API响应时间、数据库查询性能
- **错误监控**：异常捕获、错误日志记录
- **用户行为**：操作日志、访问统计

### **日志系统**

```python
# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

## 🐳 部署架构

### **Docker容器化**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **部署选项**

1. **单机部署**：Docker + SQLite
2. **云服务部署**：阿里云/腾讯云 + PostgreSQL
3. **容器编排**：Docker Compose / Kubernetes

## 🔧 开发工具链

### **开发环境**

- **Python 3.11+**：现代Python特性支持
- **FastAPI CLI**：开发服务器、热重载
- **SQLite Browser**：数据库可视化管理
- **Postman/Insomnia**：API测试工具

### **代码质量**

- **类型提示**：Python Type Hints
- **代码格式化**：Black / autopep8
- **静态检查**：mypy / pylint
- **测试框架**：pytest + pytest-asyncio

## 📈 扩展性设计

### **水平扩展**

- **数据库分离**：SQLite → PostgreSQL/MySQL
- **文件存储**：本地存储 → 对象存储(OSS/S3)
- **缓存层**：Redis缓存、会话存储
- **消息队列**：Celery + Redis异步任务

### **功能扩展**

- **微服务架构**：按业务域拆分服务
- **API网关**：统一入口、限流熔断
- **搜索引擎**：Elasticsearch全文搜索
- **实时通信**：WebSocket消息推送

这个技术架构设计兼顾了**开发效率**、**性能表现**和**扩展能力**，为K12教育资源共享平台提供了坚实的技术基础。
