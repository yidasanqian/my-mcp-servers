# 🚀 my-mcp-servers

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-orange.svg)

一个包含多个Model Context Protocol (MCP)服务器实现的开源项目，为AI助手提供数据库访问、图像生成等功能集成。

## ✨ 特性

- 🗄️ **PostgreSQL集成** - 完整的数据库访问和分析能力
- 🎨 **AI图像生成** - 基于阿里云百炼平台的图像生成与编辑
- 🔒 **安全设计** - 只读数据库访问，SQL注入防护
- 🏗️ **模块化架构** - 独立的服务器模块，易于扩展
- 📦 **即装即用** - 支持uv和pip安装方式

## 🛠️ 服务器列表

### 📊 PostgreSQL MCP服务器

提供与PostgreSQL数据库交互的完整功能：

**核心功能：**
- 📋 **资源管理** - 获取表结构、索引信息
- 🔍 **查询执行** - 安全的只读SQL查询
- 📈 **数据分析** - 表统计信息和样本数据
- 💡 **智能提示** - 数据探索、性能优化、业务洞察分析

**安全特性：**
- 只读访问（仅支持SELECT和WITH查询）
- SQL注入防护
- 查询结果限制（最多100行）
- 自动连接管理

### 🎨 阿里云百炼生图API MCP服务器

基于阿里云百炼平台的图像生成和编辑服务：

**核心功能：**
- 🖼️ **图像生成** - 基于文本提示生成高质量图像
- ✏️ **图像编辑** - 智能图像修改和优化
- 📏 **多种分辨率** - 支持1:1、16:9、4:3等多种比例
- 🎯 **智能提示** - 自动提示词优化和反向提示

**技术特性：**
- 异步任务处理
- 多种输出格式
- 水印控制
- Docker部署支持

## 🚀 快速开始

### 环境要求

- Python 3.8+
- PostgreSQL (用于数据库服务器)
- 阿里云百炼API密钥 (用于图像生成服务器)

### 安装

#### 使用 uv (推荐)

```bash
# 无需特定安装，使用uvx直接运行
uvx --from my-mcp-servers postgresql-mcp-server
uvx --from my-mcp-servers bailian-mcp-server
```

#### 使用 pip

```bash
pip install -e .
```

### 配置示例

#### Claude.app 配置

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "uvx",
      "args": ["--from", "my-mcp-servers", "postgresql-mcp-server"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "your_database",
        "DB_USER": "your_user",
        "DB_PASSWORD": "your_password"
      }
    },
    "bailian-image": {
      "command": "uvx",
      "args": ["--from", "my-mcp-servers", "bailian-mcp-server"],
      "env": {
        "DASHSCOPE_API_KEY": "your_api_key"
      }
    }
  }
}
```

## 📖 使用指南

### PostgreSQL服务器

与AI助手对话示例：
- "显示数据库中的所有表"
- "分析users表的结构"
- "查询sales表的前10条记录"
- "为orders表生成数据质量报告"

### 图像生成服务器

与AI助手对话示例：
- "生成一张1328x1328像素的猫咪图片"
- "创建一个16:9比例的城市夜景"
- "编辑这张图片，将天空改为蓝色"

## 🏗️ 项目结构

```
my-mcp-servers/
├── src/
│   ├── postgresql/          # PostgreSQL MCP服务器
│   │   ├── pg_mcpserver.py
│   │   └── README.md
│   └── gen_images/          # 阿里云百炼生图MCP服务器
│       ├── bailian_mcpserver.py
│       ├── docker-compose.yml
│       ├── Dockerfile
│       └── README.md
├── tests/                   # 测试文件
├── script/                  # 部署脚本
└── pyproject.toml          # 项目配置
```

## 🤝 贡献指南

我们欢迎各种形式的贡献：

1. **🐛 报告问题** - 发现bug请提交issue
2. **💡 功能建议** - 有好想法欢迎讨论
3. **🔧 代码贡献** - 提交Pull Request
4. **📚 文档改进** - 帮助完善文档

### 开发环境

```bash
# 克隆仓库
git clone https://github.com/yidasanqian/my-mcp-servers.git
cd my-mcp-servers

# 安装依赖
uv sync

# 运行测试
uv run pytest
```

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)。

## 🔗 相关链接

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [阿里云百炼平台](https://bailian.console.aliyun.com/)
- [PostgreSQL](https://www.postgresql.org/)

## 💬 联系与支持

- 📧 Issues: [GitHub Issues](https://github.com/yidasanqian/my-mcp-servers/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/yidasanqian/my-mcp-servers/discussions)

---

⭐ 如果这个项目对您有帮助，请给个星标支持！