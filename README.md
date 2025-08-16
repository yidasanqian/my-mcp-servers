# my-mcp-servers
Model Context Protocol Servers

## 项目介绍

本项目包含多个Model Context Protocol (MCP)服务器实现，用于提供各种工具和服务。

## 服务器列表

### 1. PostgreSQL MCP服务器
提供与PostgreSQL数据库交互的工具和资源。

### 2. 阿里云百炼生图API MCP服务器
```json
{
  "mcpServers": {
    "TextToImage": {
      "name": "通义qwen-文生图",
      "type": "streamableHttp",
      "description": "基于阿里云百炼文生图模型封装的 MCP服务器",
      "isActive": true,
      "baseUrl": "http://localhost:8000/mcp",
      "headers": {
        "Authorization": "Bearer ${BAILIAN_API_KEY}"
      }
    }
  }
}
```

## 开发说明

### 环境配置
```bash
# 使用uv安装依赖
uv sync
```

## 运行服务器
# 启动 PostgreSQL MCP 服务器
```bash
uv run mcp dev src/postgresql/pg_mcpserver.py
```
# 启动 阿里云百炼生图API MCP 服务器
```bash
uv run mcp dev src/gen_images/bailian_mcpserver.py
```