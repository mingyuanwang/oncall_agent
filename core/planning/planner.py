# 规划模块
from typing import List, Dict, Any
import json
import asyncio

from models.llm_inference import LLMInference
from utils.logging_config import get_logger

logger = get_logger(__name__)

class Planner:
    """
    规划模块
    功能：基于当前 query 和检索到的 context，生成可执行的 plan
    """
    
    def __init__(self):
        self.llm_inference = LLMInference()
        
    async def generate_plan(
        self, 
        query: str, 
        context_chunks: List[Dict[str, Any]]
    ) -> List[str]:
        """
        生成执行计划
        
        Args:
            query: 用户查询
            context_chunks: 检索到的记忆片段
            
        Returns:
            plan_steps: 执行步骤列表
        """
        try:
            # 构造 prompt
            prompt = self._construct_planning_prompt(query, context_chunks)
            
            # 调用 LLM 生成计划
            plan_response = await self.llm_inference.generate_response(prompt)
            
            # 解析计划步骤
            plan_steps = self._parse_plan_response(plan_response)
            
            logger.info(f"Generated plan with {len(plan_steps)} steps for query: {query}")
            return plan_steps
            
        except Exception as e:
            logger.error(f"Plan generation failed: {str(e)}")
            return [f"处理查询：{query}"]
    
    def _construct_planning_prompt(
        self, 
        query: str, 
        context_chunks: List[Dict[str, Any]]
    ) -> str:
        """构造规划 prompt"""
        
        # 格式化记忆片段
        memory_context = ""
        if context_chunks:
            memory_context = "你当前拥有如下背景知识：\n"
            for i, chunk in enumerate(context_chunks, 1):
                content = chunk.get("content", "")
                score = chunk.get("relevance_score", 0.0)
                
                memory_context += f"{i}. {content}\n"
                memory_context += f"   相关性评分：{score:.2f}\n\n"
        
        prompt = f"""
你是一个智能助手，请根据用户的问题和背景知识，制定详细的解决步骤。

{memory_context}

用户问题：{query}

请输出解决步骤列表，要求：
1. 步骤要具体可执行
2. 考虑背景知识中的相关信息
3. 如果背景知识中有相关解决方案，优先参考
4. 每个步骤要清晰明确

请以JSON格式返回，格式如下：
{{
    "steps": [
        "步骤1描述",
        "步骤2描述",
        "步骤3描述"
    ],
    "reasoning": "制定此计划的理由"
}}

如果无法解析为JSON，请直接返回步骤列表，每行一个步骤。
"""
        return prompt
    
    def _parse_plan_response(self, response: str) -> List[str]:
        """解析 LLM 返回的计划响应"""
        try:
            # 尝试解析 JSON 格式
            plan_data = json.loads(response)
            if isinstance(plan_data, dict) and "steps" in plan_data:
                return plan_data["steps"]
        except json.JSONDecodeError:
            pass
        
        # 如果不是 JSON 格式，按行分割
        lines = response.strip().split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('{') and not line.startswith('}'):
                # 移除可能的序号
                if line[0].isdigit() and line[1] in ['.', '、', ' ']:
                    line = line[2:].strip()
                steps.append(line)
        
        return steps if steps else ["处理用户查询"]
    
    async def generate_detailed_plan(
        self, 
        query: str, 
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        生成详细计划（包含推理过程）
        
        Returns:
            包含步骤和推理的详细计划
        """
        try:
            prompt = self._construct_detailed_planning_prompt(query, context_chunks)
            response = await self.llm_inference.generate_response(prompt)
            
            # 尝试解析 JSON 响应
            try:
                plan_data = json.loads(response)
                return plan_data
            except json.JSONDecodeError:
                # 如果不是 JSON，构造基本结构
                return {
                    "steps": self._parse_plan_response(response),
                    "reasoning": "基于用户查询和背景知识制定的计划",
                    "confidence": 0.8
                }
                
        except Exception as e:
            logger.error(f"Detailed plan generation failed: {str(e)}")
            return {
                "steps": [f"处理查询：{query}"],
                "reasoning": "由于生成失败，使用基本处理步骤",
                "confidence": 0.5
            }
    
    def _construct_detailed_planning_prompt(
        self, 
        query: str, 
        context_chunks: List[Dict[str, Any]]
    ) -> str:
        """构造详细规划 prompt"""
        
        memory_context = ""
        if context_chunks:
            memory_context = "背景知识：\n"
            for i, chunk in enumerate(context_chunks, 1):
                content = chunk.get("content", "")
                score = chunk.get("relevance_score", 0.0)
                
                memory_context += f"{i}. {content}\n"
                memory_context += f"   相关性：{score:.2f}\n\n"
        
        prompt = f"""
你是一个智能助手，请分析用户问题并制定详细的解决计划。

{memory_context}

用户问题：{query}

请分析：
1. 问题类型和复杂度
2. 背景知识中是否有相关解决方案
3. 需要哪些具体步骤
4. 每个步骤的预期结果

请以JSON格式返回详细计划：
{{
    "problem_analysis": "问题分析",
    "relevant_knowledge": "相关背景知识",
    "steps": [
        {{
            "step": "步骤描述",
            "purpose": "步骤目的",
            "expected_result": "预期结果"
        }}
    ],
    "reasoning": "制定此计划的推理过程",
    "confidence": 0.8,
    "estimated_time": "预计耗时"
}}
"""
        return prompt