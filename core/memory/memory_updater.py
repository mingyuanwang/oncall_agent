# 记忆更新模块
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import uuid

from models.embedding_model import EmbeddingModel
from models.llm_inference import LLMInference
from utils.logging_config import get_logger
from utils.helpers import save_json_file

logger = get_logger(__name__)

class MemoryUpdater:
    """
    记忆更新模块
    功能：将 agent 执行过程中的关键步骤、最终结果写入记忆系统
    """
    
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.llm_inference = LLMInference()
        self.memory_db_path = "data/memory.db"
        self.memory_file_path = "data/episodic_memory.json"
        
    async def update_memory(
        self, 
        query: str, 
        plan_steps: List[str], 
        execution_result: Dict[str, Any],
        user_id: str = "default"
    ) -> List[Dict[str, Any]]:
        """
        更新记忆
        
        Args:
            query: 用户查询
            plan_steps: 执行计划
            execution_result: 执行结果
            user_id: 用户ID
            
        Returns:
            memory_traces: 记忆轨迹列表
        """
        try:
            memory_traces = []
            
            # 1. 生成完整执行轨迹
            full_trace = self._create_full_trace(query, plan_steps, execution_result)
            
            # 2. 分段打分：评估哪些步骤值得写入长期记忆
            scored_segments = await self._score_memory_segments(full_trace)
            
            # 3. 选择高分片段进行记忆存储
            valuable_segments = [seg for seg in scored_segments if seg["score"] >= 0.7]
            
            # 4. 结构化处理并存储
            for segment in valuable_segments:
                memory_entry = await self._create_memory_entry(segment, user_id)
                await self._store_memory(memory_entry)
                memory_traces.append(memory_entry)
            
            logger.info(f"Updated memory with {len(memory_traces)} valuable segments")
            return memory_traces
            
        except Exception as e:
            logger.error(f"Memory update failed: {str(e)}")
            import traceback
            logger.error(f"Memory update traceback: {traceback.format_exc()}")
            return []
    
    def _create_full_trace(
        self, 
        query: str, 
        plan_steps: List[str], 
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建完整的执行轨迹"""
        return {
            "trace_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "plan_steps": plan_steps,
            "intermediate_results": execution_result.get("intermediate_results", []),
            "final_answer": execution_result.get("final_answer", ""),
            "success": execution_result.get("success", False),
            "total_steps": len(execution_result.get("intermediate_results", [])),
            "execution_time": execution_result.get("execution_time", 0)
        }
    
    async def _score_memory_segments(self, full_trace: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分段打分：评估记忆片段的价值"""
        try:
            segments = self._extract_segments(full_trace)
            scored_segments = []
            
            for segment in segments:
                score = await self._evaluate_segment_value(segment)
                scored_segment = {
                    **segment,
                    "score": score,
                    "timestamp": datetime.now().isoformat()
                }
                scored_segments.append(scored_segment)
            
            # 按评分排序
            scored_segments.sort(key=lambda x: x["score"], reverse=True)
            return scored_segments
            
        except Exception as e:
            logger.error(f"Segment scoring failed: {str(e)}")
            return []
    
    def _extract_segments(self, full_trace: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取记忆片段"""
        segments = []
        
        # 1. 查询片段
        segments.append({
            "type": "query",
            "content": full_trace["query"],
            "metadata": {
                "trace_id": full_trace["trace_id"],
                "segment_type": "user_query"
            }
        })
        
        # 2. 计划片段
        if full_trace["plan_steps"]:
            segments.append({
                "type": "plan",
                "content": "\n".join(full_trace["plan_steps"]),
                "metadata": {
                    "trace_id": full_trace["trace_id"],
                    "segment_type": "execution_plan",
                    "step_count": len(full_trace["plan_steps"])
                }
            })
        
        # 3. 中间结果片段
        for i, result in enumerate(full_trace["intermediate_results"]):
            if result.get("success") and result.get("result"):
                segments.append({
                    "type": "intermediate_result",
                    "content": result["result"],
                    "metadata": {
                        "trace_id": full_trace["trace_id"],
                        "segment_type": "step_result",
                        "step_number": i + 1,
                        "step": result.get("step", ""),
                        "thought": result.get("thought", "")
                    }
                })
        
        # 4. 最终答案片段
        if full_trace["final_answer"]:
            segments.append({
                "type": "final_answer",
                "content": full_trace["final_answer"],
                "metadata": {
                    "trace_id": full_trace["trace_id"],
                    "segment_type": "final_result",
                    "success": full_trace["success"]
                }
            })
        
        return segments
    
    async def _evaluate_segment_value(self, segment: Dict[str, Any]) -> float:
        """评估记忆片段的价值"""
        try:
            prompt = f"""
            请评估以下记忆片段的价值，评分范围 0-1：
            
            片段类型：{segment.get('type', '')}
            片段内容：{segment.get('content', '')}
            元数据：{segment.get('metadata', {})}
            
            评估标准：
            1. 信息的新颖性和独特性
            2. 解决问题的有效性
            3. 可重用性和通用性
            4. 知识密度和完整性
            
            请只返回一个 0-1 之间的数字作为价值评分。
            """
            
            response = await self.llm_inference.generate_response(prompt)
            
            try:
                score = float(response.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                return 0.5
                
        except Exception as e:
            logger.error(f"Segment evaluation failed: {str(e)}")
            return 0.5
    
    async def _create_memory_entry(
        self, 
        segment: Dict[str, Any], 
        user_id: str
    ) -> Dict[str, Any]:
        """创建记忆条目"""
        try:
            # 生成 embedding
            content = segment.get("content", "")
            embedding = self.embedding_model.embed_text(content)
            
            # 创建记忆条目
            memory_entry = {
                "id": str(uuid.uuid4()),
                "content": content,
                "embedding": embedding,
                "tags": [],
                "type": segment.get("type", ""),
                "metadata": segment.get("metadata", {}),
                "score": segment.get("score", 0.0),
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "storage_type": "episodic"  # 或 "semantic", "procedural"
            }
            
            return memory_entry
            
        except Exception as e:
            logger.error(f"Memory entry creation failed: {str(e)}")
            return {}
    
    async def _store_memory(self, memory_entry: Dict[str, Any]):
        """存储记忆条目"""
        try:
            # 1. 存储到向量数据库（模拟）
            await self._store_to_vector_db(memory_entry)
            
            # 2. 存储到知识图谱（模拟）
            await self._store_to_knowledge_graph(memory_entry)
            
            # 3. 存储到文本文件
            await self._store_to_text_file(memory_entry)
            
            logger.info(f"Stored memory entry: {memory_entry.get('id')}")
            
        except Exception as e:
            logger.error(f"Memory storage failed: {str(e)}")
    
    async def _store_to_vector_db(self, memory_entry: Dict[str, Any]):
        """存储到向量数据库（FAISS实现）"""
        try:
            # 使用FAISS向量数据库存储
            from .faiss_vector_store import FAISSVectorStore
            
            # 初始化FAISS索引
            faiss_store = FAISSVectorStore()
            
            # 提取需要存储的数据
            memory_id = memory_entry.get("id")
            embedding = memory_entry.get("embedding")
            
            # 添加到FAISS索引
            if memory_id and embedding:
                faiss_store.add_vectors([memory_id], [embedding])
                logger.info(f"Stored to FAISS vector DB: {memory_id}")
            else:
                logger.warning(f"Missing id or embedding for memory entry: {memory_id}")
                
        except Exception as e:
            logger.error(f"Failed to store to FAISS vector DB: {str(e)}")
            import traceback
            logger.error(f"FAISS vector store traceback: {traceback.format_exc()}")
    
    async def _store_to_knowledge_graph(self, memory_entry: Dict[str, Any]):
        """存储到知识图谱"""
        # 这里应该连接到实际的知识图谱数据库
        # 目前是模拟实现
        logger.info(f"Storing to knowledge graph: {memory_entry.get('id')}")
    
    async def _store_to_text_file(self, memory_entry: Dict[str, Any]):
        """存储到文本文件"""
        try:
            # 读取现有记忆文件
            try:
                with open(self.memory_file_path, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
            except FileNotFoundError:
                memory_data = {"memories": []}
            
            # 添加新记忆条目
            memory_data["memories"].append(memory_entry)
            
            # 保存到文件
            save_json_file(memory_data, self.memory_file_path)
            
        except Exception as e:
            logger.error(f"Text file storage failed: {str(e)}")
    
    async def update_memory_with_feedback(
        self, 
        memory_id: str, 
        feedback: Dict[str, Any]
    ) -> bool:
        """根据用户反馈更新记忆"""
        try:
            # 更新记忆条目的评分
            # 这里应该连接到实际的数据库进行更新
            logger.info(f"Updated memory {memory_id} with feedback")
            return True
            
        except Exception as e:
            logger.error(f"Memory feedback update failed: {str(e)}")
            return False