# 第三方工具封装
from typing import Dict, Any, Optional, List
import asyncio
import json
import requests
import subprocess
import os
from utils.logging_config import get_logger

# 尝试导入MCP包装器
try:
    from models.mcp_wrapper import MCPWrapper
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP wrapper not available.")

logger = get_logger(__name__)

class ToolWrapper:
    def __init__(self):
        self.registered_tools = {}
        self._register_default_tools()
    
    def register_tool(self, tool_name: str, tool_function):
        """注册工具"""
        self.registered_tools[tool_name] = tool_function
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        logger.info(f"开始调用工具: {tool_name}, 参数: {parameters}")
        try:
            if tool_name in self.registered_tools:
                tool_func = self.registered_tools[tool_name]
                
                # 检查是否是异步函数
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**parameters)
                else:
                    result = tool_func(**parameters)
                
                logger.info(f"工具调用成功: {tool_name}, 结果: {result}")
                return {
                    "success": True,
                    "result": result,
                    "tool_name": tool_name
                }
            else:
                error_msg = f"工具未找到: {tool_name}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "tool_name": tool_name
                }
                
        except Exception as e:
            logger.error(f"工具调用失败: {tool_name}, 错误: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    def _register_default_tools(self):
        """注册默认工具"""
        # 搜索工具
        self.register_tool("search_tool", self._search_tool)
        
        # Bing搜索工具
        self.register_tool("bing_search", self._bing_search_tool)
        
        # 计算器工具
        self.register_tool("calculator_tool", self._calculator_tool)
        
        # 文件操作工具
        self.register_tool("file_tool", self._file_tool)
        
        # API 请求工具
        self.register_tool("api_tool", self._api_tool)
        
        # 系统命令工具
        self.register_tool("system_tool", self._system_tool)
        
        # MCP工具
        if MCP_AVAILABLE:
            self.mcp_wrapper = MCPWrapper()
            # 注册MCP工具调用方法
            self.register_tool("mcp_tool", self._mcp_tool)
        else:
            self.mcp_wrapper = None
    
    def _search_tool(self, query: str, **kwargs) -> str:
        """搜索工具（模拟实现）"""
        # 这里应该连接到实际的搜索 API
        return f"搜索结果：{query} 的相关信息"
    
    def _bing_search_tool(self, query: str, **kwargs) -> str:
        """Bing搜索工具"""
        try:
            # 从环境变量获取Bing API密钥
            api_key = os.getenv("BING_API_KEY")
            if not api_key:
                return "错误：未配置BING_API_KEY环境变量"
            
            # Bing搜索API端点
            endpoint = "https://api.bing.microsoft.com/v7.0/search"
            
            # 请求参数
            params = {
                "q": query,
                "count": 5,  # 返回结果数量
                "offset": 0,
                "mkt": "zh-CN"  # 市场代码
            }
            
            # 请求头
            headers = {
                "Ocp-Apim-Subscription-Key": api_key
            }
            
            # 发送请求
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析响应
            search_results = response.json()
            web_pages = search_results.get("webPages", {}).get("value", [])
            
            # 格式化结果
            if not web_pages:
                return f"Bing搜索结果：未找到与'{query}'相关的结果"
            
            result_text = f"Bing搜索结果：\n"
            for i, page in enumerate(web_pages[:3], 1):  # 只返回前3个结果
                result_text += f"{i}. {page.get('name', '')}\n"
                result_text += f"   URL: {page.get('url', '')}\n"
                result_text += f"   描述: {page.get('snippet', '')}\n\n"
            
            return result_text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Bing搜索请求错误: {str(e)}")
            return f"错误：Bing搜索请求失败 - {str(e)}"
        except Exception as e:
            logger.error(f"Bing搜索错误: {str(e)}")
            return f"错误：Bing搜索失败 - {str(e)}"
    
    def _calculator_tool(self, expression: str, **kwargs) -> str:
        """计算器工具"""
        try:
            # 安全地评估数学表达式
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "错误：表达式包含不允许的字符"
            
            result = eval(expression)
            return f"计算结果：{expression} = {result}"
        except Exception as e:
            return f"计算错误：{str(e)}"
    
    def _file_tool(self, operation: str, file_path: str, content: str = None, **kwargs) -> str:
        """文件操作工具"""
        try:
            if operation == "read":
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    return f"文件不存在：{file_path}"
            
            elif operation == "write":
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content or "")
                return f"文件写入成功：{file_path}"
            
            elif operation == "append":
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(content or "")
                return f"文件追加成功：{file_path}"
            
            else:
                return f"不支持的操作：{operation}"
                
        except Exception as e:
            return f"文件操作错误：{str(e)}"
    
    def _api_tool(self, url: str, method: str = "GET", data: Dict[str, Any] = None, **kwargs) -> str:
        """API 请求工具"""
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                return f"不支持的 HTTP 方法：{method}"
            
            return f"API 响应：状态码 {response.status_code}, 内容：{response.text[:200]}"
            
        except Exception as e:
            return f"API 请求错误：{str(e)}"
    
    def _system_tool(self, command: str, **kwargs) -> str:
        """系统命令工具"""
        try:
            # 安全检查：只允许安全的命令
            safe_commands = ["ls", "pwd", "echo", "date", "whoami"]
            base_command = command.split()[0] if command else ""
            
            if base_command not in safe_commands:
                return f"命令 '{base_command}' 不在安全列表中"
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                return f"命令执行成功：{result.stdout}"
            else:
                return f"命令执行失败：{result.stderr}"
                
        except Exception as e:
            return f"系统命令错误：{str(e)}"
    
    async def _mcp_tool(self, tool_name: str, **kwargs) -> str:
        """MCP工具调用"""
        if not self.mcp_wrapper or not self.mcp_wrapper.is_available():
            return "MCP工具不可用，请检查MCP SDK是否已安装"
        
        try:
            result = await self.mcp_wrapper.call_mcp_tool(tool_name, kwargs)
            if result.get("success"):
                return result.get("result", "MCP工具调用成功但无返回结果")
            else:
                return f"MCP工具调用失败：{result.get('error', '未知错误')}"
        except Exception as e:
            return f"MCP工具调用异常：{str(e)}"
    
    async def call_tool_async(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """异步调用工具"""
        try:
            if tool_name in self.registered_tools:
                tool_func = self.registered_tools[tool_name]
                
                # 检查是否是异步函数
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**parameters)
                else:
                    # 在线程池中运行同步函数
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, tool_func, **parameters)
                
                return {
                    "success": True,
                    "result": result,
                    "tool_name": tool_name
                }
            else:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found",
                    "tool_name": tool_name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    def list_available_tools(self) -> List[str]:
        """列出可用的工具"""
        tools = list(self.registered_tools.keys())
        
        # 如果MCP可用，添加MCP工具信息
        if self.mcp_wrapper and self.mcp_wrapper.is_available():
            tools.append("mcp_tool")
            
        return tools
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """获取工具信息"""
        if tool_name in self.registered_tools:
            tool_func = self.registered_tools[tool_name]
            return {
                "name": tool_name,
                "function": tool_func.__name__,
                "doc": tool_func.__doc__ or "No documentation available"
            }
        elif tool_name == "mcp_tool" and self.mcp_wrapper and self.mcp_wrapper.is_available():
            return {
                "name": "mcp_tool",
                "function": "_mcp_tool",
                "doc": "MCP工具调用，可以调用外部MCP服务器提供的工具"
            }
        else:
            return {"error": f"Tool '{tool_name}' not found"}