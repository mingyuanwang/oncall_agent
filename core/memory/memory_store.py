# 记忆检索模块
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime

from models.embedding_model import EmbeddingModel
from models.llm_inference import LLMInference
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MemoryStore:
    """
    记忆检索模块
    功能：从记忆库中获取与当前任务最相关的上下文
    """
    
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.llm_inference = LLMInference()
        self.memory_db_path = "data/memory.db"
        
    async def retrieve_memory(
        self, 
        query: str, 
        user_id: str = "default",
        max_chunks: int = 5
    ) -> List[Dict[str, Any]]:
        """
        记忆检索主函数
        
        Args:
            query: 用户查询
            user_id: 用户ID
            max_chunks: 最大返回记忆片段数
            
        Returns:
            context_chunks: 相关记忆片段列表
        """
        try:
            # 1. embedding 相似度召回
            embedding_results = await self._embedding_retrieval(query, user_id)
            
            # 2. tag-based routing
            tag_results = await self._tag_based_routing(query, user_id)
            
            # 3. 合并结果并去重
            all_candidates = self._merge_candidates(embedding_results, tag_results)
            
            # 4. chunk scoring（评分模型选择关键记忆）
            scored_chunks = await self._chunk_scoring(query, all_candidates)
            
            # 5. 选择 top-k 结果
            context_chunks = scored_chunks[:max_chunks]
            
            logger.info(f"Retrieved {len(context_chunks)} memory chunks for query: {query}")
            return context_chunks
            
        except Exception as e:
            logger.error(f"Memory retrieval failed: {str(e)}")
            return []
    
    async def _embedding_retrieval(
        self, 
        query: str, 
        user_id: str
    ) -> List[Dict[str, Any]]:
        """embedding 相似度召回"""
        try:
            # 获取查询的 embedding
            query_embedding = self.embedding_model.embed_text(query)
            
            # 从向量库中检索相似记忆
            # 这里应该连接到实际的向量数据库（FAISS/Chroma等）
            similar_memories = await self._search_vector_db(query_embedding, user_id)
            
            return similar_memories
            
        except Exception as e:
            logger.error(f"Embedding retrieval failed: {str(e)}")
            return []
    
    async def _tag_based_routing(
        self, 
        query: str, 
        user_id: str
    ) -> List[Dict[str, Any]]:
        """tag-based routing（按标签召回）"""
        try:
            # 分析查询，提取可能的标签
            query_tags = await self._extract_query_tags(query)
            
            # 根据标签检索相关记忆
            tagged_memories = await self._search_by_tags(query_tags, user_id)
            
            return tagged_memories
            
        except Exception as e:
            logger.error(f"Tag-based routing failed: {str(e)}")
            return []
    
    async def _chunk_scoring(
        self, 
        query: str, 
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """chunk scoring（评分模型选择关键记忆）"""
        try:
            scored_candidates = []
            
            for candidate in candidates:
                # 使用 LLM 对每个候选记忆进行评分
                score = await self._score_chunk_relevance(query, candidate)
                
                scored_candidate = {
                    **candidate,
                    "relevance_score": score
                }
                scored_candidates.append(scored_candidate)
            
            # 按评分排序
            scored_candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return scored_candidates
            
        except Exception as e:
            logger.error(f"Chunk scoring failed: {str(e)}")
            return candidates
    
    async def _score_chunk_relevance(
        self, 
        query: str, 
        chunk: Dict[str, Any]
    ) -> float:
        """使用 LLM 评分记忆片段的相关性"""
        try:
            prompt = f"""
            请评估以下记忆片段与用户查询的相关性，评分范围 0-1：
            
            用户查询：{query}
            记忆片段：{chunk.get('content', '')}
            记忆标签：{chunk.get('tags', [])}
            
            请只返回一个 0-1 之间的数字作为相关性评分。
            """
            
            response = await self.llm_inference.generate_response(prompt)
            
            # 解析评分
            try:
                score = float(response.strip())
                return max(0.0, min(1.0, score))  # 确保在 0-1 范围内
            except ValueError:
                return 0.5  # 默认评分
                
        except Exception as e:
            logger.error(f"Chunk scoring failed: {str(e)}")
            return 0.5
    
    async def _extract_query_tags(self, query: str) -> List[str]:
        """提取查询中的标签"""
        try:
            prompt = f"""
            请从以下查询中提取相关标签（最多5个）：
            查询：{query}
            
            请以JSON格式返回标签列表，例如：["标签1", "标签2"]
            """
            
            response = await self.llm_inference.generate_response(prompt)
            
            try:
                import json
                tags = json.loads(response)
                return tags if isinstance(tags, list) else []
            except:
                return []
                
        except Exception as e:
            logger.error(f"Tag extraction failed: {str(e)}")
            return []
    
    def _merge_candidates(
        self, 
        embedding_results: List[Dict[str, Any]], 
        tag_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """合并 embedding 和 tag 检索结果"""
        merged = []
        seen_ids = set()
        
        # 添加 embedding 结果
        for result in embedding_results:
            memory_id = result.get("id")
            if memory_id and memory_id not in seen_ids:
                merged.append({**result, "source": "embedding"})
                seen_ids.add(memory_id)
        
        # 添加 tag 结果
        for result in tag_results:
            memory_id = result.get("id")
            if memory_id and memory_id not in seen_ids:
                merged.append({**result, "source": "tag"})
                seen_ids.add(memory_id)
        
        return merged
    
    async def _search_vector_db(self, query_embedding: List[float], user_id: str) -> List[Dict[str, Any]]:
        """从向量数据库搜索（模拟实现）"""
        # 这里应该连接到实际的向量数据库
        # 目前返回模拟数据
        return [
            {
                "id": "mem_001",
                "content": "如何解决Python内存泄漏问题：使用gc模块进行垃圾回收",
                "tags": ["python", "memory", "debugging"],
                "embedding": query_embedding,
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def _search_by_tags(self, tags: List[str], user_id: str) -> List[Dict[str, Any]]:
        """根据标签搜索记忆（模拟实现）"""
        # 这里应该连接到实际的数据库
        # 目前返回模拟数据
        return [
            {
                "id": "mem_002", 
                "content": "Python性能优化技巧：使用列表推导式替代循环",
                "tags": ["python", "performance", "optimization"],
                "timestamp": datetime.now().isoformat()
            }
        ] 