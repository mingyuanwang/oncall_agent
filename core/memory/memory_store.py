# 记忆检索模块
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime

from models.embedding_model import EmbeddingModel
from models.llm_inference import LLMInference
from utils.logging_config import get_logger

logger = get_logger(__name__)

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
            
            # 2. chunk scoring（评分模型选择关键记忆）
            scored_chunks = await self._chunk_scoring(query, embedding_results)
            
            # 3. 选择 top-k 结果
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
    
    async def _search_vector_db(self, query_embedding: List[float], user_id: str) -> List[Dict[str, Any]]:
        """从向量数据库搜索（FAISS实现）"""
        try:
            # 使用FAISS向量数据库搜索
            from .faiss_vector_store import FAISSVectorStore
            
            # 初始化FAISS索引
            faiss_store = FAISSVectorStore()
            
            # 导入配置
            try:
                from config.vector_db_config import FAISSConfig
                search_top_k = FAISSConfig.SEARCH_TOP_K
            except ImportError:
                # 如果配置导入失败，使用默认值
                search_top_k = 5
            
            # 执行搜索
            search_results = faiss_store.search(query_embedding, k=search_top_k)
            
            # 这里需要根据实际存储结构返回结果
            # 目前返回模拟数据结构
            results = []
            for result in search_results:
                results.append({
                    "id": result["id"],
                    "content": "从FAISS检索到的内容",  # 需要从实际存储中获取
                    "embedding": query_embedding,
                    "timestamp": datetime.now().isoformat()
                })
            
            return results
            
        except Exception as e:
            logger.error(f"FAISS vector search failed: {str(e)}")
            import traceback
            logger.error(f"FAISS vector search traceback: {traceback.format_exc()}")
            # 出错时返回空结果
            return []