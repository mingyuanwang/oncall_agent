"""
FAISS向量数据库实现
"""
import faiss
import numpy as np
import json
import os
from typing import List, Dict, Any
import logging
from config.vector_db_config import FAISSConfig

logger = logging.getLogger(__name__)

class FAISSVectorStore:
    def __init__(self, index_path: str = None, dimension: int = None):
        """
        初始化FAISS向量数据库
        :param index_path: 索引文件路径
        :param dimension: 向量维度
        """
        self.index_path = index_path or FAISSConfig.INDEX_PATH
        self.dimension = dimension or FAISSConfig.DIMENSION
        self.index = None
        self.id_map = {}  # ID映射表
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """加载或创建索引"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.index_path + ".ids"):
                # 加载现有索引
                self.index = faiss.read_index(self.index_path)
                with open(self.index_path + ".ids", "r") as f:
                    self.id_map = json.load(f)
                logger.info(f"Loaded FAISS index from {self.index_path}")
            else:
                # 创建新索引
                self.index = faiss.IndexFlatL2(self.dimension)
                self.id_map = {}
                logger.info("Created new FAISS index")
        except Exception as e:
            logger.error(f"Failed to load or create FAISS index: {e}")
            # 创建新索引
            self.index = faiss.IndexFlatL2(self.dimension)
            self.id_map = {}
    
    def add_vectors(self, ids: List[str], vectors: List[List[float]]):
        """添加向量到索引"""
        try:
            # 转换向量格式
            vectors_np = np.array(vectors).astype('float32')
            
            # 添加到索引
            start_id = self.index.ntotal
            self.index.add(vectors_np)
            
            # 更新ID映射
            for i, id in enumerate(ids):
                self.id_map[str(start_id + i)] = id
            
            # 保存索引
            self._save_index()
            logger.info(f"Added {len(ids)} vectors to FAISS index")
        except Exception as e:
            logger.error(f"Failed to add vectors to FAISS index: {e}")
    
    def search(self, query_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似向量"""
        try:
            # 转换查询向量格式
            query_np = np.array([query_vector]).astype('float32')
            
            # 执行搜索
            distances, indices = self.index.search(query_np, k)
            
            # 构建结果
            results = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx != -1:  # FAISS返回-1表示没有找到更多结果
                    original_id = self.id_map.get(str(idx), str(idx))
                    results.append({
                        "id": original_id,
                        "distance": float(distances[0][i])
                    })
            
            return results
        except Exception as e:
            logger.error(f"Failed to search FAISS index: {e}")
            return []
    
    def _save_index(self):
        """保存索引到磁盘"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # 保存索引
            faiss.write_index(self.index, self.index_path)
            
            # 保存ID映射
            with open(self.index_path + ".ids", "w") as f:
                json.dump(self.id_map, f)
            
            logger.info(f"Saved FAISS index to {self.index_path}")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")