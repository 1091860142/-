# CLAUDE.md — 视频人数统计软件 项目指引

## 项目概述

为医院候诊室拍摄的患者视频开发一个 Windows 桌面软件，批量导入 MP4 视频，
提取中间帧用 AI（YOLOv8）识别画面中的患者人数，按人数筛选并导出选中的视频。

## 文档路径索引

| 文档 | 路径 | 说明 |
|------|------|------|
| 开发需求 | [docs/requirements.md](docs/requirements.md) | 用户需求、功能清单、决策记录 |
| 技术规范 | [docs/tech-spec.md](docs/tech-spec.md) | Python 版本、依赖库、模型选型 |
| 设计规范 | [docs/design-spec.md](docs/design-spec.md) | UI 布局、配色、交互逻辑 |
| 执行计划 | [docs/execution-plan.md](docs/execution-plan.md) | 分阶段执行步骤和验收标准 |
| 开发日志 | [dev-logs/](dev-logs/) | 每日开发日志（按日期命名） |
| 计划文件 | 本地开发计划文件 | 总体开发规划 |

## 工作规范

### 基本规则
1. **每次开始工作前**：先读取 `docs/execution-plan.md` 了解当前进度
2. **每次工作结束后**：在 `dev-logs/YYYY-MM-DD.md` 中记录完成事项和待办事项
3. **修改代码前**：先确认当前处于哪个开发阶段，不要跨阶段操作
4. **遇到问题**：先记录到日志，分析清楚再动手

### 开发原则
- 一个阶段一个阶段来，每阶段通过验收再进下一阶段
- 先保证底层模块正确，再开发 UI
- 保持代码简洁，注释用中文
- 优先使用 `本地脚本目录` 目录下的 PowerShell

### 阶段顺序
0. 环境搭建 → 1. 视频处理模块 → 2. 人体检测模块 → 3. UI 界面 → 4. 串联集成 → 5. 打包收尾

### 验收方式
- 每完成一个阶段，运行对应测试，确保功能正确
- 阶段 5 完成后，在未安装 Python 的 Windows 电脑上测试 exe

## 项目结构

```
项目根目录
├── CLAUDE.md                  # 本文件 — AI 助手项目指引
├── docs/                      # 项目标准文档
│   ├── requirements.md        # 需求文档
│   ├── tech-spec.md           # 技术规范
│   ├── design-spec.md         # 设计规范
│   └── execution-plan.md      # 执行计划（含进度追踪）
├── dev-logs/                  # 开发日志
│   └── YYYY-MM-DD.md          # 每日日志
├── video-people-counter/      # 源代码
│   ├── main.py                # 程序入口
│   ├── ui/                    # UI 层
│   │   ├── main_window.py     # 主窗口
│   │   ├── video_list.py      # 视频列表组件
│   │   └── filter_bar.py      # 筛选按钮栏
│   ├── core/                  # 核心逻辑层
│   │   ├── video_processor.py # 视频处理（提取帧、元信息）
│   │   └── people_detector.py # 人体检测（YOLO 模型）
│   └── utils/                 # 工具函数
│       └── file_utils.py      # 文件操作（复制导出等）
├── requirements.txt           # Python 依赖
└── build.bat                  # 一键打包脚本
```
