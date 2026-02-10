"""
执行机主窗口
- 显示连接状态
- 显示当前任务
- 显示日志输出
- 托盘图标控制
"""

import sys
from datetime import datetime
from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QSystemTrayIcon,
    QMenu, QApplication, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont, QAction, QColor

from config import get_config_manager
from task_manager_v2 import get_task_manager_v2
from utils.system import get_resource_usage


class LogWindow(QMainWindow):
    """日志窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("执行日志")
        self.setGeometry(100, 100, 800, 600)

        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))

        self.setCentralWidget(self.log_text)

    def append_log(self, message: str, level: str = "INFO"):
        """追加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = {
            "DEBUG": "#999",
            "INFO": "#333",
            "WARNING": "#f39c12",
            "ERROR": "#e74c3c"
        }.get(level, "#333")

        html = f'<span style="color: #666;">[{timestamp}]</span> <span style="color: {color}; font-weight: bold;">[{level}]</span> {message}<br>'
        self.log_text.append(html)

    def clear_logs(self):
        """清空日志"""
        self.log_text.clear()


class MainWindow(QMainWindow):
    """
    执行机主窗口

    显示执行机状态、当前任务、日志等
    """

    # 定义信号用于从子线程更新 UI
    update_connected_signal = pyqtSignal()
    update_disconnected_signal = pyqtSignal()
    show_error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = get_config_manager().get()
        self.task_manager = get_task_manager_v2()
        self.log_window = LogWindow()
        self.current_tasks = {}  # task_id -> task_info
        self.total_count = 0  # 总任务数
        self.success_count = 0  # 成功数
        self.fail_count = 0  # 失败数

        # 计划执行状态管理
        self.current_plans: Dict[str, Dict[str, Any]] = {}  # parent_execution_id -> plan_info

        # 注册任务完成回调
        self.task_manager.on_task_complete = self._on_task_complete

        # 连接信号
        self.update_connected_signal.connect(self._do_update_connected_ui)
        self.update_disconnected_signal.connect(self._do_update_disconnected_ui)
        self.show_error_signal.connect(lambda msg: QMessageBox.critical(self, "连接失败", msg))

        self.setup_ui()
        self.setup_signals()
        self.setup_tray()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(f"执行机 - {self.config.executor_name}")
        self.setMinimumSize(800, 600)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 顶部状态栏
        status_group = QGroupBox("执行机状态")
        status_layout = QHBoxLayout()

        self.status_label = QLabel("状态: 未连接")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #999;")
        status_layout.addWidget(self.status_label)

        self.executor_info_label = QLabel(f"UUID: {self.config.executor_uuid}")
        self.executor_info_label.setStyleSheet("color: #666;")
        status_layout.addWidget(self.executor_info_label)

        status_layout.addStretch()

        # 连接按钮
        self.connect_btn = QPushButton("连接服务器")
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        status_layout.addWidget(self.connect_btn)

        # 配置按钮
        config_btn = QPushButton("重新配置")
        config_btn.clicked.connect(self.reconfigure)
        status_layout.addWidget(config_btn)

        # 日志按钮
        log_btn = QPushButton("查看日志")
        log_btn.clicked.connect(self.show_log_window)
        status_layout.addWidget(log_btn)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # 任务列表（使用标签页）
        task_tab_widget = QTabWidget()

        # 当前任务标签页
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(4)
        self.task_table.setHorizontalHeaderLabels(["任务ID", "脚本名称", "状态", "开始时间"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.task_table.verticalHeader().setVisible(False)  # 隐藏行号列
        self.task_table.setRowCount(0)
        task_tab_widget.addTab(self.task_table, "当前任务")

        # 计划执行标签页
        self.plan_table = QTableWidget()
        self.plan_table.setColumnCount(5)
        self.plan_table.setHorizontalHeaderLabels(["序号", "脚本名称", "计划名称", "执行模式", "状态"])
        self.plan_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.plan_table.verticalHeader().setVisible(False)  # 隐藏行号列
        self.plan_table.setRowCount(0)
        task_tab_widget.addTab(self.plan_table, "计划执行")

        main_layout.addWidget(task_tab_widget, stretch=1)

        # 统计信息
        stats_group = QGroupBox("统计信息")
        stats_layout = QHBoxLayout()

        self.stats_label = QLabel(
            f"总任务数: 0 | 成功: 0 | 失败: 0 | "
            f"心跳: 正常 | CPU: 0% | 内存: 0%"
        )
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()

        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)

    def setup_signals(self):
        """设置信号连接"""
        # 任务管理器 V2 使用消息队列，不需要 WebSocket 事件
        # 使用定时器检查任务状态
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_task_status_from_manager)
        self.status_timer.start(1000)  # 每秒检查一次

    def setup_tray(self):
        """设置系统托盘"""
        # 创建托盘图标（使用应用图标）
        # 这里使用标准图标，实际应用中应该加载图标文件
        from PyQt6.QtWidgets import QStyle
        self.tray_icon = QSystemTrayIcon(self)
        # 使用标准图标作为托盘图标
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)

        # 创建托盘菜单
        tray_menu = QMenu()

        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        log_action = QAction("查看日志", self)
        log_action.triggered.connect(self.show_log_window)
        tray_menu.addAction(log_action)

        tray_menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # 双击托盘图标显示主窗口
        self.tray_icon.activated.connect(self.on_tray_activated)

        self.tray_icon.show()

    def on_tray_activated(self, reason):
        """托盘图标被激活"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()

    def _on_connect_clicked(self):
        """连接按钮点击事件"""
        # 使用线程执行异步连接
        import threading
        thread = threading.Thread(
            target=self._connect_thread,
            daemon=True
        )
        thread.start()

    def _connect_thread(self):
        """连接线程"""
        try:
            if self.task_manager.mq_consumer.is_running():
                # 断开连接
                self.task_manager.disconnect()
                self._update_disconnected_ui()
            else:
                # 连接服务器（connect() 是同步函数）
                success = self.task_manager.connect()
                if success:
                    self.log_window.append_log("已连接到服务器", "INFO")
                    self._update_connected_ui()
                else:
                    self._show_connection_error("无法连接到服务器，请检查配置和 RabbitMQ")
        except Exception as e:
            self._show_connection_error(f"连接失败: {str(e)}")

    def _update_connected_ui(self):
        """更新已连接状态的 UI"""
        self.update_connected_signal.emit()

    def _do_update_connected_ui(self):
        """实际更新已连接 UI"""
        self.status_label.setText("状态: 在线")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #27ae60;")
        self.connect_btn.setText("断开连接")
        self.log_window.append_log("消息队列已连接", "INFO")

    def _update_disconnected_ui(self):
        """更新断开连接状态的 UI"""
        self.update_disconnected_signal.emit()

    def _do_update_disconnected_ui(self):
        """实际更新断开连接 UI"""
        self.status_label.setText("状态: 未连接")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #999;")
        self.connect_btn.setText("连接服务器")
        self.log_window.append_log("已断开连接", "WARNING")

    def _show_connection_error(self, message):
        """显示连接错误"""
        self.show_error_signal.emit(message)

    def _on_task_complete(self, task_id: str, status: str, message: str):
        """任务完成回调"""
        if task_id in self.current_tasks:
            task_info = self.current_tasks[task_id]
            self.current_tasks[task_id]["status"] = status

            # 更新统计
            if status == "completed":
                self.success_count += 1
            elif status == "failed":
                self.fail_count += 1

            # 记录日志
            status_text = "成功" if status == "completed" else "失败"
            self.log_window.append_log(f"任务完成: {task_id} - {status_text}", "INFO" if status == "completed" else "ERROR")

            # 更新计划执行脚本状态（从 plan_executions 中查找）
            script_data = task_info.get("script_data", {})
            parent_execution_id = script_data.get("parent_execution_id")
            script_index = script_data.get("script_index", -1)

            if parent_execution_id and parent_execution_id in self.task_manager.plan_executions:
                if 0 <= script_index < len(self.task_manager.plan_executions[parent_execution_id]["scripts"]):
                    old_status = self.task_manager.plan_executions[parent_execution_id]["scripts"][script_index]["status"]
                    self.task_manager.plan_executions[parent_execution_id]["scripts"][script_index]["status"] = status
                    self.log_window.append_log(f"计划执行脚本状态更新: {self.task_manager.plan_executions[parent_execution_id]['scripts'][script_index]['name']} {old_status} -> {status}", "DEBUG")

                    # 检查计划是否全部完成
                    plan_scripts = self.task_manager.plan_executions[parent_execution_id]["scripts"]
                    all_done = all(s["status"] in ["completed", "failed"] for s in plan_scripts)

                    if all_done:
                        self.log_window.append_log(
                            f"计划 '{self.task_manager.plan_executions[parent_execution_id]['plan_name']}' 执行完成",
                            "INFO"
                        )

            # 从当前任务列表中移除已完成的任务（"当前任务"只显示正在运行的）
            del self.current_tasks[task_id]

            # 更新 UI
            self.update_task_table()
            self.update_plan_table()
            self.update_stats()


    def update_task_status_from_manager(self):
        """从任务管理器更新任务状态（定时调用）"""
        # 获取任务管理器中正在运行的任务
        running_tasks = self.task_manager.running_tasks

        # 调试输出
        plan_executions_count = len(self.task_manager.plan_executions)
        if plan_executions_count > 0:
            print(f"[GUI DEBUG] plan_executions has {plan_executions_count} plans")
            for parent_id, plan_info in self.task_manager.plan_executions.items():
                print(f"[GUI DEBUG] Plan {parent_id}: name={plan_info.get('plan_name')}, scripts={len(plan_info.get('scripts', []))}")

        # 更新任务列表
        for task_id, task_info in running_tasks.items():
            if task_id not in self.current_tasks:
                # 新任务
                self.current_tasks[task_id] = {
                    "name": task_info.get("script_name", "未命名脚本"),
                    "status": "running",
                    "start_time": datetime.now().strftime("%H:%M:%S"),
                    "script_data": task_info.get("script_data", {})
                }
                self.total_count += 1
                self.log_window.append_log(f"任务开始: {task_id}", "INFO")

        # 从 plan_executions 更新计划执行表格
        new_plans_added = 0
        for parent_id, plan_info in self.task_manager.plan_executions.items():
            if parent_id not in self.current_plans:
                # 复制计划信息到 current_plans
                self.current_plans[parent_id] = {
                    "plan_name": plan_info["plan_name"],
                    "execution_mode": plan_info["execution_mode"],
                    "scripts": list(plan_info["scripts"])  # 复制脚本列表
                }
                new_plans_added += 1
                self.log_window.append_log(f"加载计划执行信息: {plan_info['plan_name']}, 脚本数: {len(plan_info['scripts'])}", "DEBUG")
                print(f"[GUI DEBUG] Loaded plan: {plan_info['plan_name']}, scripts: {len(plan_info['scripts'])}")

        if new_plans_added > 0:
            print(f"[GUI DEBUG] Added {new_plans_added} new plans to current_plans")

        # 更新表格
        self.update_task_table()
        self.update_plan_table()
        self.update_stats()

    def update_task_table(self):
        """更新任务表格"""
        self.task_table.setRowCount(len(self.current_tasks))

        for row, (task_id, task_info) in enumerate(self.current_tasks.items()):
            # 任务ID
            item_id = QTableWidgetItem(str(task_id))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_table.setItem(row, 0, item_id)

            # 脚本名称
            item_name = QTableWidgetItem(task_info["name"])
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_table.setItem(row, 1, item_name)

            # 状态
            status_item = QTableWidgetItem()
            if task_info["status"] == "running":
                status_item.setText("执行中")
                status_item.setBackground(QColor("#e6f7ff"))
            elif task_info["status"] == "completed":
                status_item.setText("已完成")
                status_item.setBackground(QColor("#f6ffed"))
            elif task_info["status"] == "failed":
                status_item.setText("失败")
                status_item.setBackground(QColor("#fff2f0"))
            elif task_info["status"] == "cancelled":
                status_item.setText("已取消")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_table.setItem(row, 2, status_item)

            # 开始时间
            item_time = QTableWidgetItem(task_info["start_time"])
            item_time.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_table.setItem(row, 3, item_time)

    def update_plan_table(self):
        """更新计划执行表格"""
        # 【修复】直接从 task_manager.plan_executions 读取，而不是从 current_plans
        # 这样可以确保状态实时同步
        plan_executions = self.task_manager.plan_executions
        total_rows = sum(len(plan["scripts"]) for plan in plan_executions.values())
        self.plan_table.setRowCount(total_rows)

        # 调试日志
        print(f"[GUI DEBUG] update_plan_table: plan数={len(plan_executions)}, 行数={total_rows}")
        self.log_window.append_log(f"[DEBUG] 更新计划表格: plan数={len(plan_executions)}, 行数={total_rows}", "DEBUG")
        from loguru import logger
        logger.info(f"[GUI] 更新计划表格: plan数={len(plan_executions)}, 行数={total_rows}")

        row = 0
        for plan_id, plan_info in plan_executions.items():
            print(f"[GUI DEBUG] 处理计划 {plan_id}: {plan_info['plan_name']}")
            logger.info(f"[GUI] 处理计划 {plan_id}: {plan_info['plan_name']}, 脚本数={len(plan_info['scripts'])}")
            self.log_window.append_log(f"[DEBUG] 处理计划 {plan_id}: {plan_info['plan_name']}", "DEBUG")
            for script in plan_info["scripts"]:
                print(f"[GUI DEBUG]   脚本: {script['name']}, 状态: {script['status']}")
                # 序号（第一列）
                item_index = QTableWidgetItem(f"{script['index'] + 1}")
                item_index.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.plan_table.setItem(row, 0, item_index)

                # 脚本名称
                item_name = QTableWidgetItem(script["name"])
                item_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.plan_table.setItem(row, 1, item_name)

                # 计划名称
                item_plan = QTableWidgetItem(plan_info["plan_name"])
                item_plan.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.plan_table.setItem(row, 2, item_plan)

                # 执行模式
                mode_text = "顺序执行" if plan_info["execution_mode"] == "sequential" else "并行执行"
                item_mode = QTableWidgetItem(mode_text)
                item_mode.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.plan_table.setItem(row, 3, item_mode)

                # 状态
                status_item = QTableWidgetItem()
                status = script["status"]
                if status == "waiting":
                    status_item.setText("等待执行")
                    status_item.setBackground(QColor("#f5f5f5"))
                elif status == "running":
                    status_item.setText("执行中")
                    status_item.setBackground(QColor("#e6f7ff"))
                elif status == "completed":
                    status_item.setText("已完成")
                    status_item.setBackground(QColor("#f6ffed"))
                elif status == "failed":
                    status_item.setText("失败")
                    status_item.setBackground(QColor("#fff2f0"))
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.plan_table.setItem(row, 4, status_item)

                row += 1

        print(f"[GUI DEBUG] 表格更新完成，共填充 {row} 行")
        logger.info(f"[GUI] 表格更新完成，共填充 {row} 行")

    def update_stats(self):
        """更新统计信息"""
        # 从任务管理器获取当前正在运行的任务数
        running_count = len(self.task_manager.running_tasks)

        # 获取系统资源使用情况
        resources = get_resource_usage()

        # 检查连接状态
        is_connected = self.task_manager.mq_consumer.is_running()

        self.stats_label.setText(
            f"总任务数: {self.total_count} | 成功: {self.success_count} | 失败: {self.fail_count} | "
            f"当前运行: {running_count} | "
            f"心跳: {'正常' if is_connected else '未连接'} | "
            f"CPU: {resources.get('cpu', 0)}% | 内存: {resources.get('memory', 0)}%"
        )

    def show_log_window(self):
        """显示日志窗口"""
        self.log_window.show()
        self.log_window.activateWindow()

    def reconfigure(self):
        """重新配置"""
        reply = QMessageBox.question(
            self,
            "重新配置",
            "确定要重新配置执行机吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 关闭连接
            if self.task_manager.mq_consumer.is_running():
                self.task_manager.disconnect()

            # 清空配置（清除必需的配置项，触发配置向导）
            from config import get_config_manager
            config_manager = get_config_manager()
            config_manager.update(
                server_url="",
                owner_username="",
                owner_password=""
            )

            # 重启应用进入配置向导
            QMessageBox.information(self, "提示", "配置已重置，请重启应用程序以进入配置向导")
            QApplication.instance().quit()

    def closeEvent(self, event):
        """关闭事件 - 最小化到托盘而不是退出"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "执行机已最小化",
            "执行机已在后台运行，双击托盘图标可恢复窗口",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def quit_application(self):
        """真正退出应用程序"""
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出执行机吗？\n退出后将无法接收和执行任务。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 断开连接
            if self.task_manager.mq_consumer.is_running():
                self.task_manager.disconnect()

            # 隐藏托盘图标
            self.tray_icon.hide()

            # 退出程序
            QApplication.instance().quit()
