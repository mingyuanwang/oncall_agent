"""
简单测试FAISS向量数据库功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # 测试FAISS导入
    import faiss
    print("FAISS导入成功")
    
    # 测试配置导入
    try:
        from config.vector_db_config import FAISSConfig
        print(f"配置导入成功: INDEX_PATH={FAISSConfig.INDEX_PATH}")
    except Exception as e:
        print(f"配置导入失败: {e}")
    
    # 测试FAISS向量存储导入
    try:
        from core.memory.faiss_vector_store import FAISSVectorStore
        print("FAISS向量存储导入成功")
    except Exception as e:
        print(f"FAISS向量存储导入失败: {e}")
        import traceback
        traceback.print_exc()
    
except Exception as e:
    print(f"FAISS导入失败: {e}")
    sys.exit(1)

print("测试完成")