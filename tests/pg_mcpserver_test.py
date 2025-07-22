"""
测试PostgreSQL MCP服务器的基本功能
"""

import asyncio


from postgresql.pg_mcpserver import get_db_connection, mcp


async def test_mcp_server():
    """测试MCP服务器的基本功能"""
    print("=== PostgreSQL MCP 服务器测试 ===\n")

    # 1. 测试数据库连接
    print("1. 测试数据库连接...")
    try:
        conn = get_db_connection()
        conn.close()
        print("✅ 数据库连接成功！\n")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}\n")
        print("请检查以下配置:")
        print("- 数据库是否运行")
        print("- 连接信息是否正确")
        print("- 环境变量是否设置正确")
        return

    # 2. 测试MCP服务器配置
    print("2. 检查MCP服务器配置...")

    # 检查资源
    print("📋 已配置的资源:")
    for resource_name in await mcp.list_resources():
        print(f"   - {resource_name}")

    # 检查工具
    print("\n🔧 已配置的工具:")
    tools = await mcp.list_tools()
    for tool_name in tools:
        print(f"   - {tool_name}")

    # 检查提示
    print("\n💡 已配置的提示:")
    prompts = await mcp.list_prompts()
    for prompt_name in prompts:
        print(f"   - {prompt_name}")

    print("\n✅ MCP服务器配置完成！")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
