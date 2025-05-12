import subprocess
import time
import os
import sys
from winreg import *  # 仅Windows可用

# ---------------------- 配置项 ---------------------- #
PROGRAMS = [
    {"path": "frpc.exe", "type": "exe", "delay": 0},    # 立即启动
    {"path": "1.exe",      "type": "exe", "delay": 3},    # 延迟3秒
    {"path": "go1.bat",    "type": "bat", "delay": 3}     # 延迟3秒
]
LOG_FILENAME = "startup_log.txt"    # 日志文件名
USER_STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_FLAG = "startup_configured.txt"  # 自启标记文件
# ---------------------------------------------------- #

def add_to_startup(script_path):
    """添加到用户开机自启（非管理员权限）"""
    try:
        script_name = os.path.basename(script_path)
        python_path = sys.executable
        with OpenKey(HKEY_CURRENT_USER, USER_STARTUP_KEY, 0, KEY_SET_VALUE) as key:
            SetValueEx(key, script_name, 0, REG_SZ, f'"{python_path}" "{script_path}"')
        log_message("自启项已添加")
    except Exception as e:
        log_message(f"自启添加失败: {str(e)}")

def start_program(path, program_type):
    """启动程序（支持exe和bat，隐藏窗口）"""
    abs_path = os.path.abspath(path)
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # 隐藏窗口
        
        if program_type == "bat":
            # 启动bat文件需通过cmd执行
            subprocess.Popen(
                ["cmd.exe", "/C", abs_path],
                startupinfo=startupinfo,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # 启动exe程序
            subprocess.Popen(
                [abs_path],
                startupinfo=startupinfo,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        log_message(f"成功启动: {abs_path}")
        return True
    except Exception as e:
        log_message(f"启动失败 {abs_path}: {str(e)}")
        return False

def log_message(message):
    """记录日志到当前目录"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_content = f"[{timestamp}] {message}\n"
    with open(LOG_FILENAME, "a", encoding="utf-8") as f:
        f.write(log_content)
    print(log_content.strip())  # 同时输出到控制台

def main():
    # 初始化日志文件
    if not os.path.exists(LOG_FILENAME):
        with open(LOG_FILENAME, "w", encoding="utf-8") as f:
            f.write("===== 开机启动日志 =====\n")
    
    # 配置开机自启（仅首次运行）
    appdata_dir = os.path.join(os.getenv("APPDATA"), "")
    startup_flag_path = os.path.join(appdata_dir, STARTUP_FLAG)
    if not os.path.exists(startup_flag_path):
        add_to_startup(sys.argv[0])
        with open(startup_flag_path, "w") as f:
            f.write("initialized")
        log_message("首次运行，已配置自启")
    
    # 按顺序启动程序
    for program in PROGRAMS:
        time.sleep(program["delay"])  # 等待指定延迟
        start_program(program["path"], program["type"])

if __name__ == "__main__":
    main()
