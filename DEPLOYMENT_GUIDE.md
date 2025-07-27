# K12家校资料共享平台 - 部署指南

## 🚀 快速部署

### 方法1：Docker Compose 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/blebleman2022/parents_share_info.git
cd parents_share_info

# 2. 构建并启动
docker compose up -d

# 3. 访问应用
# 应用地址: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方法2：使用管理脚本

```bash
# 给脚本执行权限
chmod +x manage.sh

# 启动应用
./manage.sh start

# 查看状态
./manage.sh status

# 查看日志
./manage.sh logs

# 停止应用
./manage.sh stop
```

## 📋 系统要求

- **操作系统**: Linux (Ubuntu/CentOS/Debian) 或 Windows
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **内存**: 最少 2GB RAM
- **存储**: 最少 10GB 可用空间
- **端口**: 8000 (可配置)

## 🔧 环境配置

### 1. 安装Docker (Ubuntu/Debian)

```bash
# 更新系统
sudo apt update

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER
```

### 2. 安装Docker (CentOS/RHEL)

```bash
# 安装Docker
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 3. 配置镜像加速（中国大陆）

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF

sudo systemctl restart docker
```

## 🌐 Dokploy 部署（推荐生产环境）

### 1. 安装Dokploy

```bash
# 一键安装
curl -sSL https://dokploy.com/install.sh | sh
```

### 2. 配置项目

1. 访问 `http://your-server-ip:3000`
2. 创建新应用
3. 配置Git仓库: `https://github.com/blebleman2022/parents_share_info.git`
4. 设置构建配置:
   - Build Command: `docker build -t k12-platform .`
   - Start Command: `docker run -p 8000:8000 k12-platform`
   - Port: 8000

### 3. 环境变量配置

```env
PYTHONPATH=/app
TZ=Asia/Shanghai
ENVIRONMENT=production
SECRET_KEY=your-secret-key-here
```

## 📁 项目结构

```
parents_share_info/
├── app/                    # 应用核心代码
├── static/                 # 静态文件
├── uploads/                # 用户上传文件
├── logs/                   # 日志文件
├── Dockerfile              # Docker镜像配置
├── docker-compose.yml      # Docker编排配置
├── manage.sh              # 管理脚本
├── requirements.txt       # Python依赖
├── main.py               # 应用入口
└── k12_share.db          # SQLite数据库
```

## 🔒 安全配置

### 1. 防火墙设置

```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 2. SSL证书配置

```bash
# 使用Let's Encrypt
sudo apt install certbot
sudo certbot --nginx -d your-domain.com
```

### 3. 反向代理 (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 监控和维护

### 1. 查看应用状态

```bash
# 使用管理脚本
./manage.sh status

# 直接使用Docker
docker compose ps
docker stats
```

### 2. 查看日志

```bash
# 应用日志
./manage.sh logs

# 系统日志
docker compose logs -f
```

### 3. 备份数据

```bash
# 自动备份
./manage.sh backup

# 手动备份
cp k12_share.db backups/k12_share_$(date +%Y%m%d).db
tar -czf backups/uploads_$(date +%Y%m%d).tar.gz uploads/
```

### 4. 更新应用

```bash
# 使用管理脚本
./manage.sh update

# 手动更新
git pull
docker compose down
docker compose build --no-cache
docker compose up -d
```

## 🚨 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo netstat -tlnp | grep :8000
   sudo kill -9 <PID>
   ```

2. **Docker权限问题**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **内存不足**
   ```bash
   # 检查内存使用
   free -h
   docker stats
   ```

4. **磁盘空间不足**
   ```bash
   # 清理Docker资源
   docker system prune -f
   docker volume prune -f
   ```

### 日志分析

```bash
# 查看详细错误
docker compose logs app | grep ERROR

# 查看最近日志
docker compose logs app --tail 100

# 实时监控
docker compose logs -f app
```

## 📞 技术支持

- **项目地址**: https://github.com/blebleman2022/parents_share_info
- **问题反馈**: 在GitHub上提交Issue
- **文档更新**: 查看项目README.md

## 📝 更新日志

### v1.0.0 (2024-01-XX)
- ✅ 完整的Docker化部署
- ✅ 自动化管理脚本
- ✅ 数据备份功能
- ✅ 健康检查配置
- ✅ 生产环境优化
