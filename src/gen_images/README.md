# 阿里云百炼生图 MCP 服务器

一个 Model Context Protocol 服务器，提供阿里云百炼平台的图像生成和编辑功能。该服务器使LLM能够调用阿里云百炼API来生成、编辑图像，支持多种图像分辨率和自定义参数。

## 可用工具

### `generate_image` - 生成图像

使用文本提示词生成图像。

**必需参数：**

- `prompt` (string): 正向提示词，描述期望生成的图像内容

**可选参数：**

- `size` (string): 输出图像分辨率，默认 "1328*1328"
  - "1664*928": 约 16:9 宽屏
  - "1472*1140": 约 4:3
  - "1328*1328": 1:1 正方形
  - "1140*1472": 约 3:4
  - "928*1664": 约 9:16 竖屏
- `n` (int): 生成图片数量，当前仅支持 1
- `prompt_extend` (bool): 是否开启prompt智能改写，默认 true
- `watermark` (bool): 是否添加水印标识，默认 false
- `negative_prompt` (string): 反向提示词，描述不希望出现的内容

### `get_image_generation_result` - 获取生成结果

根据任务ID查询图像生成进度和结果。

**必需参数：**

- `task_id` (string): 图像生成任务ID

**可选参数：**

- `max_retries` (int): 最大重试次数，默认 30
- `retry_interval` (int): 重试间隔秒数，默认 3

### `image_edit_generation` - 编辑图像

基于现有图像和文本提示生成新的编辑版本。

**必需参数：**

- `prompt` (string): 编辑指令提示词
- `image` (string): 输入图像的URL

**可选参数：**

- `negative_prompt` (string): 反向提示词

## 安装

### 使用 uv (推荐)

使用 [uv](https://docs.astral.sh/uv/) 时无需特定安装。我们将使用 [uvx](https://docs.astral.sh/uv/guides/tools/) 直接运行 MCP 服务器。

### 使用 pip

或者，您可以通过 pip 安装：

```bash
pip install -e .
```

安装后，可以作为脚本运行：

```bash
python -m src.gen_images.bailian_mcpserver
```

## 配置

### 身份验证

您需要阿里云百炼平台的 API 密钥。有两种配置方式：

1. **环境变量** (推荐)：

   ```bash
   export DASHSCOPE_API_KEY="your_api_key_here"
   ```

2. **HTTP 模式下的 Authorization 头**：

   ```text
   Authorization: Bearer your_api_key_here
   ```

### 为 Claude.app 配置

将以下内容添加到您的 Claude 设置：

```json
{
  "mcpServers": {
    "bailian-image": {
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

### 为 VS Code 配置

[![Install in VS Code](https://img.shields.io/badge/Install%20in-VS%20Code-blue?style=for-the-badge&logo=visualstudiocode)](vscode:mcp/install?%7B%22mcp%22%3A%7B%22servers%22%3A%7B%22bailian-image%22%3A%7B%22type%22%3A%22stdio%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22my-mcp-servers%22%2C%22bailian-mcp-server%22%5D%2C%22env%22%3A%7B%22DASHSCOPE_API_KEY%22%3A%22sk-your-api-key%22%7D%7D%7D%7D%7D)

在工作区中创建 `.vscode/mcp.json` 文件：

```json
{
  "mcp": {
    "servers": {
      "bailian-image": {
        "type": "stdio",
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
}
```

## 示例交互

### 1. 生成图像

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "一只可爱的橙色小猫坐在阳光明媚的窗台上",
    "size": "1328*1328",
    "watermark": false
  }
}
```

响应：

```json
{
  "task_id": "task_12345678",
  "task_status": "PENDING",
  "request_id": "req_87654321"
}
```

### 2. 查询生成结果

```json
{
  "name": "get_image_generation_result",
  "arguments": {
    "task_id": "task_12345678"
  }
}
```

响应：

```json
{
  "output": {
    "task_id": "task_12345678",
    "task_status": "SUCCEEDED",
    "results": [
      {
        "url": "https://example.com/generated_image.jpg"
      }
    ]
  }
}
```

### 3. 编辑图像

```json
{
  "name": "image_edit_generation",
  "arguments": {
    "prompt": "将猫的颜色改为白色",
    "image": "https://example.com/original_image.jpg"
  }
}
```

响应：

```json
{
  "image_url": "https://example.com/edited_image.jpg",
  "request_id": "req_11223344"
}
```

## 运行模式

该服务器支持两种运行模式：

### Stdio 模式 (默认)

```bash
python -m src.gen_images.bailian_mcpserver
```

### HTTP 模式 (团队服务)

```bash
python -m src.gen_images.bailian_mcpserver --http
```

## 调试

您可以使用 MCP 检查器来调试服务器：

```bash
npx @modelcontextprotocol/inspector python -m src.gen_images.bailian_mcpserver
```

## Claude 问题示例

1. "生成一张1328x1328像素的猫咪图片"
2. "创建一个日落海滩场景的图像，不要包含人物"
3. "编辑这张图片，将天空改为蓝色"
4. "生成一个16:9宽屏比例的城市夜景"

## Docker 部署

项目包含 Docker 配置文件，可以使用 Docker 部署：

```bash
cd src/gen_images
docker-compose up -d
```

## 贡献

我们鼓励贡献来帮助扩展和改进阿里云百炼生图 MCP 服务器。无论您想添加新的图像处理工具、增强现有功能，还是改进文档，您的贡献都是宝贵的。

欢迎提交 Pull Request！请随时贡献新想法、错误修复或增强功能，让这个 MCP 服务器更加强大和有用。

## 许可证

该项目采用 MIT 许可证。这意味着您可以自由使用、修改和分发软件，但需遵守 MIT 许可证的条款和条件。更多详情请参见项目仓库中的 LICENSE 文件。
