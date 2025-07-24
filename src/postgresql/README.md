# PostgreSQL MCP 服务器

这是一个功能完整的PostgreSQL MCP（Model Context Protocol）服务器，为AI助手提供数据库访问能力。

## 功能特性

### 📋 资源 (Resources)
- **schema://tables** - 获取数据库中所有表的列表
- **schema://table/{table_name}** - 获取指定表的详细模式信息
- **schema://indexes/{table_name}** - 获取指定表的索引信息

### 🔧 工具 (Tools)
- **execute_readonly_query** - 执行只读SQL查询（SELECT和WITH语句）
- **get_sample_data** - 获取表的样本数据
- **analyze_table_stats** - 分析表的统计信息

### 💡 提示 (Prompts)
- **数据探索分析** - 生成数据探索分析的提示
- **性能优化分析** - 生成性能优化分析的提示
- **业务洞察分析** - 生成业务洞察分析的提示
- **数据质量报告** - 生成数据质量报告的提示

## 安装和配置

### 1. 安装依赖

```bash
# 使用uv安装依赖
uv add psycopg2-binary mcp[cli]

# 或使用pip
pip install psycopg2-binary mcp[cli]
```

### 2. 配置数据库连接

复制环境变量配置文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置您的PostgreSQL连接信息：
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

### 3. 测试连接

运行测试脚本确保配置正确：
```bash
python tests/pg_mcpserver_test.py
```

## 使用方法

### 直接运行服务器
```bash
python src/postgresql/pg_mcpserver.py
```

### 开发模式（推荐）
```bash
uv run --env-file .env mcp dev src/postgresql/pg_mcpserver.py
```
#### mcp inspector connect command
```
uv --directory src/postgresql run pg_mcpserver.py
```
### 安装到Claude Desktop
```bash
uv run mcp install src/postgresql/pg_mcpserver.py
```

## 安全特性

- **只读访问**: 只允许执行SELECT和WITH查询
- **SQL注入防护**: 使用参数化查询
- **结果限制**: 查询结果最多返回100行
- **连接管理**: 每次查询后自动关闭数据库连接

## 示例用法

在AI助手中，您可以这样使用这个MCP服务器：

### 查看所有表
```
请显示数据库中的所有表
```

### 分析表结构
```
请分析 users 表的结构和约束
```

### 执行查询
```
查询 users 表中前10条记录
```

### 数据分析
```
请为 sales 表生成数据质量报告
```

## 文件结构

```
src/
└── postgresql/
    ├── __init__.py         # Python包初始化文件
    └── pg_mcpserver.py     # 主要的MCP服务器代码
tests/
├── __init__.py             # Python测试包初始化文件
└── pg_mcpserver_test.py    # 测试脚本
.env.example                # 环境变量配置示例
README.md                   # 说明文档
```

## 依赖项

- `psycopg2-binary` - PostgreSQL数据库适配器
- `mcp[cli]` - Model Context Protocol SDK

## 故障排除

### 连接问题
1. 确保PostgreSQL服务正在运行
2. 检查网络连接和防火墙设置
3. 验证数据库连接信息是否正确
4. 确认用户有足够的权限

### 权限问题
确保数据库用户至少具有以下权限：
- `CONNECT` - 连接数据库
- `USAGE` - 使用模式
- `SELECT` - 查询表数据

### 环境变量
确保正确设置了以下环境变量：
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

## 开发和扩展

要添加新功能，您可以：

1. **添加新资源**: 使用 `@mcp.resource()` 装饰器
2. **添加新工具**: 使用 `@mcp.tool()` 装饰器
3. **添加新提示**: 使用 `@mcp.prompt()` 装饰器

示例：
```python
@mcp.tool()
def my_custom_tool(param: str) -> str:
    """自定义工具的描述"""
    # 实现您的逻辑
    return result
```

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issues和Pull Requests来改进这个项目！
