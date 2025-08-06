#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志功能的脚本
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from models.tool_wrappers import ToolWrapper
from models.mcp_wrapper import MCPWrapper
from core.react_executor.react_agent import ReactAgent

async def test_tool_wrapper_logging():
    """测试工具包装器的日志功能"""
    print("=== 测试工具包装器日志功能 ===")
    tool_wrapper = ToolWrapper()
    
    # 测试调用计算器工具
    result = await tool_wrapper.call_tool("calculator_tool", {"expression": "2+2"})
    print(f"计算器工具调用结果: {result}")
    
    # 测试调用不存在的工具
    result = await tool_wrapper.call_tool("nonexistent_tool", {})
    print(f"不存在工具调用结果: {result}")

async def test_mcp_wrapper_logging():
    """测试MCP包装器的日志功能"""
    print("\n=== 测试MCP包装器日志功能 ===")
    mcp_wrapper = MCPWrapper()
    
    # 检查MCP是否可用
    if mcp_wrapper.is_available():
        print("MCP可用，测试调用MCP工具")
        # 测试调用MCP工具（这里使用一个示例工具名）
        result = await mcp_wrapper.call_mcp_tool("get_current_time", {})
        print(f"MCP工具调用结果: {result}")
    else:
        print("MCP不可用，跳过MCP工具测试")

async def test_react_agent_logging():
    """测试ReactAgent的日志功能"""
    print("\n=== 测试ReactAgent日志功能 ===")
    agent = ReactAgent()
    
    # 测试执行一个简单的步骤
    result = await agent._execute_action(
        step="计算2+2的结果",
        thought="需要使用计算器工具来计算2+2的结果"
    )
    print(f"ReactAgent执行结果: {result}")

async def main():
    """主函数"""
    print("开始测试日志功能...")
    
    # 测试工具包装器
    await test_tool_wrapper_logging()
    
    # 测试MCP包装器
    await test_mcp_wrapper_logging()
    
    # 测试ReactAgent
    await test_react_agent_logging()
    
    print("\n日志功能测试完成！")

if __name__ == "__main__":
    asyncio.run(main())