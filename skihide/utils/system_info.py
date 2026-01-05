import os
import sys
import platform
import traceback

def get_system_info():
    import psutil
    try:
        system = platform.system()
        release = platform.release()
        version = platform.version()
        machine = platform.machine()
        processor = platform.processor()

        windows_version = ""
        if system == "Windows":
            try:
                import win32api
                import winreg

                version_info = win32api.GetVersionEx()
                win_build = version_info[2]

                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    product_name = winreg.QueryValueEx(key, "ProductName")[0]
                    release_id = winreg.QueryValueEx(key, "ReleaseId")[0]
                    build_branch = winreg.QueryValueEx(key, "CurrentBuildBranch")[0]
                    display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                    ubr = winreg.QueryValueEx(key, "UBR")[0]

                windows_version = f"{product_name} {display_version} {release_id} {win_build}.{ubr} {build_branch}"
            except Exception:
                windows_version = f"{system} {release} {version}"

        mem = psutil.virtual_memory()
        total_mem = mem.total / (1024**3)
        available_mem = mem.available / (1024**3)
        memory_info = f"{available_mem:.2f} GB / {total_mem:.2f} GB"

        disk = psutil.disk_usage('/')
        used_disk = disk.used / (1024**3)
        total_disk = disk.total / (1024**3)

        network_interfaces = [nic for nic, addrs in psutil.net_if_addrs().items()]

        script_path = os.path.abspath(__file__)
        exe_path = sys.executable

        system_info = {
            "系统版本": windows_version,
            "平台": platform.platform(),
            "系统": system,
            "版本号": release,
            "构建版本": version,
            "架构": machine,
            "处理器": processor,
            "Python版本": platform.python_version(),
            "Python构建": platform.python_build(),
            "Python编译器": platform.python_compiler(),
            "Python路径": exe_path,
            "软件路径": script_path,
            "工作目录": os.getcwd(),
            "CPU核心数": str(psutil.cpu_count()),
            "内存信息": memory_info,
            "可用内存": "%.2f GB" % available_mem,
            "总内存": "%.2f GB" % total_mem,
            "磁盘使用": "%.2f GB / %.2f GB" % (used_disk, total_disk),
            "网络接口": str(network_interfaces),
            "进程ID": str(os.getpid()),
            "父进程ID": str(os.getppid())
        }
        return system_info
    except Exception as e:
        system = platform.system()
        release = platform.release()
        version = platform.version()
        windows_version = f"{system} {release} {version}"
        return {
            "错误信息": str(e),
            "系统版本": windows_version,
            "平台": platform.platform(),
            "Python版本": platform.python_version(),
            "Python路径": sys.executable,
            "软件路径": os.path.abspath(__file__),
            "进程ID": str(os.getpid())
        }
