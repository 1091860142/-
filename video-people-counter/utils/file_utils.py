"""
文件操作工具 — 视频导出、设置持久化等。
"""

import json
import shutil
from pathlib import Path


# 设置文件路径
SETTINGS_DIR = Path.home() / "AppData" / "Roaming" / "video-people-counter"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


def load_settings() -> dict:
    """读取用户设置。"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings: dict) -> None:
    """保存用户设置。"""
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    # 合并已有设置
    existing = load_settings()
    existing.update(settings)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


def get_last_export_dir() -> str:
    """获取上次使用的导出目录。"""
    settings = load_settings()
    return settings.get("last_export_dir", str(Path.home() / "Desktop"))


def set_last_export_dir(directory: str) -> None:
    """记住导出目录。"""
    save_settings({"last_export_dir": directory})


def copy_videos(video_paths: list[str], dest_dir: str) -> tuple[int, list[str]]:
    """
    将视频文件复制到目标目录。

    Args:
        video_paths: 视频文件路径列表
        dest_dir: 目标文件夹路径

    Returns:
        (成功数量, 失败文件列表)
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = []

    for src_path in video_paths:
        src = Path(src_path)
        dst = dest / src.name

        try:
            shutil.copy2(src, dst)  # copy2 保留文件元信息
            success += 1
        except Exception as e:
            failed.append(f"{src.name}: {e}")

    return success, failed
