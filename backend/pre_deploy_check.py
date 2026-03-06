#!/usr/bin/env python3
"""
部署前环境检查脚本
检查所有必要的配置和依赖
"""
import os
import sys
import subprocess
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(msg):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{msg}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def check_python_version():
    """检查Python版本"""
    print_header("检查 Python 版本")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print_warning("需要 Python 3.9 或更高版本")
        return False

def check_env_variables():
    """检查环境变量"""
    print_header("检查环境变量")

    required_vars = {
        'development': ['DEBUG', 'DJANGO_SECRET_KEY'],
        'production': ['DEBUG', 'DJANGO_SECRET_KEY', 'RABBITMQ_ENCRYPTION_KEY']
    }

    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    env_type = 'development' if debug else 'production'

    print(f"环境类型: {env_type}")
    print()

    all_set = True
    for var in required_vars[env_type]:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if 'KEY' in var or 'PASSWORD' in var:
                display_value = value[:10] + '...' if len(value) > 10 else '***'
            else:
                display_value = value
            print_success(f"{var}: {display_value}")
        else:
            print_error(f"{var}: 未设置")
            all_set = False

    return all_set

def check_redis():
    """检查Redis连接"""
    print_header("检查 Redis 连接")
    try:
        import redis
        redis_host = os.getenv('REDIS_HOST', '127.0.0.1')
        redis_port = int(os.getenv('REDIS_PORT', 6379))

        r = redis.Redis(host=redis_host, port=redis_port)
        r.ping()
        print_success(f"Redis连接成功: {redis_host}:{redis_port}")
        return True
    except ImportError:
        print_error("Redis库未安装")
        print_warning("运行: pip install redis")
        return False
    except Exception as e:
        print_error(f"Redis连接失败: {str(e)}")
        print_warning("请确保Redis服务已启动")
        return False

def check_rabbitmq():
    """检查RabbitMQ连接"""
    print_header("检查 RabbitMQ 连接")
    try:
        import pika
        rabbitmq_host = os.getenv('RABBITMQ_HOST', '127.0.0.1')
        rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
        rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
        rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')

        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        parameters = pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        connection.close()
        print_success(f"RabbitMQ连接成功: {rabbitmq_host}:{rabbitmq_port}")
        return True
    except ImportError:
        print_error("pika库未安装")
        print_warning("运行: pip install pika")
        return False
    except Exception as e:
        print_error(f"RabbitMQ连接失败: {str(e)}")
        print_warning("请确保RabbitMQ服务已启动")
        return False

def check_database():
    """检查数据库"""
    print_header("检查数据库")
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()

        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        print_success("数据库连接成功")
        return True
    except Exception as e:
        print_error(f"数据库连接失败: {str(e)}")
        return False

def check_dependencies():
    """检查Python依赖"""
    print_header("检查Python依赖")

    required_packages = [
        'django',
        'djangorestframework',
        'channels',
        'channels_redis',
        'cryptography',
        'pika',
        'redis',
    ]

    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} 已安装")
        except ImportError:
            print_error(f"{package} 未安装")
            all_installed = False

    return all_installed

def check_migration():
    """检查数据库迁移"""
    print_header("检查数据库迁移")
    try:
        result = subprocess.run(
            ['python3', 'manage.py', 'showmigrations'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # 检查是否有未应用的迁移
            if '[X]' in result.stdout:
                print_success("数据库迁移已应用")
                return True
            else:
                print_warning("数据库迁移未应用")
                print_warning("运行: python manage.py migrate")
                return False
        else:
            print_error(f"检查迁移失败: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"检查迁移异常: {str(e)}")
        return False

def main():
    """主函数"""
    print(f"\n{Colors.BLUE}自动化测试平台 - 部署前检查{Colors.RESET}\n")

    # 切换到backend目录
    backend_dir = Path(__file__).parent / 'backend'
    if backend_dir.exists():
        os.chdir(backend_dir)
        print(f"工作目录: {os.getcwd()}\n")

    checks = [
        ("Python版本", check_python_version),
        ("环境变量", check_env_variables),
        ("Python依赖", check_dependencies),
        ("Redis连接", check_redis),
        ("RabbitMQ连接", check_rabbitmq),
        ("数据库连接", check_database),
        ("数据库迁移", check_migration),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"{name}检查异常: {str(e)}")
            results[name] = False

    # 总结
    print_header("检查总结")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        if result:
            print_success(f"{name}: 通过")
        else:
            print_error(f"{name}: 失败")

    print(f"\n总计: {passed}/{total} 项检查通过\n")

    if passed == total:
        print_success("所有检查通过！可以开始部署。")
        return 0
    else:
        print_error("部分检查未通过，请修复后再部署。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
