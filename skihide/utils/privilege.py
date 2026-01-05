import sys
import ctypes

def ensure_admin_or_exit() -> None:
    """Re-run as admin on Windows. Exits current process if elevation is triggered."""
    if sys.platform != 'win32':
        return
    try:
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, ' '.join(sys.argv), None, 1
            )
            sys.exit(0)
    except Exception as e:
        print("权限提升失败:", e)
        sys.exit(1)
