#!/bin/bash

# 部署脚本用于构建和上传 Python 包到 PyPI

set -e  # 遇到错误时退出

echo "开始部署流程..."

# 检查是否安装了 uv
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到 uv 命令。请先安装 uv。"
    exit 1
fi


# 创建 dist 目录（如果不存在）
mkdir -p dist

# 清理旧的构建文件
echo "清理旧的构建文件..."
rm -rf dist/*

# 构建包
echo "正在构建包..."
uv build

# 检查是否成功构建了文件
if ls dist/*.{whl,tar.gz} 1> /dev/null 2>&1; then
    echo "构建成功完成。"
else
    echo "错误: 构建失败，未找到生成的包文件。"
    exit 1
fi

# 上传到 PyPI
echo "正在上传到 PyPI..."
uv run -m twine upload dist/*

echo "部署完成！"