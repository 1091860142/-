"""
筛选按钮栏 — 提供 全部 / 0 / 1 / ... / 10 / 10+ 的多选筛选按钮。
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt


class FilterBar(QWidget):
    """人数筛选按钮栏 — 支持多选。"""

    # 信号：当筛选条件改变时发射，参数为选中的筛选值集合
    # None 表示「全部」，-1 表示「10+」，0~10 表示对应人数
    filter_changed = Signal(set)

    FILTERS = [
        ("全部", None),
        ("0", 0),
        ("1", 1),
        ("2", 2),
        ("3", 3),
        ("4", 4),
        ("5", 5),
        ("6", 6),
        ("7", 7),
        ("8", 8),
        ("9", 9),
        ("10", 10),
        ("10+", -1),
    ]

    # 样式
    BTN_NORMAL = """
        QPushButton {
            background-color: #2D2D4A;
            color: #B0B0B0;
            border: 1px solid #3A3A5A;
            border-radius: 4px;
            font-size: 12pt;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #3A3A6A;
            color: #E0E0E0;
        }
    """
    BTN_CHECKED = """
        QPushButton {
            background-color: #4FC3F7;
            color: #1A1A2E;
            border: 1px solid #4FC3F7;
            border-radius: 4px;
            font-size: 12pt;
            font-weight: bold;
            padding: 5px 10px;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected: set = {None}  # 默认选中「全部」
        self._buttons: dict = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel("按人数筛选:")
        label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #E0E0E0; background: transparent;")
        layout.addWidget(label)

        for text, value in self.FILTERS:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedSize(52, 36) if text != "全部" else btn.setFixedSize(60, 36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setChecked(value in self._selected)
            self._buttons[value] = btn
            layout.addWidget(btn)

            def make_handler(v):
                return lambda: self._on_click(v)
            btn.clicked.connect(make_handler(value))

        layout.addStretch()
        self._update_styles()

    def _on_click(self, value):
        """处理按钮点击 — 多选逻辑。"""
        if value is None:
            # 点击「全部」→ 清空其他选择，只保留全部
            if self._selected == {None}:
                return  # 已经是全部，不变化
            self._selected = {None}
        else:
            # 点击数字按钮
            if None in self._selected:
                # 当前是全选状态 → 取消全部，只选当前
                self._selected = {value}
            elif value in self._selected:
                # 取消当前选择
                self._selected.discard(value)
                # 如果全取消了，自动回到「全部」
                if not self._selected:
                    self._selected = {None}
            else:
                # 添加当前选择
                self._selected.add(value)

        self._update_styles()
        self.filter_changed.emit(self._selected)

    def _update_styles(self):
        """刷新按钮状态和样式。"""
        for val, btn in self._buttons.items():
            btn.setChecked(val in self._selected)
            if val in self._selected:
                btn.setStyleSheet(self.BTN_CHECKED)
            else:
                btn.setStyleSheet(self.BTN_NORMAL)

    @property
    def current_filter(self) -> set:
        """当前选中的筛选值集合。{None} 表示全部。"""
        return self._selected
