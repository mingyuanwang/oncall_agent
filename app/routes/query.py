# 查询入口（用户提问）
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    question: str
    context: str = ""

@router.post("/")
async def query_endpoint(request: QueryRequest):
    # 处理用户查询
    return {"response": "Query processed"} 