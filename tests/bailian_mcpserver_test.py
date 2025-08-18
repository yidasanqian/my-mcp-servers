"""
阿里云百炼生图API MCP服务器测试
"""

import asyncio

from gen_images.bailian_mcpserver import mcp


async def test_mcp_server():
    # 检查工具
    print("\n🔧 已配置的工具:")
    tools = await mcp.list_tools()
    for tool_name in tools:
        print(f"   - {tool_name}")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
