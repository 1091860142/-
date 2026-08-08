"""
人体检测模块 — 使用 YOLOv8 模型识别图片中的人数。
"""

from pathlib import Path
from ultralytics import YOLO


class PeopleDetector:
    """人体检测器：加载 YOLO 模型，统计画面中的人数。"""

    # YOLO 模型中 "person" 类别的索引为 0
    PERSON_CLASS_ID = 0

    def __init__(self, model_name: str = "yolov8n.pt"):
        """
        初始化检测器，加载 YOLO 模型。

        Args:
            model_name: 模型名称或路径。
                        "yolov8n.pt" — 最轻量，适合 CPU 运行（默认）
                        "yolov8s.pt" — 更准确，但速度稍慢
                        首次运行会自动下载模型文件（约 6MB）。
        """
        self.model_name = model_name
        self._model: YOLO | None = None

    @property
    def model(self) -> YOLO:
        """延迟加载模型（首次调用时才加载）。"""
        if self._model is None:
            print(f"[信息] 正在加载 AI 模型 {self.model_name}（首次运行需要下载，约 6MB）...")
            self._model = YOLO(self.model_name)
            print(f"[信息] 模型加载完成。")
        return self._model

    def count_people(self, image_path: str) -> int:
        """
        检测图片中的人数。

        Args:
            image_path: 图片文件路径

        Returns:
            检测到的人数 (>= 0)

        Raises:
            FileNotFoundError: 图片文件不存在
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 运行检测
        results = self.model(str(image_path), verbose=False)

        # 统计 person 类别的检测框数量
        count = 0
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    if class_id == self.PERSON_CLASS_ID:
                        count += 1

        return count

    def count_people_batch(self, image_paths: list[str]) -> list[int]:
        """
        批量检测多张图片中的人数。

        Args:
            image_paths: 图片文件路径列表

        Returns:
            人数列表，与输入顺序一一对应
        """
        results = []
        for path in image_paths:
            try:
                count = self.count_people(path)
                results.append(count)
            except Exception as e:
                print(f"[警告] 检测失败: {path} — {e}")
                results.append(-1)  # -1 表示检测失败
        return results


# ============================================================
# 简单自测：直接运行此文件时对指定图片检测人数
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python people_detector.py <图片文件路径>")
        print("  例: python people_detector.py frame.jpg")
        sys.exit(1)

    detector = PeopleDetector()
    count = detector.count_people(sys.argv[1])
    print(f"检测结果: {count} 人")
