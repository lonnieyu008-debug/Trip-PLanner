"""
高德地图 MCP 工具层（LangGraph 版）

通过 langchain-mcp-adapters 连接 amap-mcp-server，
自动将所有 MCP 工具转换为标准 LangChain tool，供 Agent 使用。

单例模式：全局共享一个 MultiServerMCPClient 实例，
在 FastAPI lifespan 中初始化和关闭，避免每次请求重复
启动 uvx amap-mcp-server 子进程带来的资源开销。
"""

import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from ..config import get_settings

# 全局单例
_mcp_client: MultiServerMCPClient | None = None


def get_mcp_client() -> MultiServerMCPClient:
    """获取全局 MCP 客户端单例（需在 lifespan 中提前初始化）"""
    if _mcp_client is None:
        raise RuntimeError("MCP 客户端尚未初始化，请确保 FastAPI lifespan 已执行")
    return _mcp_client


async def init_mcp_client() -> None:
    """
    初始化全局 MCP 客户端，在 FastAPI startup 时调用一次。
    启动 uvx amap-mcp-server 子进程并保持长连接。
    """
    global _mcp_client
    settings = get_settings()

    if not settings.amap_api_key:
        raise ValueError("AMAP_API_KEY 未配置，请在 .env 文件中设置")

    _mcp_client = MultiServerMCPClient(
        {
            "amap": {
                "command": "uvx",
                "args": ["amap-mcp-server"],
                "env": {
                    **os.environ,  # 继承当前环境变量
                    "AMAP_MAPS_API_KEY": settings.amap_api_key,
                },
                "transport": "stdio",
            }
        }
    )
    print("✅ MCP 客户端初始化完成（amap-mcp-server 已连接）")


async def close_mcp_client() -> None:
    """
    关闭全局 MCP 客户端，在 FastAPI shutdown 时调用。
    释放与 amap-mcp-server 子进程的连接。
    """
    global _mcp_client
    if _mcp_client is not None:
        # MultiServerMCPClient 支持 async context manager，
        # 直接置 None 让 GC 回收，子进程随之终止
        _mcp_client = None
        print("👋 MCP 客户端已关闭")
