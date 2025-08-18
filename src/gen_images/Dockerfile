FROM python:3.11-slim

ARG PIP_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"

# 设置工作目录
WORKDIR /app

# 安装uv
RUN pip config set global.index-url $PIP_INDEX ; \
    pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock README.md ./
COPY src/gen_images/bailian_mcpserver.py ./gen_images/bailian_mcpserver.py

# 安装依赖
RUN uv sync --frozen

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "gen_images/bailian_mcpserver.py", "--http"]