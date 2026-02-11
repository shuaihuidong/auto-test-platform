"""
配置向导 - 首次运行时的引导配置界面
6个配置项：
1. 服务器地址
2. 执行机名称
3. 用户名/密码
4. 浏览器路径配置
5. 最大并发数
6. 日志保留天数
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QFileDialog, QWizard, QWizardPage,
    QFormLayout, QGroupBox, QMessageBox, QTextEdit, QRadioButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont

from config import get_config_manager, ExecutorConfig


class ServerConfigPage(QWizardPage):
    """第1页：服务器配置"""

    def __init__(self, config: ExecutorConfig):
        super().__init__()
        self.config = config
        self.setTitle("服务器配置")
        self.setSubTitle("请输入平台服务器的地址")

        layout = QFormLayout()

        # 服务器地址
        self.server_url_input = QLineEdit()
        self.server_url_input.setText(config.server_url)
        self.server_url_input.setPlaceholderText("http://127.0.0.1:8000")
        self.server_url_input.textChanged.connect(self.completeChanged)
        self.registerField("server_url", self.server_url_input)

        layout.addRow("服务器地址*:", self.server_url_input)

        # 说明文字
        help_label = QLabel(
            "\n提示：\n"
            "• 如果服务器在同一台电脑，使用 http://127.0.0.1:8000\n"
            "• 如果服务器在其他电脑，使用服务器的实际IP（如 http://192.168.1.100:8000）\n"
            "• 注意：使用 http:// 协议（新架构使用 HTTP API，不再使用 WebSocket）\n"
            "• 127.0.0.1 只能连接本机，无法连接其他电脑"
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addRow(help_label)

        self.setLayout(layout)

    def isComplete(self) -> bool:
        """检查页面是否完成（控制"下一步"按钮状态）"""
        url = self.server_url_input.text().strip()
        if not url:
            return False
        # 支持多种协议
        if not (url.startswith("http://") or url.startswith("https://") or
                url.startswith("ws://") or url.startswith("wss://")):
            return False
        return True

    def validatePage(self) -> bool:
        """验证页面"""
        url = self.server_url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "验证失败", "请输入服务器地址")
            return False

        # 支持多种协议
        if not (url.startswith("http://") or url.startswith("https://") or
                url.startswith("ws://") or url.startswith("wss://")):
            QMessageBox.warning(self, "验证失败", "服务器地址必须以 http://、https://、ws:// 或 wss:// 开头")
            return False

        self.config.server_url = url
        return True


class RabbitMQConfigPage(QWizardPage):
    """第2页：RabbitMQ 配置"""

    def __init__(self, config: ExecutorConfig):
        super().__init__()
        self.config = config
        self.setTitle("RabbitMQ 配置")
        self.setSubTitle("配置消息队列服务器地址")

        layout = QFormLayout()

        # RabbitMQ 主机地址
        self.rabbitmq_host_input = QLineEdit()
        self.rabbitmq_host_input.setText(config.rabbitmq_host)
        self.rabbitmq_host_input.setPlaceholderText("127.0.0.1（本机） 或 192.168.1.100（服务器IP）")
        self.rabbitmq_host_input.textChanged.connect(self.completeChanged)
        self.registerField("rabbitmq_host", self.rabbitmq_host_input)
        layout.addRow("RabbitMQ 地址*:", self.rabbitmq_host_input)

        # RabbitMQ 端口
        self.rabbitmq_port_input = QLineEdit()
        self.rabbitmq_port_input.setText(str(config.rabbitmq_port))
        self.rabbitmq_port_input.setPlaceholderText("5672")
        self.rabbitmq_port_input.textChanged.connect(self.completeChanged)
        self.registerField("rabbitmq_port", self.rabbitmq_port_input)
        layout.addRow("端口*:", self.rabbitmq_port_input)

        # 用户名
        self.rabbitmq_user_input = QLineEdit()
        self.rabbitmq_user_input.setText(config.rabbitmq_user)
        self.rabbitmq_user_input.setPlaceholderText("guest")
        self.rabbitmq_user_input.textChanged.connect(self.completeChanged)
        self.registerField("rabbitmq_user", self.rabbitmq_user_input)
        layout.addRow("用户名:", self.rabbitmq_user_input)

        # 密码
        self.rabbitmq_password_input = QLineEdit()
        self.rabbitmq_password_input.setText(config.rabbitmq_password)
        self.rabbitmq_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.rabbitmq_password_input.setPlaceholderText("guest")
        self.rabbitmq_password_input.textChanged.connect(self.completeChanged)
        self.registerField("rabbitmq_password", self.rabbitmq_password_input)
        layout.addRow("密码:", self.rabbitmq_password_input)

        # 说明文字
        help_label = QLabel(
            "\n提示：\n"
            "• 如果执行机和服务器在同一台电脑，使用默认值 127.0.0.1\n"
            "• 如果执行机和服务器在不同电脑，填写服务器的实际 IP 地址\n"
            "• RabbitMQ 运行在服务器上，执行机通过网络连接\n"
            "• 确保服务器防火墙允许访问 5672 端口"
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addRow(help_label)

        self.setLayout(layout)

    def isComplete(self) -> bool:
        """检查页面是否完成"""
        host = self.rabbitmq_host_input.text().strip()
        port = self.rabbitmq_port_input.text().strip()
        return bool(host and port)

    def validatePage(self) -> bool:
        """验证页面"""
        host = self.rabbitmq_host_input.text().strip()
        port = self.rabbitmq_port_input.text().strip()
        user = self.rabbitmq_user_input.text().strip()
        password = self.rabbitmq_password_input.text().strip()

        if not host or not port:
            QMessageBox.warning(self, "验证失败", "请填写 RabbitMQ 地址和端口")
            return False

        # 验证端口
        try:
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                QMessageBox.warning(self, "验证失败", "端口必须在 1-65535 之间")
                return False
        except ValueError:
            QMessageBox.warning(self, "验证失败", "端口必须是数字")
            return False

        self.config.rabbitmq_host = host
        self.config.rabbitmq_port = port_num
        self.config.rabbitmq_user = user or "guest"
        self.config.rabbitmq_password = password or "guest"
        return True


class ExecutorInfoPage(QWizardPage):
    """第2页：执行机信息"""

    def __init__(self, config: ExecutorConfig):
        super().__init__()
        self.config = config
        self.setTitle("执行机信息")
        self.setSubTitle("设置执行机的名称和身份")

        layout = QFormLayout()

        # 执行机名称
        self.name_input = QLineEdit()
        if config.executor_name:
            self.name_input.setText(config.executor_name)
        self.name_input.setPlaceholderText("例如：测试执行机-01")
        self.name_input.textChanged.connect(self.completeChanged)
        self.registerField("executor_name", self.name_input)
        layout.addRow("执行机名称*:", self.name_input)

        # UUID显示（只读）
        uuid_label = QLabel(f"执行机UUID: {config.executor_uuid}")
        uuid_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addRow(uuid_label)

        # 用户名
        self.username_input = QLineEdit()
        if config.owner_username:
            self.username_input.setText(config.owner_username)
        self.username_input.setPlaceholderText("平台登录用户名")
        self.username_input.textChanged.connect(self.completeChanged)
        self.registerField("username", self.username_input)
        layout.addRow("用户名*:", self.username_input)

        # 密码
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        if config.owner_password:
            self.password_input.setText(config.owner_password)
        self.password_input.setPlaceholderText("平台登录密码")
        self.password_input.textChanged.connect(self.completeChanged)
        self.registerField("password", self.password_input)
        layout.addRow("密码*:", self.password_input)

        self.setLayout(layout)

    def isComplete(self) -> bool:
        """检查页面是否完成（控制"下一步"按钮状态）"""
        name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        return bool(name and username and password)

    def validatePage(self) -> bool:
        """验证页面"""
        name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not name or not username or not password:
            QMessageBox.warning(self, "验证失败", "请填写所有必填项")
            return False

        self.config.executor_name = name
        self.config.owner_username = username
        self.config.owner_password = password
        return True


class BrowserConfigPage(QWizardPage):
    """第3页：浏览器配置"""

    def __init__(self, config: ExecutorConfig):
        super().__init__()
        self.config = config
        self.setTitle("浏览器配置")
        self.setSubTitle("配置浏览器和驱动路径（可留空，系统自动检测）")

        layout = QVBoxLayout()

        # 创建滚动区域的内容容器
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # 顶部说明（在滚动区域内）
        help_label = QLabel("如需使用特定版本的浏览器或驱动，请在此处配置。留空则系统自动检测和下载。")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 12px; padding: 8px; background: #f5f5f5; border-radius: 4px;")
        scroll_layout.addWidget(help_label)

        # Chrome 配置
        chrome_group = QGroupBox("Chrome 浏览器")
        chrome_layout = QFormLayout()

        self.chrome_path_input = QLineEdit()
        self.chrome_path_input.setText(config.chrome_path)
        self.chrome_path_input.setPlaceholderText(r"例如: C:\Program Files\Google\Chrome\Application\chrome.exe（留空自动检测）")
        chrome_layout.addRow("浏览器路径:", self.chrome_path_input)

        chrome_browse_btn = QPushButton("浏览...")
        chrome_browse_btn.setMaximumWidth(80)
        chrome_browse_btn.clicked.connect(lambda: self._browse_file(self.chrome_path_input, "Chrome可执行文件 (*.exe)"))
        chrome_layout.addRow("", chrome_browse_btn)

        self.chrome_driver_path_input = QLineEdit()
        self.chrome_driver_path_input.setText(config.chrome_driver_path)
        self.chrome_driver_path_input.setPlaceholderText("留空则自动下载对应版本的ChromeDriver")
        chrome_layout.addRow("驱动路径:", self.chrome_driver_path_input)

        chrome_driver_browse_btn = QPushButton("浏览...")
        chrome_driver_browse_btn.setMaximumWidth(80)
        chrome_driver_browse_btn.clicked.connect(lambda: self._browse_file(self.chrome_driver_path_input, "可执行文件 (*.exe)"))
        chrome_layout.addRow("", chrome_driver_browse_btn)

        chrome_group.setLayout(chrome_layout)
        scroll_layout.addWidget(chrome_group)

        # Firefox 配置
        firefox_group = QGroupBox("Firefox 浏览器")
        firefox_layout = QFormLayout()

        self.firefox_path_input = QLineEdit()
        self.firefox_path_input.setText(config.firefox_path)
        self.firefox_path_input.setPlaceholderText(r"例如: C:\Program Files\Mozilla Firefox\firefox.exe（留空自动检测）")
        firefox_layout.addRow("浏览器路径:", self.firefox_path_input)

        firefox_browse_btn = QPushButton("浏览...")
        firefox_browse_btn.setMaximumWidth(80)
        firefox_browse_btn.clicked.connect(lambda: self._browse_file(self.firefox_path_input, "Firefox可执行文件 (*.exe)"))
        firefox_layout.addRow("", firefox_browse_btn)

        self.firefox_driver_path_input = QLineEdit()
        self.firefox_driver_path_input.setText(config.firefox_driver_path)
        self.firefox_driver_path_input.setPlaceholderText("留空则自动下载对应版本的GeckoDriver")
        firefox_layout.addRow("驱动路径:", self.firefox_driver_path_input)

        firefox_driver_browse_btn = QPushButton("浏览...")
        firefox_driver_browse_btn.setMaximumWidth(80)
        firefox_driver_browse_btn.clicked.connect(lambda: self._browse_file(self.firefox_driver_path_input, "可执行文件 (*.exe)"))
        firefox_layout.addRow("", firefox_driver_browse_btn)

        firefox_group.setLayout(firefox_layout)
        scroll_layout.addWidget(firefox_group)

        # Edge 配置
        edge_group = QGroupBox("Edge 浏览器（Windows 自带）")
        edge_layout = QFormLayout()

        self.edge_driver_path_input = QLineEdit()
        self.edge_driver_path_input.setText(config.edge_driver_path)
        self.edge_driver_path_input.setPlaceholderText("留空则自动下载对应版本的EdgeDriver")
        edge_layout.addRow("驱动路径:", self.edge_driver_path_input)

        edge_driver_browse_btn = QPushButton("浏览...")
        edge_driver_browse_btn.setMaximumWidth(80)
        edge_driver_browse_btn.clicked.connect(lambda: self._browse_file(self.edge_driver_path_input, "可执行文件 (*.exe)"))
        edge_layout.addRow("", edge_driver_browse_btn)

        edge_group.setLayout(edge_layout)
        scroll_layout.addWidget(edge_group)

        # 添加弹性空间
        scroll_layout.addStretch()

        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(500)
        # 确保滚动条始终可见
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        layout.addWidget(scroll)
        self.setLayout(layout)

    def _browse_file(self, input_field: QLineEdit, file_filter: str):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", file_filter)
        if file_path:
            input_field.setText(file_path)

    def validatePage(self) -> bool:
        """验证页面"""
        self.config.chrome_path = self.chrome_path_input.text().strip()
        self.config.chrome_driver_path = self.chrome_driver_path_input.text().strip()
        self.config.firefox_path = self.firefox_path_input.text().strip()
        self.config.firefox_driver_path = self.firefox_driver_path_input.text().strip()
        self.config.edge_driver_path = self.edge_driver_path_input.text().strip()
        return True


class BrowserSelectPage(QWizardPage):
    """第3页：选择默认浏览器"""

    def __init__(self, config: ExecutorConfig):
        super().__init__()
        self.config = config
        self.setTitle("选择浏览器")
        self.setSubTitle("选择执行测试时使用的默认浏览器")

        layout = QVBoxLayout()

        # 说明
        help_label = QLabel("请选择执行测试脚本时使用的默认浏览器：")
        help_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(help_label)

        # 浏览器选择
        browser_group = QGroupBox("默认浏览器")
        browser_layout = QVBoxLayout()

        self.chrome_radio = QRadioButton("Chrome (推荐)")
        self.chrome_radio.setChecked(True)
        self.chrome_radio.setStyleSheet("font-size: 13px; padding: 5px;")
        browser_layout.addWidget(self.chrome_radio)

        self.firefox_radio = QRadioButton("Firefox")
        self.firefox_radio.setStyleSheet("font-size: 13px; padding: 5px;")
        browser_layout.addWidget(self.firefox_radio)

        self.edge_radio = QRadioButton("Microsoft Edge")
        self.edge_radio.setStyleSheet("font-size: 13px; padding: 5px;")
        browser_layout.addWidget(self.edge_radio)

        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)

        # 提示
        tip_label = QLabel(
            "\n提示：\n"
            "• Chrome: 最常用的浏览器，驱动自动下载\n"
            "• Firefox: 适合调试和开发\n"
            "• Edge: Windows 系统自带浏览器"
        )
        tip_label.setWordWrap(True)
        tip_label.setStyleSheet("color: #666; font-size: 12px; background: #f5f5f5; padding: 10px; border-radius: 5px;")
        layout.addWidget(tip_label)

        layout.addStretch()
        self.setLayout(layout)

        # 设置默认值
        if config.default_browser == "firefox":
            self.firefox_radio.setChecked(True)
        elif config.default_browser == "edge":
            self.edge_radio.setChecked(True)
        else:
            self.chrome_radio.setChecked(True)

    def validatePage(self) -> bool:
        """验证页面"""
        if self.chrome_radio.isChecked():
            self.config.default_browser = "chrome"
        elif self.firefox_radio.isChecked():
            self.config.default_browser = "firefox"
        elif self.edge_radio.isChecked():
            self.config.default_browser = "edge"
        else:
            self.config.default_browser = "chrome"
        return True


class AdvancedConfigPage(QWizardPage):
    """第4页：高级配置"""

    def __init__(self, config: ExecutorConfig):
        super().__init__()
        self.config = config
        self.setTitle("高级配置")
        self.setSubTitle("设置执行参数和日志配置")

        layout = QFormLayout()

        # 最大并发数
        self.max_concurrent_spin = QSpinBox()
        self.max_concurrent_spin.setRange(1, 10)
        self.max_concurrent_spin.setValue(config.max_concurrent)
        layout.addRow("最大并发任务数:", self.max_concurrent_spin)

        # 日志保留天数
        self.log_retention_spin = QSpinBox()
        self.log_retention_spin.setRange(1, 30)
        self.log_retention_spin.setValue(config.log_retention_days)
        layout.addRow("日志保留天数:", self.log_retention_spin)

        # 心跳间隔
        self.heartbeat_spin = QSpinBox()
        self.heartbeat_spin.setRange(10, 120)
        self.heartbeat_spin.setValue(config.heartbeat_interval)
        self.heartbeat_spin.setSuffix(" 秒")
        layout.addRow("心跳间隔:", self.heartbeat_spin)

        # 描述
        self.desc_input = QLineEdit()
        self.desc_input.setText(config.description)
        self.desc_input.setPlaceholderText("执行机描述信息（可选）")
        layout.addRow("描述:", self.desc_input)

        self.setLayout(layout)

    def validatePage(self) -> bool:
        """验证页面"""
        self.config.max_concurrent = self.max_concurrent_spin.value()
        self.config.log_retention_days = self.log_retention_spin.value()
        self.config.heartbeat_interval = self.heartbeat_spin.value()
        self.config.description = self.desc_input.text().strip()
        return True


class FinishPage(QWizardPage):
    """完成页"""

    def __init__(self, config: ExecutorConfig):
        super().__init__()
        self.config = config
        self.setTitle("配置完成")
        self.setSubTitle("确认配置信息")

        layout = QVBoxLayout()

        # 配置摘要
        summary = QTextEdit()
        summary.setReadOnly(True)
        summary.setMaximumHeight(300)
        summary.setHtml(self._generate_summary())
        layout.addWidget(summary)

        self.setLayout(layout)

    def _generate_summary(self) -> str:
        """生成配置摘要"""
        browser_names = {"chrome": "Chrome", "firefox": "Firefox", "edge": "Microsoft Edge"}
        browser_name = browser_names.get(self.config.default_browser, self.config.default_browser)

        return f"""
        <h3>配置摘要</h3>
        <table cellpadding="8">
        <tr><td><b>服务器地址:</b></td><td>{self.config.server_url}</td></tr>
        <tr><td><b>执行机名称:</b></td><td>{self.config.executor_name}</td></tr>
        <tr><td><b>执行机UUID:</b></td><td>{self.config.executor_uuid}</td></tr>
        <tr><td><b>用户名:</b></td><td>{self.config.owner_username}</td></tr>
        <tr><td><b>默认浏览器:</b></td><td>{browser_name}</td></tr>
        <tr><td><b>最大并发:</b></td><td>{self.config.max_concurrent}</td></tr>
        <tr><td><b>日志保留:</b></td><td>{self.config.log_retention_days} 天</td></tr>
        </table>
        <p><i>点击"完成"保存配置并启动执行机</i></p>
        """


class ConfigWizard(QWizard):
    """配置向导主类"""

    config_saved = pyqtSignal(object)  # 配置保存信号

    def __init__(self, config: ExecutorConfig):
        super().__init__()
        self.config = config
        self.setWindowTitle("执行机配置向导")
        self.setMinimumSize(650, 600)
        self.resize(700, 650)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        # 添加页面
        self.addPage(ServerConfigPage(config))
        self.addPage(RabbitMQConfigPage(config))
        self.addPage(ExecutorInfoPage(config))
        self.addPage(BrowserSelectPage(config))
        self.addPage(BrowserConfigPage(config))
        self.addPage(AdvancedConfigPage(config))
        self.addPage(FinishPage(config))

    def accept(self):
        """完成时保存配置"""
        # 保存配置
        config_manager = get_config_manager()
        config_manager.save(self.config)
        self.config_saved.emit(self.config)
        super().accept()
