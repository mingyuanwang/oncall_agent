# 本地模型或调用 OpenAI/HuggingFace 等接口
from typing import List, Optional
import numpy as np
import hashlib
import json
import openai
from app.config import Config

class EmbeddingModel:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.model_name = "text-embedding-ada-002"  # OpenAI embedding model
        self.client = None
        self.cache = {}  # 简单的内存缓存
        
        if self.api_key:
            try:
                self.client = openai.AsyncOpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize OpenAI client for embeddings: {e}")
    
    def embed_text(self, text: str) -> List[float]:
        """文本嵌入"""
        try:
            # 检查缓存
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # 如果没有 OpenAI 客户端，使用简单的哈希嵌入
            if not self.client:
                return self._simple_hash_embedding(text)
            
            # 使用 OpenAI embedding
            return self._openai_embedding(text)
            
        except Exception as e:
            print(f"Embedding failed: {e}")
            return self._simple_hash_embedding(text)
    
    async def embed_text_async(self, text: str) -> List[float]:
        """异步文本嵌入"""
        try:
            # 检查缓存
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # 如果没有 OpenAI 客户端，使用简单的哈希嵌入
            if not self.client:
                return self._simple_hash_embedding(text)
            
            # 使用 OpenAI embedding
            return await self._openai_embedding_async(text)
            
        except Exception as e:
            print(f"Async embedding failed: {e}")
            return self._simple_hash_embedding(text)
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入"""
        try:
            embeddings = []
            for text in texts:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
            return embeddings
            
        except Exception as e:
            print(f"Batch embedding failed: {e}")
            return [self._simple_hash_embedding(text) for text in texts]
    
    async def embed_batch_async(self, texts: List[str]) -> List[List[float]]:
        """异步批量嵌入"""
        try:
            embeddings = []
            for text in texts:
                embedding = await self.embed_text_async(text)
                embeddings.append(embedding)
            return embeddings
            
        except Exception as e:
            print(f"Async batch embedding failed: {e}")
            return [self._simple_hash_embedding(text) for text in texts]
    
    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _simple_hash_embedding(self, text: str) -> List[float]:
        """简单的哈希嵌入（备用方案）"""
        # 使用文本的哈希值生成固定长度的向量
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # 将哈希字节转换为浮点数列表
        embedding = []
        for i in range(0, min(len(hash_bytes), 1536), 4):  # OpenAI embedding 维度是 1536
            if i + 3 < len(hash_bytes):
                value = int.from_bytes(hash_bytes[i:i+4], byteorder='big')
                embedding.append((value % 10000) / 10000.0)  # 归一化到 0-1
        
        # 如果长度不够，用零填充
        while len(embedding) < 1536:
            embedding.append(0.0)
        
        return embedding[:1536]
    
    def _openai_embedding(self, text: str) -> List[float]:
        """使用 OpenAI embedding（同步版本）"""
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            # 缓存结果
            cache_key = self._get_cache_key(text)
            self.cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            print(f"OpenAI embedding failed: {e}")
            return self._simple_hash_embedding(text)
    
    async def _openai_embedding_async(self, text: str) -> List[float]:
        """使用 OpenAI embedding（异步版本）"""
        try:
            response = await self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            # 缓存结果
            cache_key = self._get_cache_key(text)
            self.cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            print(f"OpenAI async embedding failed: {e}")
            return self._simple_hash_embedding(text)
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """计算余弦相似度"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            print(f"Cosine similarity calculation failed: {e}")
            return 0.0
    
    def find_most_similar(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]]
    ) -> List[tuple]:
        """找到最相似的嵌入"""
        try:
            similarities = []
            for i, candidate in enumerate(candidate_embeddings):
                similarity = self.cosine_similarity(query_embedding, candidate)
                similarities.append((i, similarity))
            
            # 按相似度排序
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities
            
        except Exception as e:
            print(f"Similarity search failed: {e}")
            return [] 