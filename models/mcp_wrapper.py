# MCP工具包装类
from typing import Dict, Any, Optional, List
import asyncio
import json
import os
from utils.logging_config import get_logger

# 尝试导入MCP SDK
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP SDK not available. Please install with: pip install mcp")

logger = get_logger(__name__)

class MCPWrapper:
    def __init__(self, server_command: Optional[List[str]] = None):
        self.mcp_available = MCP_AVAILABLE
        self.server_command = server_command or ["python", "scripts/mcp_server_example.py"]
        if not self.mcp_available:
            logger.warning("MCP SDK not available. MCP tools will not function.")
    
    async def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP工具"""
        logger.info(f"开始调用MCP工具: {tool_name}, 参数: {parameters}")
        if not self.mcp_available:
            error_msg = "MCP SDK不可用"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "tool_name": tool_name
            }
        
        try:
            # 创建MCP客户端会话
            logger.info(f"创建MCP客户端会话，服务器命令: {self.server_command}")
            async with stdio_client(self.server_command) as (read, write):
                async with ClientSession(read, write) as session:
                    # 获取可用工具列表
                    logger.info("获取MCP可用工具列表")
                    tools = await session.list_tools()
                    
                    # 查找指定的工具
                    target_tool = None
                    for tool in tools:
                        if tool.name == tool_name:
                            target_tool = tool
                            break
                    
                    if not target_tool:
                        error_msg = f"MCP工具未找到: {tool_name}"
                        logger.error(error_msg)
                        return {
                            "success": False,
                            "error": error_msg,
                            "tool_name": tool_name
                        }
                    
                    # 调用工具
                    logger.info(f"调用MCP工具: {tool_name}")
                    result = await session.call_tool(tool_name, parameters)
                    
                    # 处理结果
                    logger.info(f"MCP工具调用完成: {tool_name}")
                    if result:
                        # 如果结果包含文本内容，提取文本
                        if hasattr(result, 'content') and result.content:
                            text_content = ""
                            for item in result.content:
                                if isinstance(item, TextContent):
                                    text_content += item.text + "\n"
                            result_text = text_content.strip()
                            logger.info(f"MCP工具调用成功: {tool_name}, 结果: {result_text}")
                            return {
                                "success": True,
                                "result": result_text,
                                "tool_name": tool_name
                            }
                        else:
                            result_str = str(result)
                            logger.info(f"MCP工具调用成功: {tool_name}, 结果: {result_str}")
                            return {
                                "success": True,
                                "result": result_str,
                                "tool_name": tool_name
                            }
                    else:
                        error_msg = "MCP工具调用未返回结果"
                        logger.error(error_msg)
                        return {
                            "success": False,
                            "error": error_msg,
                            "tool_name": tool_name
                        }
                        
        except Exception as e:
            logger.error(f"MCP工具调用失败: {tool_name}, 错误: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    def list_mcp_tools(self) -> List[str]:
        """列出可用的MCP工具"""
        if not self.mcp_available:
            return []
            
        try:
            # 这需要一个运行中的MCP服务器来获取工具列表
            # 在实际实现中，可能需要配置MCP服务器地址等信息
            return ["mcp_time_tool", "mcp_calculator_tool"]  # 示例工具列表
        except Exception as e:
            logger.error(f"Failed to list MCP tools: {str(e)}")
            return []
    
    def is_available(self) -> bool:
        """检查MCP是否可用"""
        return self.mcp_available