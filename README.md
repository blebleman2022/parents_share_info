# K12家校学习资料共享平台

基于积分机制的K12学习资料共享平台，支持免审核发布、积分激励、悬赏求助等功能。

## 功能特性

### 核心约束
- ✅ **无金钱交易**：平台内所有交易均基于积分系统
- ✅ **纯积分机制**：用户通过贡献资源获得积分，消耗积分下载资源
- ✅ **免审核发布**：资源上传后立即可见，依靠用户举报维护秩序
- ✅ **不支持视频格式**：仅支持文档（PDF、DOC、PPT等）和图片格式

### 主要功能
- 📚 **资源管理**：上传、下载、搜索、分类浏览学习资料
- 🎯 **积分系统**：完整的积分获取、消耗、等级划分机制
- 💰 **悬赏求助**：发布悬赏寻找特定学习资源
- 🔍 **智能搜索**：支持关键词、年级、科目、类型等多维度搜索
- 🚨 **举报系统**：维护平台内容质量和秩序

## 技术架构

### 后端技术栈
- **框架**：FastAPI (Python)
- **数据库**：PostgreSQL + Redis
- **认证**：JWT Token
- **文件存储**：本地存储
- **API文档**：自动生成的OpenAPI文档

### 前端技术栈
- **框架**：Vue.js 3
- **UI组件**：Element Plus
- **HTTP客户端**：Axios
- **构建工具**：原生HTML/JS（简化部署）

## 快速开始

### 环境要求
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose（可选）

### 使用Docker Compose启动（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd parents_share_info
```

2. 启动服务
```bash
docker-compose up -d
```

3. 访问应用
- 前端界面：http://localhost:8000/static/index.html
- API文档：http://localhost:8000/docs

### 手动安装

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，配置数据库连接等信息
```

3. 初始化数据库
```bash
# 创建数据库
createdb k12_share

# 执行SQL脚本
psql -d k12_share -f database_design.sql
```

4. 启动应用
```bash
uvicorn main:app --reload
```

## 用户指南

### 积分系统规则

#### 积分获取
- 新用户注册：100积分
- 上传资源：20积分/个
- 每日签到：5积分
- 资源被下载：2积分/次（上传者获得）
- 完善个人信息：10积分（一次性）

#### 积分消耗
- 下载资源：10积分/个
- 发布悬赏：自定义积分数量（最低50积分）

#### 用户等级
- **新手用户**（0-499积分）：每日下载限制5个文件
- **活跃用户**（500-1999积分）：每日下载限制15个文件
- **资深用户**（2000-4999积分）：每日下载限制30个文件
- **专家用户**（5000+积分）：无下载限制

### 支持的文件格式
- **文档类型**：PDF、DOC、DOCX、PPT、PPTX、XLS、XLSX
- **图片类型**：JPG、JPEG、PNG
- **文件大小**：单个文件不超过50MB

### 资源分类
- **年级**：小学1-6年级、初中1-3年级、高中1-3年级
- **科目**：语文、数学、英语、物理、化学、生物、历史、地理、政治
- **类型**：试卷、教辅、课件、笔记、其他

## API文档

启动应用后，访问 http://localhost:8000/docs 查看完整的API文档。

### 主要API端点
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息
- `GET /api/v1/resources/` - 获取资源列表
- `POST /api/v1/resources/` - 上传资源
- `POST /api/v1/downloads/{resource_id}` - 下载资源
- `GET /api/v1/search/` - 搜索资源

## 开发指南

### 项目结构
```
├── app/                    # 应用主目录
│   ├── api/               # API路由
│   ├── core/              # 核心配置
│   ├── crud/              # 数据库操作
│   ├── models/            # 数据模型
│   ├── schemas/           # 数据传输对象
│   └── services/          # 业务逻辑服务
├── static/                # 静态文件（前端）
├── uploads/               # 文件上传目录
├── main.py               # 应用入口
├── requirements.txt      # Python依赖
└── database_design.sql   # 数据库设计
```

### 添加新功能
1. 在 `app/models/` 中定义数据模型
2. 在 `app/schemas/` 中定义数据传输对象
3. 在 `app/crud/` 中实现数据库操作
4. 在 `app/services/` 中实现业务逻辑
5. 在 `app/api/` 中创建API端点

## 部署指南

### 生产环境配置
1. 修改 `.env` 文件中的配置
2. 设置强密码和安全的SECRET_KEY
3. 配置反向代理（Nginx）
4. 设置HTTPS证书
5. 配置文件存储（建议使用云存储）

### 性能优化建议
- 使用Redis缓存热门资源
- 配置数据库连接池
- 启用Gzip压缩
- 使用CDN加速静态资源

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题或建议，请通过Issue联系我们。
