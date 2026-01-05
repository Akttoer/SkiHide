import os
import ctypes
import psutil
import sys
import traceback

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

    logger.info(f"清理TEMP完成：文件 {deleted_files}，空目录 {deleted_dirs}，失败/跳过 {failed}")
    return deleted_files, deleted_dirs, failed

def clean_memory_working_set(logger):
    """Try to shrink working sets for processes using EmptyWorkingSet (Windows only)."""

    if sys.platform != 'win32':
        raise RuntimeError("仅支持 Windows")



    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA = 0x0100

    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi

    cleaned = 0
    failed = 0

    for proc in psutil.process_iter(['pid', 'name']):
        pid = proc.info.get('pid')
        if not pid or pid == 0:
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
