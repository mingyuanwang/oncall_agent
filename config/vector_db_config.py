"""
向量数据库配置
"""
import os

# FAISS配置
class FAISSConfig:
    # 索引文件路径
    INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
    
    # 向量维度
    DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    
    # 搜索返回的最相似向量数
    SEARCH_TOP_K = int(os.getenv("FAISS_SEARCH_TOP_K", "5"))