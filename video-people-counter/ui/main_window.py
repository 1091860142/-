"""
主窗口 — 视频人数统计工具的主界面。深色主题 + 追加导入 + 多选筛选。
"""

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QProgressBar, QStatusBar, QLabel,
    QFileDialog, QMessageBox, QFrame,
)
from PySide6.QtCore import Qt, QThread, Signal

from core.video_processor import VideoProcessor
from core.people_detector import PeopleDetector
from ui.filter_bar import FilterBar
from ui.video_list import VideoListWidget
from utils.file_utils import copy_videos, get_last_export_dir, set_last_export_dir


class ProcessWorker(QThread):
    """后台处理线程：提取帧 + AI 识别人数。"""
    progress = Signal(int, str)
    video_done = Signal(dict)
    all_done = Signal()
    error = Signal(str)

    def __init__(self, video_paths: list[str]):
        super().__init__()
        self.video_paths = video_paths

    def run(self):
        processor = VideoProcessor()
        detector = PeopleDetector()
        total = len(self.video_paths)

        for i, path in enumerate(self.video_paths):
            try:
                self.progress.emit(int((i / total) * 100), Path(path).name)

                info = processor.process(path)
                person_count = detector.count_people(info.thumbnail_path)

                data = {
                    "file_path": info.file_path,
                    "file_name": info.file_name,
                    "file_size_mb": info.file_size_mb,
                    "duration_str": info.duration_str,
                    "duration_sec": info.duration_sec,
                    "fps": info.fps,
                    "width": info.width,
                    "height": info.height,
                    "thumbnail_path": info.thumbnail_path,
                    "person_count": person_count,
                }
                self.video_done.emit(data)

            except Exception as e:
                self.error.emit(f"处理失败: {Path(path).name} — {e}")

        self.progress.emit(100, "处理完成")
        self.all_done.emit()


class ExportWorker(QThread):
    """后台导出线程。"""
    done = Signal(int, list)

    def __init__(self, video_paths: list[str], dest_dir: str):
        super().__init__()
        self.video_paths = video_paths
        self.dest_dir = dest_dir

    def run(self):
        success, failed = copy_videos(self.video_paths, self.dest_dir)
        self.done.emit(success, failed)


