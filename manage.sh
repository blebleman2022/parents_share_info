#!/bin/bash

# K12 家校资料共享平台管理脚本
PROJECT_NAME="K12 Platform"
CONTAINER_NAME="k12-platform"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查Docker是否运行
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_message $RED "❌ Docker未运行，请先启动Docker服务"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "K12 家校资料共享平台管理脚本"
    echo ""
    echo "使用方法: $0 {命令}"
    echo ""
    echo "可用命令:"
    echo "  start      - 启动应用"
    echo "  stop       - 停止应用"
    echo "  restart    - 重启应用"
    echo "  rebuild    - 重新构建并启动应用"
    echo "  logs       - 查看应用日志"
    echo "  status     - 查看应用状态"
    echo "  update     - 更新代码并重新部署"
    echo "  backup     - 创建数据备份"
    echo "  clean      - 清理Docker资源"
    echo "  shell      - 进入容器shell"
    echo "  db         - 数据库操作"
    echo "  help       - 显示此帮助信息"
}

# 启动应用
start_app() {
    print_message $BLUE "🚀 启动 $PROJECT_NAME..."
    check_docker
    
    if docker compose up -d; then
        print_message $GREEN "✅ $PROJECT_NAME 启动成功"
        print_message $YELLOW "📱 访问地址: http://localhost:8000"
        print_message $YELLOW "📚 API文档: http://localhost:8000/docs"
    else
        print_message $RED "❌ $PROJECT_NAME 启动失败"
        exit 1
    fi
}

# 停止应用
stop_app() {
    print_message $BLUE "🛑 停止 $PROJECT_NAME..."
    check_docker
    
    if docker compose down; then
        print_message $GREEN "✅ $PROJECT_NAME 已停止"
    else
        print_message $RED "❌ 停止失败"
        exit 1
    fi
}

# 重启应用
restart_app() {
    print_message $BLUE "🔄 重启 $PROJECT_NAME..."
    stop_app
    start_app
}

# 重新构建应用
rebuild_app() {
    print_message $BLUE "🔨 重新构建 $PROJECT_NAME..."
    check_docker
    
    print_message $YELLOW "停止现有容器..."
    docker compose down
    
    print_message $YELLOW "重新构建镜像..."
    if docker compose build --no-cache; then
        print_message $YELLOW "启动新容器..."
        start_app
    else
        print_message $RED "❌ 构建失败"
        exit 1
    fi
}

# 查看日志
show_logs() {
    print_message $BLUE "📋 查看 $PROJECT_NAME 日志..."
    check_docker
    docker compose logs -f app
}

# 查看状态
show_status() {
    print_message $BLUE "📊 $PROJECT_NAME 状态:"
    check_docker
    
    echo ""
    echo "=== 容器状态 ==="
    docker compose ps
    
    echo ""
    echo "=== 资源使用情况 ==="
    docker stats --no-stream $CONTAINER_NAME 2>/dev/null || echo "容器未运行"
    
    echo ""
    echo "=== 健康检查 ==="
    if curl -s -f http://localhost:8000/docs >/dev/null; then
        print_message $GREEN "✅ 应用健康状态: 正常"
    else
        print_message $RED "❌ 应用健康状态: 异常"
    fi
}

# 更新应用
update_app() {
    print_message $BLUE "⬆️ 更新 $PROJECT_NAME..."
    
    print_message $YELLOW "拉取最新代码..."
    git pull
    
    print_message $YELLOW "重新构建并启动..."
    rebuild_app
    
    print_message $GREEN "✅ 更新完成"
}

# 创建备份
create_backup() {
    print_message $BLUE "💾 创建备份..."
    
    # 创建备份目录
    mkdir -p backups
    
    # 生成时间戳
    timestamp=$(date +%Y%m%d_%H%M%S)
    
    # 备份数据库
    if [ -f "k12_share.db" ]; then
        cp k12_share.db "backups/k12_share_${timestamp}.db"
        print_message $GREEN "✅ 数据库备份: backups/k12_share_${timestamp}.db"
    fi
    
    # 备份上传文件
    if [ -d "uploads" ]; then
        tar -czf "backups/uploads_${timestamp}.tar.gz" uploads/
        print_message $GREEN "✅ 文件备份: backups/uploads_${timestamp}.tar.gz"
    fi
    
    # 清理旧备份（保留最近7天）
    find backups/ -name "*.db" -mtime +7 -delete 2>/dev/null
    find backups/ -name "*.tar.gz" -mtime +7 -delete 2>/dev/null
    
    print_message $GREEN "✅ 备份完成"
}

# 清理Docker资源
clean_docker() {
    print_message $BLUE "🧹 清理Docker资源..."
    check_docker
    
    print_message $YELLOW "停止容器..."
    docker compose down
    
    print_message $YELLOW "清理未使用的镜像和容器..."
    docker system prune -f
    
    print_message $YELLOW "清理未使用的卷..."
    docker volume prune -f
    
    print_message $GREEN "✅ 清理完成"
}

# 进入容器shell
enter_shell() {
    print_message $BLUE "🐚 进入容器shell..."
    check_docker
    
    if docker compose exec app bash; then
        print_message $GREEN "✅ 已退出容器shell"
    else
        print_message $RED "❌ 无法进入容器，请检查容器是否运行"
    fi
}

# 数据库操作
db_operations() {
    print_message $BLUE "🗄️ 数据库操作..."
    check_docker
    
    echo "选择操作:"
    echo "1. 查看数据库信息"
    echo "2. 进入SQLite命令行"
    echo "3. 导出数据库"
    echo "4. 返回主菜单"
    
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1)
            print_message $YELLOW "数据库信息:"
            docker compose exec app sqlite3 k12_share.db ".tables"
            ;;
        2)
            print_message $YELLOW "进入SQLite命令行 (输入.quit退出):"
            docker compose exec app sqlite3 k12_share.db
            ;;
        3)
            timestamp=$(date +%Y%m%d_%H%M%S)
            docker compose exec app sqlite3 k12_share.db ".dump" > "backups/db_export_${timestamp}.sql"
            print_message $GREEN "✅ 数据库已导出到: backups/db_export_${timestamp}.sql"
            ;;
        4)
            return
            ;;
        *)
            print_message $RED "❌ 无效选择"
            ;;
    esac
}

# 主程序
case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    rebuild)
        rebuild_app
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    update)
        update_app
        ;;
    backup)
        create_backup
        ;;
    clean)
        clean_docker
        ;;
    shell)
        enter_shell
        ;;
    db)
        db_operations
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_message $RED "❌ 未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
