# 通用数据结构定义（pydantic）
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    question: str
    context: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[str]

class MemoryEntry(BaseModel):
    id: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]

class TrainingData(BaseModel):
    input: str
    output: str
    feedback: Optional[str] = None 