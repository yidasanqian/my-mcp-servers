@echo off
chcp 65001 >nul

REM 部署脚本用于构建和上传 Python 包到 PyPI

setlocal enabledelayedexpansion

echo 开始部署流程...

REM 检查是否安装了 uv
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 uv 命令。请先安装 uv。
    exit /b 1
)

REM 创建 dist 目录（如果不存在）
if not exist dist mkdir dist

REM 清理旧的构建文件
echo 清理旧的构建文件...
if exist dist\* (
    rd /s /q dist
    mkdir dist
)

REM 构建包
echo 正在构建包...
uv build

REM 检查是否成功构建了文件
if exist "dist\*.whl" (
    set build_success=1
) else if exist "dist\*.tar.gz" (
    set build_success=1
) else (
    set build_success=0
)

if !build_success! equ 1 (
    echo 构建成功完成。
) else (
    echo 错误: 构建失败，未找到生成的包文件。
    exit /b 1
)

REM 上传到 PyPI
echo 正在上传到 PyPI...
uv run -m twine upload dist\*

echo 部署完成！