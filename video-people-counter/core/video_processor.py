"""
视频处理模块 — 提取视频中间帧、读取视频元信息。
"""

import cv2
import tempfile
from pathlib import Path
from dataclasses import dataclass


@dataclass
class VideoInfo:
    """视频元信息。"""
    file_path: str        # 视频文件完整路径
    file_name: str        # 文件名
    file_size_mb: float   # 文件大小 (MB)
    duration_sec: float   # 时长 (秒)
    duration_str: str     # 时长 (HH:MM:SS 格式)
    fps: float            # 帧率
    width: int            # 画面宽度
    height: int           # 画面高度
    total_frames: int     # 总帧数
    thumbnail_path: str   # 缩略图（中间帧）保存路径


class VideoProcessor:
    """视频处理器：提取中间帧，读取元信息。"""

    # 缩略图最大尺寸（保持宽高比缩放）
    THUMBNAIL_MAX_WIDTH = 200
    THUMBNAIL_MAX_HEIGHT = 150

    def __init__(self, thumbnail_dir: str | None = None):
        """
        初始化视频处理器。

        Args:
            thumbnail_dir: 缩略图保存目录。如果为 None，使用系统临时目录。
        """
        if thumbnail_dir:
            self.thumbnail_dir = Path(thumbnail_dir)
            self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.thumbnail_dir = Path(tempfile.gettempdir()) / "video_people_counter_thumbnails"
            self.thumbnail_dir.mkdir(parents=True, exist_ok=True)

    def process(self, video_path: str) -> VideoInfo:
        """
        处理一个视频文件：提取中间帧 + 获取元信息。

        Args:
            video_path: 视频文件路径

        Returns:
            VideoInfo 对象，包含视频的所有元信息和缩略图路径

        Raises:
            FileNotFoundError: 视频文件不存在
            ValueError: 无法打开视频文件或格式不支持
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件（格式可能不支持）: {video_path}")

        try:
            # --- 读取元信息 ---
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            if fps <= 0:
                fps = 30.0  # 默认值，避免除零

            duration_sec = total_frames / fps if fps > 0 else 0

            # 时长转为 HH:MM:SS 格式
            hours = int(duration_sec // 3600)
            minutes = int((duration_sec % 3600) // 60)
            seconds = int(duration_sec % 60)
            if hours > 0:
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes:02d}:{seconds:02d}"

            # 文件大小 (MB)
            file_size_mb = video_path.stat().st_size / (1024 * 1024)

            # --- 提取中间帧 ---
            middle_frame_index = total_frames // 2
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_index)
            ret, frame = cap.read()

            if not ret:
                # 如果中间帧读取失败，回退到第一帧
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()

            if not ret:
                raise ValueError(f"无法从视频中提取任何帧: {video_path}")

            # 缩略图：缩小到指定尺寸以内
            h, w = frame.shape[:2]
            scale = min(self.THUMBNAIL_MAX_WIDTH / w, self.THUMBNAIL_MAX_HEIGHT / h, 1.0)
            if scale < 1.0:
                new_w = int(w * scale)
                new_h = int(h * scale)
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # 保存缩略图：用视频文件名（去扩展名）+ .jpg
            thumbnail_name = video_path.stem + "_thumb.jpg"
            thumbnail_path = self.thumbnail_dir / thumbnail_name
            cv2.imwrite(str(thumbnail_path), frame)

            return VideoInfo(
                file_path=str(video_path),
                file_name=video_path.name,
                file_size_mb=round(file_size_mb, 2),
                duration_sec=round(duration_sec, 1),
                duration_str=duration_str,
                fps=round(fps, 1),
                width=width,
                height=height,
                total_frames=total_frames,
                thumbnail_path=str(thumbnail_path),
            )

        finally:
            cap.release()

    def batch_process(self, video_paths: list[str]) -> list[VideoInfo]:
        """
        批量处理视频文件。

        Args:
            video_paths: 视频文件路径列表

        Returns:
            VideoInfo 对象列表（处理失败的视频会被跳过，不包含在结果中）
        """
        results = []
        for path in video_paths:
            try:
                info = self.process(path)
                results.append(info)
            except Exception as e:
                # 跳过失败的视频，后续 UI 层可以提示用户
                print(f"[警告] 处理失败: {path} — {e}")
        return results


# ============================================================
# 简单自测：直接运行此文件时会用测试视频验证功能
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python video_processor.py <视频文件路径>")
        print("  例: python video_processor.py test.mp4")
        sys.exit(1)

    processor = VideoProcessor()
    info = processor.process(sys.argv[1])

    print(f"文件名:    {info.file_name}")
    print(f"大小:      {info.file_size_mb} MB")
    print(f"时长:      {info.duration_str} ({info.duration_sec}s)")
    print(f"分辨率:    {info.width} × {info.height}")
    print(f"帧率:      {info.fps} fps")
    print(f"总帧数:    {info.total_frames}")
    print(f"缩略图:    {info.thumbnail_path}")
