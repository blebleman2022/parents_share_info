# K12家校学习资料共享平台 - 部署指南

## 快速开始

### 方式一：使用Docker Compose（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd parents_share_info
```

2. **启动服务**
```bash
docker-compose up -d
```

3. **访问应用**
- 前端界面：http://localhost:8000/static/index.html
- API文档：http://localhost:8000/docs

### 方式二：本地开发环境

1. **环境要求**
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置数据库连接等信息
```

4. **初始化数据库**
```bash
# 创建数据库
createdb k12_share

# 初始化数据库表和配置
python init_db.py --with-test-data
```

5. **启动应用**
```bash
python start.py
```

## 生产环境部署

### 1. 服务器要求
- CPU: 2核心以上
- 内存: 4GB以上
- 存储: 50GB以上
- 操作系统: Ubuntu 20.04+ / CentOS 8+

### 2. 安装依赖服务

#### PostgreSQL
```bash
# Ubuntu
sudo apt update
sudo apt install postgresql postgresql-contrib

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE k12_share;
CREATE USER k12_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE k12_share TO k12_user;
\q
```

#### Redis
```bash
# Ubuntu
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### Nginx
```bash
# Ubuntu
sudo apt install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 3. 应用部署

#### 创建应用用户
```bash
sudo useradd -m -s /bin/bash k12app
sudo su - k12app
```

#### 部署应用代码
```bash
git clone <repository-url> /home/k12app/app
cd /home/k12app/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件
nano .env
```

示例生产环境配置：
```env
DATABASE_URL=postgresql://k12_user:your_password@localhost:5432/k12_share
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
UPLOAD_DIR=/home/k12app/uploads
```

#### 初始化数据库
```bash
python init_db.py
```

### 4. 配置系统服务

#### 创建Systemd服务文件
```bash
sudo nano /etc/systemd/system/k12-share.service
```

内容：
```ini
[Unit]
Description=K12 Share Platform
After=network.target

[Service]
Type=simple
User=k12app
WorkingDirectory=/home/k12app/app
Environment=PATH=/home/k12app/app/venv/bin
ExecStart=/home/k12app/app/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable k12-share
sudo systemctl start k12-share
sudo systemctl status k12-share
```

### 5. 配置Nginx反向代理

```bash
sudo nano /etc/nginx/sites-available/k12-share
```

内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /uploads/ {
        alias /home/k12app/uploads/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
    
    location /static/ {
        alias /home/k12app/app/static/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 启用站点
```bash
sudo ln -s /etc/nginx/sites-available/k12-share /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL证书配置（可选）

使用Let's Encrypt免费SSL证书：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 7. 日志和监控

#### 查看应用日志
```bash
sudo journalctl -u k12-share -f
```

#### 设置日志轮转
```bash
sudo nano /etc/logrotate.d/k12-share
```

内容：
```
/var/log/k12-share/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 k12app k12app
    postrotate
        systemctl reload k12-share
    endscript
}
```

## 维护和备份

### 数据库备份
```bash
# 创建备份
pg_dump -h localhost -U k12_user k12_share > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
psql -h localhost -U k12_user k12_share < backup_file.sql
```

### 文件备份
```bash
# 备份上传的文件
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz /home/k12app/uploads/
```

### 更新应用
```bash
sudo su - k12app
cd /home/k12app/app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart k12-share
```

## 性能优化

### 1. 数据库优化
- 定期执行VACUUM和ANALYZE
- 为常用查询字段添加索引
- 配置合适的连接池大小

### 2. 缓存优化
- 使用Redis缓存热门资源
- 配置适当的缓存过期时间
- 实现查询结果缓存

### 3. 文件存储优化
- 考虑使用对象存储服务（如AWS S3）
- 配置CDN加速静态资源
- 实现文件压缩和优化

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接字符串配置
   - 检查防火墙设置

2. **文件上传失败**
   - 检查上传目录权限
   - 验证文件大小限制
   - 检查磁盘空间

3. **服务启动失败**
   - 查看系统日志
   - 检查端口占用情况
   - 验证环境变量配置

### 监控指标
- 应用响应时间
- 数据库连接数
- 磁盘使用率
- 内存使用率
- 错误日志数量
