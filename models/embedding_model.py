# 本地模型或调用 OpenAI/HuggingFace 等接口
from typing import List

class EmbeddingModel:
    def __init__(self):
        pass
    
    def embed_text(self, text: str) -> List[float]:
        # 文本嵌入
        pass
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # 批量嵌入
        pass 