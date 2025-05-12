import subprocess
import sys
import os
import time
from ctypes import windll
import win32gui  # 需提前安装 pywin32 库

# ---------------------- 配置项 ---------------------- #
FRPC_PATH = "frpc.exe"               # frpc.exe 路径（默认当前目录，可改为绝对路径）
FRPC_ARGS = ["-c", "frpc.ini"]       # 启动参数（即 frpc -c frpc.ini）
HIDE_WINDOW_DELAY = 1                # 等待窗口创建的时间（秒）
# ---------------------------------------------------- #

def start_frpc_hidden(exe_path, args):
    """启动 frpc 并隐藏窗口"""
    if sys.platform != "win32":
        raise SystemError("此脚本仅支持 Windows 系统")
    
    # 构造完整命令（路径 + 参数）
    command = [exe_path] + args
    
    # 1. 启动程序并隐藏初始控制台窗口
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0  # SW_HIDE = 0（隐藏初始窗口）
    
    process = subprocess.Popen(
        command,
        startupinfo=startupinfo,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    pid = process.pid
    print(f"frpc 已启动，进程 ID：{pid}")
    
    # 2. 等待窗口创建（防止提前隐藏失败）
    time.sleep(HIDE_WINDOW_DELAY)
    
    # 3. 枚举并隐藏所有关联窗口（包括可能残留的控制台）
    hide_all_windows_by_pid(pid)
    return pid

def hide_all_windows_by_pid(pid):
    """根据进程 ID 隐藏所有窗口"""
    def enum_window_callback(hwnd, _):
        # 获取窗口所属进程 ID
        _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
        if window_pid == pid:
            # 隐藏窗口（0 表示 SW_HIDE）
            windll.user32.ShowWindow(hwnd, 0)
        return True  # 继续枚举
    
    win32gui.EnumWindows(enum_window_callback, 0)
    print("窗口已成功隐藏，frpc 在后台运行")

if __name__ == "__main__":
    try:
        # 检查 frpc.exe 是否存在
        if not os.path.exists(FRPC_PATH):
            raise FileNotFoundError(f"未找到 frpc.exe：{FRPC_PATH}")
        
        # 启动并隐藏 frpc
        pid = start_frpc_hidden(FRPC_PATH, FRPC_ARGS)
        print(f"frpc 后台运行中（进程 ID：{pid}）")
        
        # 可选：保持脚本运行（避免进程被系统回收）
        # input("按回车键终止 frpc...")
        # subprocess.Popen(f"taskkill /F /PID {pid}", shell=True)
    
    except Exception as e:
        print(f"错误：{str(e)}")
        sys.exit(1)
