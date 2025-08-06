# ReAct 执行器模块
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime

from models.llm_inference import LLMInference
from models.tool_wrappers import ToolWrapper
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ReactAgent:
    """
    ReAct 执行器
    功能：模拟"思考+行动"循环的执行体
    特点：类似 ReAct/Toolformer，每个步骤执行可产生 intermediate results
    """
    
    def __init__(self):
        self.llm_inference = LLMInference()
        self.tool_wrapper = ToolWrapper()
        self.max_iterations = 10  # 最大迭代次数
        
    async def execute_plan(
        self, 
        query: str, 
        plan_steps: List[str], 
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        执行计划
        
        Args:
            query: 用户查询
            plan_steps: 执行步骤
            context_chunks: 背景知识
            
        Returns:
            执行结果，包含最终答案和中间结果
        """
        try:
            intermediate_results = []
            current_context = self._format_context(context_chunks)
            
            # 执行每个步骤
            for i, step in enumerate(plan_steps):
                logger.info(f"Executing step {i+1}: {step}")
                
                # 执行单个步骤
                step_result = await self._execute_step(
                    step=step,
                    query=query,
                    current_context=current_context,
                    step_number=i+1
                )
                
                intermediate_results.append(step_result)
                
                # 更新上下文
                if step_result.get("success"):
                    current_context += f"\n步骤{i+1}结果：{step_result.get('result', '')}"
                
                # 检查是否需要停止
                if step_result.get("should_stop", False):
                    break
            
            # 生成最终答案
            final_answer = await self._generate_final_answer(
                query=query,
                intermediate_results=intermediate_results,
                context_chunks=context_chunks
            )
            
            return {
                "final_answer": final_answer,
                "intermediate_results": intermediate_results,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Plan execution failed: {str(e)}")
            return {
                "final_answer": f"执行失败：{str(e)}",
                "intermediate_results": [],
                "success": False
            }
    
    async def _execute_step(
        self, 
        step: str, 
        query: str, 
        current_context: str,
        step_number: int
    ) -> Dict[str, Any]:
        """执行单个步骤"""
        try:
            # 1. 思考阶段：分析当前步骤
            thought = await self._think_about_step(step, query, current_context)
            
            # 2. 行动阶段：执行具体操作
            action_result = await self._execute_action(step, thought)
            
            # 3. 观察阶段：分析执行结果
            observation = await self._observe_result(action_result, step)
            
            # 4. 判断是否需要继续
            should_continue = await self._should_continue(step_number, observation)
            
            return {
                "step": step,
                "step_number": step_number,
                "thought": thought,
                "action": action_result,
                "observation": observation,
                "success": action_result.get("success", False),
                "result": action_result.get("result", ""),
                "should_stop": not should_continue,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Step execution failed: {str(e)}")
            return {
                "step": step,
                "step_number": step_number,
                "thought": f"步骤执行失败：{str(e)}",
                "action": {"success": False, "error": str(e)},
                "observation": "执行过程中出现错误",
                "success": False,
                "result": "",
                "should_stop": True,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _think_about_step(
        self, 
        step: str, 
        query: str, 
        current_context: str
    ) -> str:
        """思考当前步骤"""
        prompt = f"""
        请分析当前需要执行的步骤：
        
        用户查询：{query}
        当前上下文：{current_context}
        当前步骤：{step}
        
        请思考：
        1. 这个步骤的目的是什么？
        2. 需要什么工具或方法来完成？
        3. 预期的结果是什么？
        4. 可能遇到的困难是什么？
        
        请简要描述你的思考过程。
        """
        
        try:
            thought = await self.llm_inference.generate_response(prompt)
            return thought.strip()
        except Exception as e:
            return f"思考过程：分析步骤 {step}，准备执行"
    
    async def _execute_action(self, step: str, thought: str) -> Dict[str, Any]:
        """执行具体行动"""
        try:
            # 分析步骤中是否需要调用工具
            tool_call = await self._analyze_tool_requirement(step, thought)
            
            if tool_call:
                # 调用工具
                result = await self.tool_wrapper.call_tool(
                    tool_name=tool_call["tool_name"],
                    parameters=tool_call["parameters"]
                )
                return {
                    "success": True,
                    "result": result.get("result", ""),
                    "tool_used": tool_call["tool_name"],
                    "action_type": "tool_call"
                }
            else:
                # 纯文本处理
                result = await self._process_text_step(step, thought)
                return {
                    "success": True,
                    "result": result,
                    "action_type": "text_processing"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action_type": "error"
            }
    
    async def _analyze_tool_requirement(self, step: str, thought: str) -> Optional[Dict[str, Any]]:
        """分析步骤是否需要调用工具"""
        prompt = f"""
        分析以下步骤是否需要调用特定工具：
        
        步骤：{step}
        思考：{thought}
        
        如果步骤涉及以下操作，请返回工具调用信息：
        - 搜索信息：使用 search_tool
        - 计算：使用 calculator_tool
        - 文件操作：使用 file_tool
        - 网络请求：使用 api_tool
        
        请以JSON格式返回，如果不需要工具则返回null：
        {{
            "tool_name": "工具名称",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}
        """
        
        try:
            response = await self.llm_inference.generate_response(prompt)
            if response.strip().lower() == "null":
                return None
            
            tool_call = json.loads(response)
            return tool_call if isinstance(tool_call, dict) else None
            
        except Exception as e:
            logger.error(f"Tool analysis failed: {str(e)}")
            return None
    
    async def _process_text_step(self, step: str, thought: str) -> str:
        """处理纯文本步骤"""
        prompt = f"""
        请执行以下步骤：
        
        步骤：{step}
        思考：{thought}
        
        请提供具体的执行结果或说明。
        """
        
        try:
            result = await self.llm_inference.generate_response(prompt)
            return result.strip()
        except Exception as e:
            return f"文本处理失败：{str(e)}"
    
    async def _observe_result(self, action_result: Dict[str, Any], step: str) -> str:
        """观察执行结果"""
        prompt = f"""
        观察以下执行结果：
        
        步骤：{step}
        执行结果：{action_result}
        
        请分析：
        1. 执行是否成功？
        2. 结果是否符合预期？
        3. 是否需要调整策略？
        4. 下一步应该做什么？
        
        请简要描述你的观察。
        """
        
        try:
            observation = await self.llm_inference.generate_response(prompt)
            return observation.strip()
        except Exception as e:
            return f"观察结果：执行{'成功' if action_result.get('success') else '失败'}"
    
    async def _should_continue(self, step_number: int, observation: str) -> bool:
        """判断是否应该继续执行"""
        # 简单的继续条件：未达到最大步骤数且没有明确的停止信号
        if step_number >= self.max_iterations:
            return False
        
        # 检查观察结果中是否有停止信号
        stop_keywords = ["完成", "结束", "停止", "finished", "complete", "stop"]
        if any(keyword in observation.lower() for keyword in stop_keywords):
            return False
        
        return True
    
    async def _generate_final_answer(
        self, 
        query: str, 
        intermediate_results: List[Dict[str, Any]],
        context_chunks: List[Dict[str, Any]]
    ) -> str:
        """生成最终答案"""
        prompt = f"""
        基于执行过程生成最终答案：
        
        用户查询：{query}
        背景知识：{self._format_context(context_chunks)}
        执行过程：{self._format_execution_process(intermediate_results)}
        
        请总结所有步骤的结果，给出完整的答案。
        """
        
        try:
            final_answer = await self.llm_inference.generate_response(prompt)
            return final_answer.strip()
        except Exception as e:
            return f"基于执行过程生成答案时出错：{str(e)}"
    
    def _format_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """格式化背景知识"""
        if not context_chunks:
            return "无相关背景知识"
        
        context = "背景知识：\n"
        for i, chunk in enumerate(context_chunks, 1):
            content = chunk.get("content", "")
            context += f"{i}. {content}\n"
        
        return context
    
    def _format_execution_process(self, intermediate_results: List[Dict[str, Any]]) -> str:
        """格式化执行过程"""
        if not intermediate_results:
            return "无执行过程"
        
        process = "执行过程：\n"
        for result in intermediate_results:
            step = result.get("step", "")
            result_text = result.get("result", "")
            success = result.get("success", False)
            
            process += f"步骤：{step}\n"
            process += f"结果：{'成功' if success else '失败'}\n"
            if result_text:
                process += f"详情：{result_text}\n"
            process += "\n"
        
        return process