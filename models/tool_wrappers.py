# 第三方工具封装
from typing import Dict, Any, Optional, List
import asyncio
import json
import requests
import subprocess
import os

class ToolWrapper:
    def __init__(self):
        self.registered_tools = {}
        self._register_default_tools()
    
    def register_tool(self, tool_name: str, tool_function):
        """注册工具"""
        self.registered_tools[tool_name] = tool_function
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        try:
            if tool_name in self.registered_tools:
                tool_func = self.registered_tools[tool_name]
                
                # 检查是否是异步函数
                if asyncio.iscoroutinefunction(tool_func):
                    result = await tool_func(**parameters)
                else:
                    result = tool_func(**parameters)
                
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
    
    def _register_default_tools(self):
        """注册默认工具"""
        # 搜索工具
        self.register_tool("search_tool", self._search_tool)
        
        # 计算器工具
        self.register_tool("calculator_tool", self._calculator_tool)
        
        # 文件操作工具
        self.register_tool("file_tool", self._file_tool)
        
        # API 请求工具
        self.register_tool("api_tool", self._api_tool)
        
        # 系统命令工具
        self.register_tool("system_tool", self._system_tool)
    
    def _search_tool(self, query: str, **kwargs) -> str:
        """搜索工具（模拟实现）"""
        # 这里应该连接到实际的搜索 API
        return f"搜索结果：{query} 的相关信息"
    
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
        return list(self.registered_tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """获取工具信息"""
        if tool_name in self.registered_tools:
            tool_func = self.registered_tools[tool_name]
            return {
                "name": tool_name,
                "function": tool_func.__name__,
                "doc": tool_func.__doc__ or "No documentation available"
            }
        else:
            return {"error": f"Tool '{tool_name}' not found"} 