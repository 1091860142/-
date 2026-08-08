"""
视频列表控件 — 显示视频缩略图、信息、复选框。深色主题。
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QCheckBox, QHeaderView, QLabel, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from pathlib import Path


class VideoListWidget(QWidget):
    """视频列表控件。"""

    # 信号：选中状态改变时发射
    selection_changed = Signal(int)  # 当前已选数量

    def __init__(self, parent=None):
        super().__init__(parent)
        self._video_data: list[dict] = []  # 存储完整视频数据
        self._filtered_indices: list[int] = []  # 筛选后的行索引
        self._filter_values: set = {None}  # 当前筛选条件
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels([
            "", "缩略图", "文件名", "人数", "时长", "大小"
        ])

        # 表头设置
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)

        self._table.setColumnWidth(0, 40)
        self._table.setColumnWidth(1, 200)
        self._table.setColumnWidth(3, 60)
        self._table.setColumnWidth(4, 80)
        self._table.setColumnWidth(5, 80)

        # 表格属性 — 关闭单元格选中聚焦，让复选框点一下就能响应
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setFocusPolicy(Qt.NoFocus)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(True)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setDefaultSectionSize(80)

        # 深色表格样式
        self._table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #2A2A4A;
                gridline-color: #2A2A4A;
                background-color: #1E1E32;
                alternate-background-color: #232340;
                font-size: 11pt;
                color: #E0E0E0;
                selection-background-color: #3A3A6A;
            }
            QTableWidget::item {
                padding: 4px;
                color: #E0E0E0;
            }
            QTableWidget::item:selected {
                background-color: #3A3A6A;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #16213E;
                border: none;
                border-bottom: 2px solid #4FC3F7;
                padding: 8px;
                font-weight: bold;
                font-size: 11pt;
                color: #B0B0B0;
            }
        """)

        layout.addWidget(self._table)

        # 全选复选框
        self._select_all_cb = QCheckBox("全选")
        self._select_all_cb.setStyleSheet("font-size: 11pt; background: transparent;")
        self._select_all_cb.stateChanged.connect(self._on_select_all)
        layout.addWidget(self._select_all_cb)

    def load_videos(self, video_data: list[dict]) -> None:
        """
        加载视频数据到列表。

        Args:
            video_data: 视频信息字典列表
        """
        self._video_data = video_data
        self._refresh_table()

    def _refresh_table(self) -> None:
        """根据当前筛选条件刷新表格。"""
        checked_paths = self._get_checked_paths()

        self._table.setRowCount(0)
        self._filtered_indices = []

        for i, data in enumerate(self._video_data):
            count = data.get("person_count", 0)

            if not self._matches_filter(count):
                continue

            self._filtered_indices.append(i)
            row = self._table.rowCount()
            self._table.insertRow(row)

            # 复选框 — 直接放在单元格里，不用包装容器（避免需要双击才能点中）
            cb = QCheckBox()
            cb.setChecked(data["file_path"] in checked_paths)
            cb.stateChanged.connect(lambda state, r=row: self._on_check_changed(r))
            cb.setStyleSheet("margin-left: 10px; background: transparent;")
            self._table.setCellWidget(row, 0, cb)

            # 缩略图
            thumb_path = data.get("thumbnail_path", "")
            if thumb_path and Path(thumb_path).exists():
                pixmap = QPixmap(thumb_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(190, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    thumb_label = QLabel()
                    thumb_label.setPixmap(pixmap)
                    thumb_label.setAlignment(Qt.AlignCenter)
                    thumb_label.setStyleSheet("background: transparent;")
                    self._table.setCellWidget(row, 1, thumb_label)

            # 文件名
            name_item = QTableWidgetItem(data.get("file_name", ""))
            self._table.setItem(row, 2, name_item)

            # 人数 (带颜色标签)
            count_str = str(count)
            count_item = QTableWidgetItem(count_str)
            count_item.setTextAlignment(Qt.AlignCenter)
            if count == 0:
                count_item.setForeground(Qt.gray)
            elif count <= 3:
                count_item.setForeground(Qt.green)
            elif count <= 6:
                count_item.setForeground(Qt.yellow)
            else:
                count_item.setForeground(Qt.red)
            self._table.setItem(row, 3, count_item)

            # 时长
            dur_item = QTableWidgetItem(data.get("duration_str", ""))
            dur_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 4, dur_item)

            # 大小
            size_item = QTableWidgetItem(f"{data.get('file_size_mb', 0)} MB")
            size_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 5, size_item)

        self._update_select_all_state()

    def _matches_filter(self, count: int) -> bool:
        """判断人数是否匹配当前筛选条件。"""
        if self._filter_values == {None}:
            return True
        result = False
        for val in self._filter_values:
            if val == -1 and count >= 11:
                result = True
            elif val == count:
                result = True
        return result

    def filter_by_values(self, filter_values: set) -> None:
        """按筛选值集合筛选列表。"""
        self._filter_values = filter_values
        self._refresh_table()

    def get_selected_paths(self) -> list[str]:
        """获取勾选的视频文件路径列表。"""
        return list(self._get_checked_paths())

    def _get_checked_paths(self) -> set[str]:
        """获取当前勾选的文件路径集合。"""
        checked = set()
        for row in range(self._table.rowCount()):
            widget = self._table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                idx = self._filtered_indices[row] if row < len(self._filtered_indices) else -1
                if 0 <= idx < len(self._video_data):
                    checked.add(self._video_data[idx]["file_path"])
        return checked

    def _on_check_changed(self, row: int) -> None:
        self._update_select_all_state()
        self.selection_changed.emit(len(self._get_checked_paths()))

    def _on_select_all(self, state: int) -> None:
        """全选 / 取消全选。"""
        is_checked = state == Qt.Checked.value
        # 阻断信号，避免每个复选框的 stateChanged 触发连锁反应
        self._select_all_cb.blockSignals(True)
        for row in range(self._table.rowCount()):
            widget = self._table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox):
                widget.setChecked(is_checked)
        self._select_all_cb.blockSignals(False)
        self.selection_changed.emit(len(self._get_checked_paths()))

    def _update_select_all_state(self) -> None:
        """根据当前勾选情况更新「全选」复选框。"""
        if self._table.rowCount() == 0:
            self._select_all_cb.blockSignals(True)
            self._select_all_cb.setCheckState(Qt.Unchecked)
            self._select_all_cb.blockSignals(False)
            return

        checked_count = sum(
            1 for row in range(self._table.rowCount())
            if isinstance(self._table.cellWidget(row, 0), QCheckBox)
            and self._table.cellWidget(row, 0).isChecked()
        )

        self._select_all_cb.blockSignals(True)
        if checked_count == 0:
            self._select_all_cb.setCheckState(Qt.Unchecked)
        elif checked_count == self._table.rowCount():
            self._select_all_cb.setCheckState(Qt.Checked)
        else:
            self._select_all_cb.setCheckState(Qt.PartiallyChecked)
        self._select_all_cb.blockSignals(False)
