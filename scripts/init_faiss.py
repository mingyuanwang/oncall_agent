"""
初始化FAISS索引目录
"""
import os
from config.vector_db_config import FAISSConfig

def init_faiss_index():
    """创建FAISS索引目录"""
    # 确保索引目录存在
    index_dir = os.path.dirname(FAISSConfig.INDEX_PATH)
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
        print(f"Created FAISS index directory: {index_dir}")
    else:
        print(f"FAISS index directory already exists: {index_dir}")

if __name__ == "__main__":
    init_faiss_index()