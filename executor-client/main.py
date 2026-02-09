"""
执行机客户端主入口
- 检查配置状态
- 启动配置向导（首次运行）
- 启动主窗口
- 初始化日志系统
"""

import sys
from loguru import logger
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from config import get_config_manager
from gui.config_wizard import ConfigWizard
from gui.main_window import MainWindow


def setup_logging(config):
    """
    配置日志系统

    Args:
        config: ExecutorConfig 配置对象
    """
    from pathlib import Path

    try:
        # 日志目录
        log_dir = Path.home() / ".executor" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # 移除默认handler
        try:
            logger.remove()
        except:
            pass

        # 控制台输出（带颜色）- 只在有 stderr 时添加
        if sys.stderr is not None:
            try:
                logger.add(
                    sys.stderr,
                    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
                    level=config.log_level,
                    catch=True
                )
            except:
                pass

        # 文件输出（按天轮转）
        try:
            logger.add(
                str(log_dir / "executor_{time:YYYY-MM-DD}.log"),
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
                level=config.log_level,
                rotation="00:00",  # 每天0点轮转
                retention=f"{config.log_retention_days} days",  # 保留天数
                compression="zip",  # 压缩旧日志
                encoding="utf-8",
                catch=True
            )
        except Exception as e:
            # 如果文件日志失败，至少确保控制台日志可用
            print(f"文件日志配置失败: {e}")

    except Exception as e:
        # 如果日志配置完全失败，使用基本配置
        print(f"日志配置失败: {e}")


class ExecutorApplication:
    """执行机应用主类"""

    def __init__(self):
        self.app = None
        self.main_window = None
        self.config_manager = get_config_manager()

    def run(self):
        """启动应用"""
        # 创建 Qt 应用
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("AutoTest Executor")
        self.app.setOrganizationName("AutoTest Platform")

        # 配置日志
        config = self.config_manager.get()
        setup_logging(config)
        logger.info("执行机客户端启动中...")

        # 检查是否需要配置
        if not self.config_manager.is_configured():
            logger.info("首次运行，启动配置向导...")
            self.run_config_wizard()
        else:
            logger.info(f"加载配置: {config.executor_name}")
            self.run_main_window()

        # 运行事件循环
        sys.exit(self.app.exec())

    def run_config_wizard(self):
        """运行配置向导"""
        config = self.config_manager.get()

        wizard = ConfigWizard(config)
        wizard.config_saved.connect(self.on_config_saved)

        if wizard.exec():
            # 配置完成，启动主窗口
            logger.info("配置完成，启动执行机...")
            self.run_main_window()
        else:
            # 用户取消配置
            logger.warning("配置已取消，退出程序")
            sys.exit(0)

    def on_config_saved(self, config):
        """配置保存回调"""
        logger.info(f"配置已保存: {config.executor_name}")
        logger.info(f"服务器: {config.server_url}")
        logger.info(f"用户: {config.owner_username}")

    def run_main_window(self):
        """运行主窗口"""
        # 防止重复创建窗口
        if self.main_window is not None:
            logger.warning("主窗口已存在，跳过创建")
            return

        from gui.main_window import MainWindow

        # 创建主窗口
        self.main_window = MainWindow()

        # 显示窗口
        self.main_window.show()
        logger.info("主窗口已显示")

        # 自动连接（可选）
        # asyncio.create_task(self.ws_client.connect())


def main():
    """主入口函数"""
    application = ExecutorApplication()
    application.run()


if __name__ == "__main__":
    main()
