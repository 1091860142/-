@echo off
chcp 65001 >nul
echo ============================================
echo   视频人数统计工具 — 打包脚本
echo ============================================
echo.

REM 激活虚拟环境
call venv\Scripts\activate.bat

echo [1/3] 清理旧打包文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo [2/3] 开始打包（可能需要几分钟）...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "视频人数统计" ^
    --add-data "video-people-counter;video-people-counter" ^
    --hidden-import PySide6 ^
    --hidden-import cv2 ^
    --hidden-import ultralytics ^
    --hidden-import PIL ^
    --collect-all ultralytics ^
    video-people-counter\main.py

echo.
echo [3/3] 打包完成！
echo 可执行文件位于: dist\视频人数统计.exe
echo.
pause
