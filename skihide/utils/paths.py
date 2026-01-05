import os
import sys

def resource_path(relative_path: str) -> str:
    """Get resource path; works in PyInstaller one-file too."""
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
