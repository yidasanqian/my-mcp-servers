"""
阿里云百炼生图API MCP服务器

此MCP服务器提供调用阿里云百炼平台生图API的工具。
"""

import json
import time
from typing import Optional
import httpx
from mcp.server.fastmcp import FastMCP, Context
from starlette.datastructures import Headers

# 创建MCP服务器实例
mcp = FastMCP("阿里云百炼生图API MCP服务器")

# 阿里云百炼baseurl
BAILIAN_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"


def get_api_key_from_context(ctx: Context) -> str:
    """从MCP请求上下文中获取API密钥"""

    headers: Headers = ctx.request_context.request.headers
    # 如果没有找到认证头，抛出异常
    if "Authorization" not in headers:
        raise ValueError("未找到有效的API密钥，请在MCP客户端配置中设置Authorization头")
    return headers["Authorization"][7:]  # 移除 "Bearer " 前缀


def get_http_client(api_key: str) -> httpx.Client:
    """获取HTTP客户端"""
    return httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        },
        timeout=30.0,
    )


@mcp.tool()
def generate_image(
    prompt: str,
    ctx: Context,
    size: str = "1328*1328",
    n: int = 1,
    prompt_extend: bool = True,
    watermark: bool = False,
    negative_prompt: Optional[str] = None,
) -> str:
    """
    调用阿里云百炼生图API生成图像

    Args:
        prompt: 正向提示词，用来描述生成图像中期望包含的元素和视觉特点
        ctx: MCP上下文对象
        size: 输出图像的分辨率，格式为宽*高。：
            默认为1328*1328,可选的分辨率及其对应的图像宽高比例为:
            - "1664*928": approximately 16:9
            - "1472*1140": approximately 4:3
            - "1328*1328": 1:1 (square)
            - "1140*1472": approximately 3:4
            - "928*1664": approximately 9:16
        n: 生成图片的数量。当前仅支持生成1张图像
        prompt_extend: 是否开启prompt智能改写
        watermark: 是否添加水印标识
        negative_prompt: 反向提示词，用来描述不希望在画面中看到的内容

    Returns:
        任务ID和初始状态的JSON格式字符串
    """
    try:
        api_key = get_api_key_from_context(ctx)
    except ValueError as e:
        return f"认证错误: {str(e)}"

    # 构建请求数据
    data = {
        "model": "qwen-image",
        "input": {
            "prompt": prompt,
        },
        "parameters": {
            "size": size,
            "n": n,
            "prompt_extend": prompt_extend,
            "watermark": watermark,
        },
    }

    # 添加反向提示词（如果提供）
    if negative_prompt:
        data["input"]["negative_prompt"] = negative_prompt

    try:
        with get_http_client(api_key) as client:
            response = client.post(
                f"{BAILIAN_BASE_URL}/services/aigc/text2image/image-synthesis",
                json=data,
            )
            response.raise_for_status()
            result = response.json()

            # 检查响应是否包含任务ID
            if "output" in result and "task_id" in result["output"]:
                return json.dumps(
                    {
                        "task_id": result["output"]["task_id"],
                        "task_status": result["output"]["task_status"],
                        "request_id": result.get("request_id", ""),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            else:
                return f"API响应错误: {result}"

    except httpx.RequestError as e:
        return f"请求错误: {str(e)}"
    except httpx.HTTPStatusError as e:
        return f"HTTP错误: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"生成图像时发生未知错误: {str(e)}"


@mcp.tool()
def get_image_generation_result(
    task_id: str, ctx: Context, max_retries: int = 30, retry_interval: int = 3
) -> str:
    """
    根据任务ID查询图像生成结果

    Args:
        task_id: 图像生成任务的ID
        ctx: MCP上下文对象
        max_retries: 最大重试次数
        retry_interval: 重试间隔（秒）

    Returns:
        图像生成结果的JSON格式字符串
    """
    try:
        api_key = get_api_key_from_context(ctx)
    except ValueError as e:
        return f"认证错误: {str(e)}"

    try:
        with get_http_client(api_key) as client:
            for _ in range(max_retries):
                response = client.get(
                    f"{BAILIAN_BASE_URL}/tasks/{task_id}",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                response.raise_for_status()
                result = response.json()

                # 检查任务状态
                task_status = result.get("output", {}).get("task_status", "UNKNOWN")

                # 如果任务完成或失败，返回结果
                if task_status in ["SUCCEEDED", "FAILED", "CANCELED"]:
                    return json.dumps(result, ensure_ascii=False, indent=2)

                # 如果任务仍在进行中，等待后重试
                time.sleep(retry_interval)

            # 超过最大重试次数
            return f"查询超时: 任务 {task_id} 仍未完成"

    except httpx.RequestError as e:
        return f"请求错误: {str(e)}"
    except httpx.HTTPStatusError as e:
        return f"HTTP错误: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"查询任务结果时发生未知错误: {str(e)}"


def main():
    """运行MCP服务器"""
    print("启动 阿里云百炼生图API MCP 服务器...")
    print("API Key 将从MCP客户端的Authorization头获取")

    # 启动MCP服务器，使用streamable-http传输方式
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
