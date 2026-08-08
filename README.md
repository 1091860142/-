# 🏥 视频人数统计工具
> 日常运营需每日拍摄医院人流量视频，每月产出 200 + 条素材用于朋友圈宣传推送。因公司共享盘存储空间不足，被要求人工剔除人流量偏少的视频，手动逐条筛查耗时低效，遂用deepseek开发本本地自动筛选工具。可以批量导入 MP4 视频，AI 自动识别画面人数，按人数多选筛选，一键导出。

![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue)
![Python](https://img.shields.io/badge/Python-3.12-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ 功能

- **📁 批量导入** — 支持 MP4/AVI/MOV/MKV/WMV，一次选多个文件
- **🧠 AI 识别人数** — 自动提取视频中间帧，YOLOv8 模型检测画面人数
- **🔍 多选筛选** — 数字按钮多选组合筛选（如：选 6+7+8+9+10+10+ = 显示 ≥6人）
- **📂 导出视频** — 勾选视频，一键复制到指定文件夹
- **🌙 深色主题** — 灰黑配色，长时间使用不刺眼
- **🔒 本地处理** — 所有识别在本地完成，视频不上传网络，保护患者隐私

---

## 📥 下载

> 点击下方链接下载最新版可执行文件（无需安装 Python）：

### [⬇️ 下载 video-people-counter.exe](../../releases/latest)

下载后双击 `video-people-counter.exe` 即可运行。首次运行会自动下载 AI 模型（约 6MB），需要联网；之后完全离线使用。

---

## 🖥️ 界面预览
<img width="1102" height="752" alt="image" src="https://github.com/user-attachments/assets/03e68740-d524-4efe-a3be-18eef77f8930" />

---

## 🚀 快速开始

### 方式一：下载 exe（推荐）

1. 从 [Releases](../../releases) 页面下载 `视频人数统计.exe`
2. 双击运行，首次启动会自动下载 AI 模型
3. 导入视频 → 等待识别 → 筛选 → 勾选 → 导出

### 方式二：从源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/xxx/video-people-counter.git
cd video-people-counter

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行
python video-people-counter/main.py
```

### 方式三：自己打包

```bash
# 安装 PyInstaller
pip install pyinstaller

# 运行打包脚本
build.bat
```

---

## 📁 项目结构

```
├── video-people-counter/      # 源代码
│   ├── main.py                # 程序入口
│   ├── ui/                    # UI 层
│   │   ├── main_window.py     # 主窗口
│   │   ├── video_list.py      # 视频列表
│   │   └── filter_bar.py      # 筛选栏
│   ├── core/                  # 核心逻辑
│   │   ├── video_processor.py # 视频帧提取
│   │   └── people_detector.py # YOLO 人体检测
│   └── utils/
│       └── file_utils.py      # 文件工具
├── docs/                      # 项目文档
│   ├── requirements.md        # 需求文档
│   ├── tech-spec.md           # 技术规范
│   └── design-spec.md         # 设计规范
├── requirements.txt           # Python 依赖
├── build.bat                  # 打包脚本
└── CLAUDE.md                  # 开发指引
```

---

## 🛠️ 技术栈

| 模块 | 技术 |
|------|------|
| 桌面框架 | PySide6 (Qt) |
| 视频处理 | OpenCV |
| AI 模型 | YOLOv8n (Ultralytics) |
| 打包 | PyInstaller |

---

## ⚠️ 注意事项

- **首次运行需联网**：YOLO 模型首次会自动下载（约 6MB），之后离线运行
- **exe 文件较大（~305MB）**：因为包含了 PyTorch + CUDA 运行库
- **隐私安全**：所有视频处理在本地完成，不会上传到任何服务器
- **系统要求**：Windows 10/11 64 位

---

## 📄 License

MIT — 自由使用、修改、分发。
