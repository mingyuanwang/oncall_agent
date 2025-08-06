#!/usr/bin/env python3
"""
MCP工具调用测试脚本

用于测试MCP工具调用功能。
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.tool_wrappers import ToolWrapper

async def test_mcp_tool():
    """测试MCP工具调用"""
    print("测试MCP工具调用...")
    
    # 创建工具包装器实例
    tool_wrapper = ToolWrapper()
    
    # 检查MCP是否可用
    if not tool_wrapper.mcp_wrapper or not tool_wrapper.mcp_wrapper.is_available():
        print("MCP工具不可用，请检查MCP SDK是否已安装")
        return
    
    # 测试调用MCP工具
    print("调用MCP工具: get_current_time")
    result = await tool_wrapper.call_tool_async("mcp_tool", {
        "tool_name": "get_current_time"
    })
    print(f"结果: {result}")
    
    print("\n调用MCP工具: add_numbers")
    result = await tool_wrapper.call_tool_async("mcp_tool", {
        "tool_name": "add_numbers",
        "a": 10,
        "b": 20
    })
    print(f"结果: {result}")
    
    print("\n调用MCP工具: get_weather_info")
    result = await tool_wrapper.call_tool_async("mcp_tool", {
        "tool_name": "get_weather_info",
        "city": "北京"
    })
    print(f"结果: {result}")

if __name__ == "__main__":
    asyncio.run(test_mcp_tool())