class MainWindow(QMainWindow):
    """主窗口。"""

    def __init__(self):
        super().__init__()
        self._video_data: list[dict] = []
        self._existing_paths: set[str] = set()  # 已导入的文件路径，用于去重
        self._process_worker: ProcessWorker | None = None
        self._export_worker: ExportWorker | None = None

        self._setup_ui()
        self._connect_signals()

    # ================================================================
    # UI 初始化
    # ================================================================

    def _setup_ui(self):
        self.setWindowTitle("视频人数统计工具")
        self.resize(1100, 720)
        self.setMinimumSize(800, 500)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(10)

        # 工具栏
        main_layout.addWidget(self._create_toolbar())

        # 筛选栏
        self._filter_bar = FilterBar()
        main_layout.addWidget(self._filter_bar)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        main_layout.addWidget(line)

        # 视频列表
        self._video_list = VideoListWidget()
        main_layout.addWidget(self._video_list, stretch=1)

        # 状态栏
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_label = QLabel("就绪 — 点击「导入视频」开始")
        self._status_count_label = QLabel("")
        self._status_bar.addWidget(self._status_label, 1)
        self._status_bar.addPermanentWidget(self._status_count_label)

    def _create_toolbar(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        btn_style_import = """
            QPushButton {
                background-color: #4FC3F7;
                color: #1A1A2E;
                border: none;
                border-radius: 6px;
                font-size: 13pt;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover { background-color: #81D4FA; }
            QPushButton:pressed { background-color: #29B6F6; }
            QPushButton:disabled { background-color: #3A3A5A; color: #666666; }
        """

        btn_style_export = """
            QPushButton {
                background-color: #66BB6A;
                color: #1A1A2E;
                border: none;
                border-radius: 6px;
                font-size: 13pt;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover { background-color: #81C784; }
            QPushButton:pressed { background-color: #43A047; }
            QPushButton:disabled { background-color: #3A3A5A; color: #666666; }
        """

        self._import_btn = QPushButton("📁 导入视频")
        self._import_btn.setFixedHeight(42)
        self._import_btn.setCursor(Qt.PointingHandCursor)
        self._import_btn.setStyleSheet(btn_style_import)

        self._export_btn = QPushButton("📂 导出选中")
        self._export_btn.setFixedHeight(42)
        self._export_btn.setCursor(Qt.PointingHandCursor)
        self._export_btn.setEnabled(False)
        self._export_btn.setStyleSheet(btn_style_export)

        # 进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(28)
        self._progress_bar.setVisible(False)

        self._progress_label = QLabel("")
        self._progress_label.setStyleSheet("font-size: 11pt; color: #9E9E9E; background: transparent;")
        self._progress_label.setVisible(False)

        layout.addWidget(self._import_btn)
        layout.addWidget(self._export_btn)
        layout.addWidget(self._progress_bar, 1)
        layout.addWidget(self._progress_label)
        layout.addStretch()

        return widget

    # ================================================================
    # 信号连接
    # ================================================================

    def _connect_signals(self):
        self._import_btn.clicked.connect(self._on_import)
        self._export_btn.clicked.connect(self._on_export)
        self._filter_bar.filter_changed.connect(self._on_filter_changed)
        self._video_list.selection_changed.connect(self._on_selection_changed)

    # ================================================================
    # 导入视频（追加模式 — 不清除已有结果）
    # ================================================================

    def _on_import(self):
        """导入视频 — 追加到现有列表，跳过重复文件。"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择视频文件",
            os.path.expanduser("~\\Desktop"),
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv);;所有文件 (*.*)",
        )
        if not file_paths:
            return

        # 去重：跳过已导入的文件
        new_paths = [p for p in file_paths if p not in self._existing_paths]
        skipped = len(file_paths) - len(new_paths)

        if not new_paths:
            QMessageBox.information(self, "提示", f"所选 {len(file_paths)} 个视频已全部导入过了。")
            return

        if skipped > 0:
            self._status_label.setText(f"跳过 {skipped} 个重复视频，处理新增的 {len(new_paths)} 个...")
        else:
            self._status_label.setText(f"正在处理 {len(new_paths)} 个视频...")

        # 禁用按钮
        self._import_btn.setEnabled(False)
        self._export_btn.setEnabled(False)

        # 显示进度
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._progress_label.setVisible(True)

        # 启动后台处理
        self._process_worker = ProcessWorker(new_paths)
        self._process_worker.progress.connect(self._on_process_progress)
        self._process_worker.video_done.connect(self._on_video_done)
        self._process_worker.all_done.connect(self._on_all_done)
        self._process_worker.error.connect(self._on_process_error)
        self._process_worker.start()

    def _on_process_progress(self, percent: int, file_name: str):
        self._progress_bar.setValue(percent)
        self._progress_label.setText(file_name)

    def _on_video_done(self, data: dict):
        """单个视频处理完成 — 追加到列表。"""
        self._video_data.append(data)
        self._existing_paths.add(data["file_path"])
        self._video_list.load_videos(self._video_data)
        self._update_status_counts()

    def _on_all_done(self):
        """全部处理完成。"""
        self._progress_bar.setVisible(False)
        self._progress_label.setVisible(False)
        self._import_btn.setEnabled(True)

        total = len(self._video_data)
        self._status_label.setText(f"导入完成，共 {total} 个视频")
        self._update_status_counts()

    def _on_process_error(self, msg: str):
        print(f"[错误] {msg}")

    # ================================================================
    # 筛选（多选）
    # ================================================================

    def _on_filter_changed(self, filter_values: set):
        """筛选条件改变（多选集合）。"""
        self._video_list.filter_by_values(filter_values)
        self._update_status_counts()

        # 生成筛选描述
        if filter_values == {None}:
            label = "全部"
        else:
            parts = []
            for v in sorted(filter_values, key=lambda x: (x is None, x if x is not None else -999)):
                if v == -1:
                    parts.append("10+")
                else:
                    parts.append(str(v))
            label = " ≥ ".join(parts) if len(parts) <= 3 else f"{len(parts)}个条件"
        self._status_label.setText(f"筛选: {label}人")

    # ================================================================
    # 导出
    # ================================================================

    def _on_export(self):
        selected = self._video_list.get_selected_paths()
        if not selected:
            QMessageBox.information(self, "提示", "请先勾选要导出的视频。")
            return

        default_dir = get_last_export_dir()
        dest_dir = QFileDialog.getExistingDirectory(self, "选择导出文件夹", default_dir)
        if not dest_dir:
            return

        set_last_export_dir(dest_dir)

        self._export_btn.setEnabled(False)
        self._import_btn.setEnabled(False)
        self._status_label.setText(f"正在导出 {len(selected)} 个视频...")

        self._export_worker = ExportWorker(selected, dest_dir)
        self._export_worker.done.connect(self._on_export_done)
        self._export_worker.start()

    def _on_export_done(self, success: int, failed: list):
        self._export_btn.setEnabled(True)
        self._import_btn.setEnabled(True)

        if failed:
            QMessageBox.warning(
                self, "导出完成",
                f"成功导出 {success} 个视频。\n以下文件导出失败:\n" + "\n".join(failed),
            )
        else:
            QMessageBox.information(self, "导出完成", f"成功导出 {success} 个视频到目标文件夹！")

        self._status_label.setText(f"导出完成: {success} 个视频")
        self._update_status_counts()

    # ================================================================
    # 状态
    # ================================================================

    def _on_selection_changed(self, count: int):
        self._export_btn.setEnabled(count > 0)
        self._update_status_counts()

    def _update_status_counts(self):
        total = len(self._video_data)
        visible = sum(1 for d in self._video_data
                      if self._video_list._matches_filter(d.get("person_count", 0)))
        selected = len(self._video_list.get_selected_paths())
        self._status_count_label.setText(
            f"共 {total} 个 | 筛选: {visible} 个 | 已选: {selected} 个"
        )
