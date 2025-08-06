#!/usr/bin/env python3
"""
MCP服务器示例

这是一个简单的MCP服务器实现，用于演示如何创建MCP工具。
"""

from mcp.server.fastmcp import FastMCP
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# 创建FastMCP实例
mcp = FastMCP("OncallAgentMCP")

@mcp.tool()
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """两个数字相加"""
    return a + b

@mcp.tool()
def get_weather_info(city: str) -> str:
    """获取天气信息（模拟实现）"""
    # 这里应该连接到实际的天气API
    return f"{city}的天气信息：晴朗，温度25°C"

@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """搜索知识库（模拟实现）"""
    # 这里应该连接到实际的知识库
    return f"知识库搜索结果：与'{query}'相关的知识内容..."

@mcp.tool()
def execute_system_command(command: str) -> str:
    """执行系统命令（模拟实现）"""
    # 出于安全考虑，这里只是模拟实现
    return f"执行系统命令：{command} (模拟结果)"

if __name__ == "__main__":
    print("启动MCP服务器...")
    # 运行MCP服务器
    mcp.run(transport='stdio')