# my-mcp-servers

Model Context Protocol Servers

## 项目介绍

本项目包含多个Model Context Protocol (MCP)服务器实现，用于提供各种工具和服务。

## 服务器列表

### 1. PostgreSQL MCP服务器

提供与PostgreSQL数据库交互的工具和资源。

### 2. 阿里云百炼生图API MCP服务器

支持两种部署模式：

### 个人使用（推荐）

```json
{
  "mcpServers": {
    "bailian-image-gen": {
      "command": "uvx",
      "args": [
        "--from",
        "my-mcp-servers",
        "bailian-mcp-server"
      ],
      "env": {
        "DASHSCOPE_API_KEY": "sk-your-api-key"
      }
    }
  }
}
```

### 团队部署

1. 部署服务器：

```bash
docker-compose up -d
```

1. cherry studio配置：

```json
{
  "mcpServers": {
    "bailian-image-gen": {
      "type": "streamableHttp",
      "url": "http://localhost:8000/mcp",
      "headers": {
        "Authorization": "Bearer ${DASHSCOPE_API_KEY}"
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
