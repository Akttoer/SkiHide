import os
import ctypes
import psutil
import sys
import traceback

# 内存清理白名单
DEFAULT_MEMORY_CLEAN_SKIP = {
    # 电压/功耗/调参
    "uxtu.exe",
    "throttlestop.exe",
    "intelxtu.exe",
    "xtucli.exe",
    "ryzenmaster.exe",
    "ryzenmasterdriver.exe",
    "ryzenadj.exe",

    # 显卡/硬件监控
    "msiafterburner.exe",
    "rtss.exe",
    "rtsshooksloader.exe",
    "hwinfo64.exe",
    "hwinfo32.exe",
    "aida64.exe",
    "occt.exe",

    # 常见系统关键（保守点）
    "dwm.exe",
    "explorer.exe",
}


def clean_temp_folder(logger):
    """Delete removable files under %TEMP%. Returns (deleted_files, deleted_dirs, failed)."""
    temp_dir = os.environ.get('TEMP') or os.environ.get('TMP')
    if not temp_dir:
        raise RuntimeError("未找到 %TEMP% 环境变量")

    deleted_files = 0
    deleted_dirs = 0
    failed = 0

    for root_dir, dirs, files in os.walk(temp_dir):
        for fn in files:
            fp = os.path.join(root_dir, fn)
            try:
                os.remove(fp)
                deleted_files += 1
            except Exception:
                failed += 1

    for root_dir, dirs, files in os.walk(temp_dir, topdown=False):
        for d in dirs:
            dp = os.path.join(root_dir, d)
            try:
                if not os.listdir(dp):
                    os.rmdir(dp)
                    deleted_dirs += 1
            except Exception:
                failed += 1

    logger.info(f"清理临时文件完成：文件 {deleted_files}，空目录 {deleted_dirs}，失败/跳过 {failed}")
    return deleted_files, deleted_dirs, failed

def clean_memory_working_set(logger, skip_process_names=None):
    """Try to shrink working sets for processes using EmptyWorkingSet (Windows only)."""

    if sys.platform != 'win32':
        raise RuntimeError("仅支持 Windows")



    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA = 0x0100

    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi

    cleaned = 0
    failed = 0

    # 合并默认跳过 + 用户自定义跳过
    skip_set = set(DEFAULT_MEMORY_CLEAN_SKIP)
    if skip_process_names:
        skip_set |= {str(x).strip().lower() for x in skip_process_names if str(x).strip()}

    for proc in psutil.process_iter(['pid', 'name']):
        pid = proc.info.get('pid')
        if not pid or pid == 0:
            continue
        name = (proc.info.get("name") or "").lower()

        # 跳过白名单进程（如 UXTU / ThrottleStop 等）
        if name in skip_set:
            continue

        # 跳过本程序自身
        if int(pid) == os.getpid():
            continue

        try:
            h = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, int(pid))
            if not h:
                failed += 1
                continue
            try:
                ok = psapi.EmptyWorkingSet(h)
                if ok:
                    cleaned += 1
                else:
                    failed += 1
            finally:
                kernel32.CloseHandle(h)
        except Exception:
            failed += 1

    logger.info(f"内存清理完成：成功 {cleaned}，失败 {failed}")
    return cleaned, failed
