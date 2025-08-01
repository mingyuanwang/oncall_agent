# 自学习模块主逻辑
from typing import Dict, Any, List
import asyncio
import json
from datetime import datetime

from models.llm_inference import LLMInference
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Learner:
    """
    自学习模块主逻辑
    功能：处理各种学习模式，包括反馈学习、批量学习等
    """
    
    def __init__(self):
        self.llm_inference = LLMInference()
        
    async def general_learn(
        self, 
        data: str, 
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        通用学习模式
        
        Args:
            data: 学习数据
            user_id: 用户ID
            
        Returns:
            学习结果
        """
        try:
            # 分析学习数据
            analysis = await self._analyze_learning_data(data)
            
            # 提取知识
            knowledge = await self._extract_knowledge(data, analysis)
            
            # 更新学习模型
            model_update = await self._update_learning_model(knowledge, user_id)
            
            return {
                "status": "success",
                "updated_memories": 1,
                "metrics": {
                    "knowledge_extracted": len(knowledge),
                    "model_updated": model_update.get("success", False),
                    "learning_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"General learning failed: {str(e)}")
            return {
                "status": "error",
                "updated_memories": 0,
                "metrics": {"error": str(e)}
            }
    
    async def learn_from_feedback(
        self, 
        data: str, 
        feedback: str, 
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        从反馈中学习
        
        Args:
            data: 原始数据
            feedback: 用户反馈
            user_id: 用户ID
            
        Returns:
            学习结果
        """
        try:
            # 分析反馈
            feedback_analysis = await self._analyze_feedback(data, feedback)
            
            # 根据反馈调整知识
            adjusted_knowledge = await self._adjust_knowledge_with_feedback(
                data, feedback, feedback_analysis
            )
            
            # 更新模型
            model_update = await self._update_model_with_feedback(
                adjusted_knowledge, user_id
            )
            
            return {
                "status": "success",
                "updated_memories": 1,
                "metrics": {
                    "feedback_processed": True,
                    "knowledge_adjusted": len(adjusted_knowledge),
                    "model_updated": model_update.get("success", False)
                }
            }
            
        except Exception as e:
            logger.error(f"Feedback learning failed: {str(e)}")
            return {
                "status": "error",
                "updated_memories": 0,
                "metrics": {"error": str(e)}
            }
    
    async def batch_learn(
        self, 
        data: str, 
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        批量学习模式
        
        Args:
            data: 批量学习数据（JSON格式）
            user_id: 用户ID
            
        Returns:
            学习结果
        """
        try:
            # 解析批量数据
            batch_data = json.loads(data) if isinstance(data, str) else data
            
            total_processed = 0
            successful_updates = 0
            
            for item in batch_data:
                try:
                    # 处理单个学习项
                    result = await self.general_learn(str(item), user_id)
                    if result.get("status") == "success":
                        successful_updates += 1
                    total_processed += 1
                except Exception as e:
                    logger.error(f"Batch item processing failed: {str(e)}")
            
            return {
                "status": "success",
                "updated_memories": successful_updates,
                "metrics": {
                    "total_processed": total_processed,
                    "successful_updates": successful_updates,
                    "success_rate": successful_updates / total_processed if total_processed > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Batch learning failed: {str(e)}")
            return {
                "status": "error",
                "updated_memories": 0,
                "metrics": {"error": str(e)}
            }
    
    async def _analyze_learning_data(self, data: str) -> Dict[str, Any]:
        """分析学习数据"""
        try:
            prompt = f"""
            请分析以下学习数据：
            
            数据：{data}
            
            请分析：
            1. 数据类型和结构
            2. 主要知识点
            3. 学习价值
            4. 适用场景
            
            请以JSON格式返回分析结果。
            """
            
            response = await self.llm_inference.generate_response(prompt)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"analysis": "无法解析分析结果", "raw_response": response}
                
        except Exception as e:
            logger.error(f"Learning data analysis failed: {str(e)}")
            return {"error": str(e)}
    
    async def _extract_knowledge(
        self, 
        data: str, 
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """提取知识"""
        try:
            prompt = f"""
            请从以下数据中提取知识：
            
            数据：{data}
            分析：{analysis}
            
            请提取：
            1. 核心知识点
            2. 规则和模式
            3. 最佳实践
            4. 注意事项
            
            请以JSON格式返回知识列表。
            """
            
            response = await self.llm_inference.generate_response(prompt)
            
            try:
                knowledge = json.loads(response)
                return knowledge if isinstance(knowledge, list) else [knowledge]
            except json.JSONDecodeError:
                return [{"content": data, "type": "raw_data"}]
                
        except Exception as e:
            logger.error(f"Knowledge extraction failed: {str(e)}")
            return [{"content": data, "type": "raw_data", "error": str(e)}]
    
    async def _update_learning_model(
        self, 
        knowledge: List[Dict[str, Any]], 
        user_id: str
    ) -> Dict[str, Any]:
        """更新学习模型"""
        try:
            # 这里应该实现实际的模型更新逻辑
            # 目前是模拟实现
            logger.info(f"Updating learning model with {len(knowledge)} knowledge items")
            
            return {
                "success": True,
                "updated_items": len(knowledge),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Model update failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_feedback(
        self, 
        data: str, 
        feedback: str
    ) -> Dict[str, Any]:
        """分析用户反馈"""
        try:
            prompt = f"""
            请分析用户反馈：
            
            原始数据：{data}
            用户反馈：{feedback}
            
            请分析：
            1. 反馈类型（正面/负面/中性）
            2. 具体问题或建议
            3. 需要改进的方面
            4. 学习价值
            
            请以JSON格式返回分析结果。
            """
            
            response = await self.llm_inference.generate_response(prompt)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"feedback_type": "unknown", "analysis": response}
                
        except Exception as e:
            logger.error(f"Feedback analysis failed: {str(e)}")
            return {"error": str(e)}
    
    async def _adjust_knowledge_with_feedback(
        self, 
        data: str, 
        feedback: str, 
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """根据反馈调整知识"""
        try:
            prompt = f"""
            请根据用户反馈调整知识：
            
            原始数据：{data}
            用户反馈：{feedback}
            反馈分析：{analysis}
            
            请调整：
            1. 修正错误信息
            2. 补充缺失内容
            3. 优化表达方式
            4. 增加相关示例
            
            请以JSON格式返回调整后的知识。
            """
            
            response = await self.llm_inference.generate_response(prompt)
            
            try:
                adjusted = json.loads(response)
                return adjusted if isinstance(adjusted, list) else [adjusted]
            except json.JSONDecodeError:
                return [{"content": data, "feedback": feedback, "adjusted": True}]
                
        except Exception as e:
            logger.error(f"Knowledge adjustment failed: {str(e)}")
            return [{"content": data, "feedback": feedback, "error": str(e)}]
    
    async def _update_model_with_feedback(
        self, 
        adjusted_knowledge: List[Dict[str, Any]], 
        user_id: str
    ) -> Dict[str, Any]:
        """根据反馈更新模型"""
        try:
            # 这里应该实现基于反馈的模型更新逻辑
            logger.info(f"Updating model with feedback-based knowledge: {len(adjusted_knowledge)} items")
            
            return {
                "success": True,
                "feedback_incorporated": True,
                "updated_items": len(adjusted_knowledge)
            }
            
        except Exception as e:
            logger.error(f"Feedback-based model update failed: {str(e)}")
            return {"success": False, "error": str(e)} 