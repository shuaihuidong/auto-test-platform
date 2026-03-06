.PHONY: help install test lint format clean run

help: ## 显示帮助信息
	@echo '使用方法: make [目标]'
	@echo ''
	@echo '可用目标:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# 安装依赖
install: ## 安装项目依赖
	cd backend && pip install -r requirements.txt
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install

install-backend: ## 安装后端依赖
	cd backend && pip install -r requirements.txt
	cd backend && pip install -r requirements-dev.txt

install-frontend: ## 安装前端依赖
	cd frontend && npm install

# 测试
test: test-backend test-frontend ## 运行所有测试

test-backend: ## 运行后端测试
	cd backend && pytest

test-frontend: ## 运行前端测试
	cd frontend && npm run test

test-coverage: ## 运行测试并生成覆盖率报告
	cd backend && pytest --cov=apps --cov-report=html

# 代码检查
lint: lint-backend lint-frontend ## 运行代码检查

lint-backend: ## 检查后端代码
	cd backend && flake8 apps core --max-line-length=100 --exclude=migrations

lint-frontend: ## 检查前端代码
	cd frontend && npm run lint

# 代码格式化
format: format-backend format-frontend ## 格式化所有代码

format-backend: ## 格式化后端代码
	cd backend && black .
	cd backend && isort .

format-frontend: ## 格式化前端代码
	cd frontend && npm run format

# 清理
clean: ## 清理临时文件
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

# 运行服务
run-backend: ## 启动后端服务
	cd backend && daphne -b 0.0.0.0 -p 8000 core.asgi:application

run-frontend: ## 启动前端服务
	cd frontend && npm run dev

# 数据库
migrate: ## 运行数据库迁移
	cd backend && python manage.py makemigrations
	cd backend && python manage.py migrate

# Docker
docker-up: ## 启动Docker服务
	docker-compose up -d

docker-down: ## 停止Docker服务
	docker-compose down

docker-logs: ## 查看Docker日志
	docker-compose logs -f

# 其他
check: ## 检查项目配置
	cd backend && python manage.py check

shell: ## 进入Django shell
	cd backend && python manage.py shell

superuser: ## 创建超级用户
	cd backend && python manage.py createsuperuser
