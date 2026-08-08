# 执行计划

## 阶段总览

| 阶段 | 名称 | 状态 | 完成时间 |
|------|------|------|----------|
| 0 | 环境搭建 | ✅ 已完成 | 2026-08-08 |
| 1 | 视频处理模块 | ✅ 已完成 | 2026-08-08 |
| 2 | AI 人体检测模块 | ✅ 已完成 | 2026-08-08 |
| 3 | UI 界面搭建 | ✅ 已完成 | 2026-08-08 |
| 4 | 串联集成 | ✅ 已完成 | 2026-08-08 |
| 5 | 打包收尾 | ✅ 已完成 | 2026-08-08 |

---

## 阶段 0：环境搭建 ✅

### 目标
确认开发环境可用，安装所有依赖，创建项目结构。

### 完成事项
- [x] Python 3.12.10 已安装
- [x] pip 25.0.1 可用
- [x] 项目目录结构已创建
- [x] 文档体系已搭建

### 待安装依赖
- [ ] PySide6
- [ ] opencv-python
- [ ] ultralytics
- [ ] Pillow

---

## 阶段 1：视频处理模块

### 目标
实现视频文件的中间帧提取和元信息读取。

### 输入
- 视频文件路径（MP4 等格式）

### 输出
- 中间帧图片文件（保存到临时目录）
- 视频元信息字典（时长、大小、fps）

### 文件
- `video-people-counter/core/video_processor.py`

### 验收标准
```python
processor = VideoProcessor()
frame_path = processor.extract_middle_frame("test.mp4")
info = processor.get_video_info("test.mp4")
# frame_path 指向存在的图片文件
# info 包含 duration, file_size, fps, width, height
```

---

## 阶段 2：AI 人体检测模块

### 目标
加载 YOLO 模型，识别图片中的人数。

### 输入
- 图片文件路径

### 输出
- 检测到的人数（int）

### 文件
- `video-people-counter/core/people_detector.py`

### 验收标准
```python
detector = PeopleDetector()
count = detector.count_people("frame.jpg")
# count >= 0，为检测到的 person 数量
```

---

## 阶段 3：UI 界面搭建

### 目标
创建完整的桌面界面（先用模拟数据）。

### 子任务
1. 主窗口框架（工具栏、状态栏）
2. 导入视频按钮 + 文件对话框
3. 视频列表控件（缩略图 + 信息 + 复选框）
4. 筛选按钮栏（0~10 + 10+）
5. 导出按钮 + 文件夹选择 + 复制逻辑

### 文件
- `video-people-counter/main.py`
- `video-people-counter/ui/main_window.py`
- `video-people-counter/ui/video_list.py`
- `video-people-counter/ui/filter_bar.py`
- `video-people-counter/utils/file_utils.py`

### 验收标准
- 能用模拟数据走通全流程：导入 → 显示 → 筛选 → 导出

---

## 阶段 4：串联集成

### 目标
将核心模块（阶段 1、2）与 UI（阶段 3）连接。

### 子任务
1. 导入视频后自动提取中间帧
2. 自动调用人体检测
3. 显示处理进度条
4. 异步处理，不阻塞 UI

### 验收标准
- 导入 5 个测试视频 → 自动处理 → 显示人数 → 可筛选 → 可导出

---

## 阶段 5：打包收尾

### 目标
打包为独立 exe，添加错误处理。

### 子任务
1. 添加错误提示（文件损坏、格式不支持等）
2. 编写 PyInstaller 打包脚本
3. 生成 exe 文件
4. 编写用户使用说明

### 验收标准
- 在未安装 Python 的电脑上可运行 exe
- 有合理的错误提示
