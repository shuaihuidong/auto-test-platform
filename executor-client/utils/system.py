"""
系统工具函数
- 获取系统资源使用情况
- 平台检测
"""

import platform
import psutil


def get_system_info() -> dict:
    """
    获取系统信息

    Returns:
        系统信息字典
    """
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }


def get_resource_usage() -> dict:
    """
    获取系统资源使用情况

    Returns:
        资源使用情况 {"cpu": float, "memory": float, "disk": float}
    """
    # CPU 使用率（百分比）
    cpu_percent = psutil.cpu_percent(interval=0.1)

    # 内存使用率（百分比）
    memory = psutil.virtual_memory()
    memory_percent = memory.percent

    # 磁盘使用率（百分比）
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent

    return {
        "cpu": round(cpu_percent, 1),
        "memory": round(memory_percent, 1),
        "disk": round(disk_percent, 1)
    }


def get_platform() -> str:
    """
    获取操作系统平台

    Returns:
        'windows', 'darwin', 'linux'
    """
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "darwin"  # macOS
    elif system == "linux":
        return "linux"
    else:
        return "unknown"


def is_windows() -> bool:
    """是否为 Windows 系统"""
    return get_platform() == "windows"


def is_macos() -> bool:
    """是否为 macOS 系统"""
    return get_platform() == "darwin"


def is_linux() -> bool:
    """是否为 Linux 系统"""
    return get_platform() == "linux"


def find_chrome_path() -> str:
    """
    查找 Chrome 浏览器路径

    Returns:
        Chrome 可执行文件路径，未找到返回空字符串
    """
    import shutil

    # 尝试通过 which/where 命令查找
    chrome_names = ["chrome", "google-chrome", "google-chrome-stable"]
    for name in chrome_names:
        path = shutil.which(name)
        if path:
            return path

    # Windows 特定路径
    if is_windows():
        import os
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")

        paths = [
            f"{program_files}\\Google\\Chrome\\Application\\chrome.exe",
            f"{program_files_x86}\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe")
        ]

        for path in paths:
            if os.path.exists(path):
                return path

    # macOS 特定路径
    elif is_macos():
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        import os
        if os.path.exists(path):
            return path

    # Linux 特定路径
    elif is_linux():
        import os
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium"
        ]
        for path in paths:
            if os.path.exists(path):
                return path

    return ""


def find_firefox_path() -> str:
    """
    查找 Firefox 浏览器路径

    Returns:
        Firefox 可执行文件路径，未找到返回空字符串
    """
    import shutil
    import os

    # 尝试通过 which/where 命令查找
    path = shutil.which("firefox")
    if path:
        return path

    # Windows 特定路径
    if is_windows():
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")

        paths = [
            f"{program_files}\\Mozilla Firefox\\firefox.exe",
            f"{program_files_x86}\\Mozilla Firefox\\firefox.exe"
        ]

        for path in paths:
            if os.path.exists(path):
                return path

    # macOS 特定路径
    elif is_macos():
        path = "/Applications/Firefox.app/Contents/MacOS/firefox"
        if os.path.exists(path):
            return path

    # Linux 特定路径
    elif is_linux():
        paths = [
            "/usr/bin/firefox",
            "/usr/lib/firefox/firefox"
        ]
        for path in paths:
            if os.path.exists(path):
                return path

    return ""
