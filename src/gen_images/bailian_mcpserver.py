"""
阿里云百炼生图API MCP服务器

此MCP服务器提供调用阿里云百炼平台生图API的工具。
"""

import json
import os
import time
from typing import Optional
import httpx
from mcp.server.fastmcp import FastMCP, Context
from starlette.datastructures import Headers


# 阿里云百炼baseurl
BAILIAN_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

# 创建全局MCP实例用于装饰器
mcp = FastMCP(name="阿里云百炼生图API MCP服务器")


def get_api_key_from_context(ctx: Context) -> str:
    """从MCP请求上下文或环境变量中获取API密钥"""

    # 首先尝试从环境变量获取（适用于两种模式）
    env_key = os.getenv("DASHSCOPE_API_KEY")
    if env_key:
        return env_key

    # HTTP模式：尝试从请求头获取
    if hasattr(ctx, "request_context") and ctx.request_context:
        try:
            headers: Headers = ctx.request_context.request.headers
            if "Authorization" in headers:
                return headers["Authorization"][7:]  # 移除 "Bearer " 前缀
        except Exception:
            pass

    raise ValueError(
        "未找到有效的API密钥。请设置 DASHSCOPE_API_KEY 环境变量，"
        "或在HTTP模式下通过Authorization头提供API密钥"
    )


def get_http_client(api_key: str) -> httpx.Client:
    """获取HTTP客户端"""
    return httpx.Client(
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        timeout=30.0,
    )


def get_http_aclient(api_key: str) -> httpx.Client:
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
    ctx: Context,
    prompt: str,
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
        with get_http_aclient(api_key) as client:
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
    ctx: Context, task_id: str, max_retries: int = 30, retry_interval: int = 3
) -> str:
    """
    根据任务ID查询图像生成结果

    Args:
        task_id: 图像生成任务的ID
        max_retries: 最大重试次数
        retry_interval: 重试间隔（秒）

    Returns:
        results: 任务结果列表，包括图像URL、prompt、部分任务执行失败报错信息等
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


@mcp.tool()
def image_edit_generation(
    ctx: Context,
    prompt: str,
    image: str,
    negative_prompt: Optional[str] = None,
) -> str:
    """
    调用阿里云百炼编辑图片API生成图像

    :param prompt: 正向提示词，用来描述生成图像中期望包含的元素和视觉特点。支持中英文，长度不超过800个字符，每个汉字/字母占一个字符，超过部分会自动截断。
    :type prompt: str
    :param image: 输入图像的URL。
    图像限制：
        - 图像格式：JPG、JPEG、PNG、BMP、TIFF、WEBP。
        - 图像分辨率：图像的宽度和高度范围为[512, 4096]像素。
        - 图像大小：不超过10MB。
        - URL地址中不能包含中文字符。

    输入图像说明：
        - 使用公网可访问URL
        - 支持 HTTP 或 HTTPS 协议。

    :type image: str
    :param negative_prompt: 反向提示词，用来描述不希望在画面中看到的内容，可以对画面进行限制。支持中英文，长度不超过500个字符，超过部分会自动截断。
    示例值：低分辨率、错误、最差质量、低质量、残缺、多余的手指、比例不良等。
    :type negative_prompt: Optional[str]

    Returns:
        image_url: 生成的图像URL
    """
    try:
        api_key = get_api_key_from_context(ctx)
    except ValueError as e:
        return f"认证错误: {str(e)}"

    # 构建请求数据
    data = {
        "model": "qwen-image-edit",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "image": image,
                        },
                        {"text": prompt},
                    ],
                }
            ]
        },
        "parameters": {
            "prompt_extend": True,
            "watermark": False,
        },
    }

    # 添加反向提示词（如果提供）
    if negative_prompt:
        data["parameters"]["negative_prompt"] = negative_prompt

    try:
        with get_http_client(api_key) as client:
            print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            response = client.post(
                f"{BAILIAN_BASE_URL}/services/aigc/multimodal-generation/generation",
                json=data,
            )
            response.raise_for_status()
            result = response.json()

            # 检查响应是否包含任务ID
            if "output" in result and "choices" in result["output"]:
                return json.dumps(
                    {
                        "image_url": result["output"]["choices"][0]["message"][
                            "content"
                        ][0]["image"],
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
        return f"编辑图像时发生未知错误: {str(e)}"


# 支持两种模式的启动脚本
def main():
    import sys

    if "--http" in sys.argv:
        print("启动HTTP模式（团队服务模式）")
        mcp.run(transport="streamable-http")
    else:
        print("启动stdio模式（个人使用模式）", file=sys.stderr)
        mcp.run()  # 默认stdio


if __name__ == "__main__":
    main()
