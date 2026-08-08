"""
视频人数统计工具 — 程序入口。

医院候诊室患者视频批量处理工具：
1. 导入 MP4 视频
2. 提取中间帧，AI 识别画面人数
3. 按人数多选筛选
4. 导出选中视频到指定文件夹
"""

import sys
from pathlib import Path

# 确保能找到项目模块
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from ui.main_window import MainWindow


# ================================================================
# 深色主题全局样式
# ================================================================
DARK_STYLE = """
/* 全局 */
QMainWindow {
    background-color: #1A1A2E;
}
QWidget {
    background-color: #1A1A2E;
    color: #E0E0E0;
    font-size: 11pt;
}

/* 状态栏 */
QStatusBar {
    background-color: #16213E;
    color: #B0B0B0;
    border-top: 1px solid #2A2A4A;
    font-size: 10pt;
}

/* 进度条 */
QProgressBar {
    border: 1px solid #3A3A5A;
    border-radius: 4px;
    text-align: center;
    background-color: #252545;
    color: #E0E0E0;
    font-size: 11pt;
}
QProgressBar::chunk {
    background-color: #4FC3F7;
    border-radius: 3px;
}

/* 滚动条 */
QScrollBar:vertical {
    background: #1A1A2E;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #4A4A6A;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #5A5A7A;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 消息框 */
QMessageBox {
    background-color: #1E1E32;
    color: #E0E0E0;
}
QMessageBox QLabel {
    color: #E0E0E0;
    font-size: 11pt;
}
QMessageBox QPushButton {
    background-color: #3A3A5A;
    color: #E0E0E0;
    border: none;
    border-radius: 4px;
    padding: 6px 20px;
    font-size: 11pt;
}
QMessageBox QPushButton:hover {
    background-color: #4A4A6A;
}

/* 文件对话框 */
QFileDialog {
    background-color: #1E1E32;
    color: #E0E0E0;
}

/* 复选框 */
QCheckBox {
    color: #E0E0E0;
    spacing: 6px;
    font-size: 11pt;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #5A5A7A;
    border-radius: 3px;
    background-color: #252545;
}
QCheckBox::indicator:checked {
    background-color: #4FC3F7;
    border-color: #4FC3F7;
}
QCheckBox::indicator:hover {
    border-color: #4FC3F7;
}

/* 分割线 */
QFrame[frameShape="4"] {  /* HLine */
    background-color: #2A2A4A;
    max-height: 1px;
}
"""


def main():
    app = QApplication(sys.argv)

    # 深色主题
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)

    # 设置默认字体（中文友好）
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
