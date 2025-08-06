"""
测试FAISS向量数据库功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_faiss_import():
    """测试FAISS导入功能"""
    try:
        # 测试配置导入
        from config.vector_db_config import FAISSConfig
        print(f"FAISS配置导入成功: INDEX_PATH={FAISSConfig.INDEX_PATH}")
        
        # 测试FAISS向量存储导入
        from core.memory.faiss_vector_store import FAISSVectorStore
        print("FAISS向量存储导入成功")
        
        # 测试初始化
        faiss_store = FAISSVectorStore()
        print("FAISS向量存储初始化成功")
        
        return True
    except Exception as e:
        print(f"FAISS导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试FAISS向量数据库功能...")
    success = test_faiss_import()
    if success:
        print("所有测试通过!")
    else:
        print("测试失败!")
        sys.exit(1)