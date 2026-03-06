#!/bin/bash
# 自动化测试平台 - 生产环境部署脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装"
        exit 1
    fi
}

# 主函数
main() {
    log_info "开始部署自动化测试平台..."
    echo "================================"

    # 1. 检查必要的命令
    log_info "检查必要的命令..."
    check_command python3
    check_command pip3
    check_command redis-cli
    log_success "所有必要命令已安装"

    # 2. 检查环境变量
    log_info "检查环境变量..."
    if [ -z "$DJANGO_SECRET_KEY" ]; then
        log_error "DJANGO_SECRET_KEY 未设置"
        exit 1
    fi

    if [ -z "$RABBITMQ_ENCRYPTION_KEY" ]; then
        log_error "RABBITMQ_ENCRYPTION_KEY 未设置"
        exit 1
    fi

    if [ "$DEBUG" = "True" ]; then
        log_warning "DEBUG模式已启用，不建议在生产环境使用"
    fi

    log_success "环境变量检查通过"

    # 3. 安装Python依赖
    log_info "安装Python依赖..."
    cd backend
    pip3 install -r requirements.txt
    log_success "Python依赖安装完成"

    # 4. 运行部署前检查
    log_info "运行部署前检查..."
    python3 pre_deploy_check.py
    if [ $? -ne 0 ]; then
        log_error "部署前检查失败"
        exit 1
    fi
    log_success "部署前检查通过"

    # 5. 数据库迁移
    log_info "运行数据库迁移..."
    python3 manage.py migrate --noinput
    log_success "数据库迁移完成"

    # 6. 加密现有RabbitMQ密码
    log_info "检查RabbitMQ密码加密..."
    python3 manage.py encrypt_rabbitmq_passwords --dry-run
    read -p "是否执行密码加密? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 manage.py encrypt_rabbitmq_passwords
        log_success "密码加密完成"
    else
        log_warning "跳过密码加密"
    fi

    # 7. 收集静态文件
    log_info "收集静态文件..."
    python3 manage.py collectstatic --noinput
    log_success "静态文件收集完成"

    # 8. 创建超级用户（可选）
    log_info "检查超级用户..."
    read -p "是否创建超级用户? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 manage.py createsuperuser
    fi

    # 9. 启动服务
    log_info "启动服务..."

    # 停止旧服务
    if pgrep -f "daphne.*core.asgi" > /dev/null; then
        log_info "停止旧服务..."
        pkill -f "daphne.*core.asgi" || true
        sleep 2
    fi

    # 启动新服务
    log_info "启动Daphne服务..."
    nohup daphne -b 0.0.0.0 -p 8000 core.asgi:application > logs/daphne.log 2>&1 &
    DAPHNE_PID=$!

    # 等待服务启动
    sleep 3

    # 检查服务是否启动成功
    if ps -p $DAPHNE_PID > /dev/null; then
        log_success "Daphne服务启动成功 (PID: $DAPHNE_PID)"
    else
        log_error "Daphne服务启动失败"
        tail -n 20 logs/daphne.log
        exit 1
    fi

    # 10. 健康检查
    log_info "运行健康检查..."
    sleep 2

    if curl -f http://localhost:8000/api/ > /dev/null 2>&1; then
        log_success "API健康检查通过"
    else
        log_warning "API健康检查失败，请检查日志"
    fi

    # 完成
    echo "================================"
    log_success "部署完成！"
    echo ""
    log_info "服务信息:"
    echo "  - API地址: http://localhost:8000/api/"
    echo "  - WebSocket: ws://localhost:8000/ws/"
    echo "  - 日志文件: logs/daphne.log"
    echo "  - 进程PID: $DAPHNE_PID"
    echo ""
    log_info "管理命令:"
    echo "  - 查看日志: tail -f logs/daphne.log"
    echo "  - 停止服务: pkill -f 'daphne.*core.asgi'"
    echo "  - 重启服务: ./deploy.sh"
    echo ""
    log_warning "建议:"
    echo "  - 配置Nginx反向代理"
    echo "  - 启用HTTPS"
    echo "  - 配置防火墙"
    echo "  - 设置日志轮转"
}

# 运行主函数
main
