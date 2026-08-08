# 技术规范文档

## 运行环境

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10 / 11（64 位） |
| Python | 3.12.x |
| 包管理 | pip |

## 依赖库

| 库 | 版本 | 用途 |
|------|------|------|
| PySide6 | >=6.5 | 桌面 UI 框架（Qt for Python） |
| opencv-python | >=4.8 | 视频帧提取、图像处理 |
| ultralytics | >=8.0 | YOLOv8 人体检测模型 |
| Pillow | >=10.0 | 图像缩略图处理 |
| pyinstaller | >=6.0 | 打包为 exe（仅开发时使用） |

## AI 模型选型

| 项目 | 选择 |
|------|------|
| 模型 | YOLOv8n（nano，最轻量版） |
| 理由 | 模型文件小（~6MB），速度快，CPU 可运行，人数检测精度足够 |
| 下载方式 | 首次运行时自动从 ultralytics 下载 |
| 检测类别 | 仅统计 `person` 类别的数量 |

## 项目结构

```
video-people-counter/
├── main.py              # 程序入口，启动 UI
├── ui/
│   ├── __init__.py
│   ├── main_window.py   # 主窗口类
│   ├── video_list.py    # 视频列表控件
│   └── filter_bar.py    # 筛选按钮栏控件
├── core/
│   ├── __init__.py
│   ├── video_processor.py  # VideoProcessor 类
│   └── people_detector.py  # PeopleDetector 类
└── utils/
    ├── __init__.py
    └── file_utils.py    # 文件复制等工具函数
```

## 核心类设计

### VideoProcessor
```
class VideoProcessor:
    def extract_middle_frame(video_path) -> Path  # 提取中间帧，返回图片路径
    def get_video_info(video_path) -> dict        # 返回时长、大小、fps 等
```

### PeopleDetector
```
class PeopleDetector:
    def __init__()                                # 加载 YOLO 模型
    def count_people(image_path) -> int           # 返回检测到的人数
```

## 打包方案

- 使用 PyInstaller 打包为单个 exe 文件
- 命令：`pyinstaller --onefile --windowed --name "视频人数统计" main.py`
- 需要将 YOLO 模型文件一同打包

## 数据存储

- 使用 JSON 文件存储用户偏好（如上次导出路径）
- 文件位置：`%APPDATA%/video-people-counter/settings.json`
- 不使用数据库
