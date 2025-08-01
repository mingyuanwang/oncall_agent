# 查询入口（用户提问）
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio

from core.memory.memory_store import MemoryStore
from core.planning.planner import Planner
from core.react_executor.react_agent import ReactAgent
from core.memory.memory_updater import MemoryUpdater

router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    question: str
    context: str = ""
    user_id: str = "default"

class QueryResponse(BaseModel):
    answer: str
    plan_steps: List[str]
    intermediate_results: List[Dict[str, Any]]
    memory_traces: List[Dict[str, Any]]

@router.post("/", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    用户查询处理主入口
    完整流程：记忆检索 -> 规划 -> 执行 -> 记忆更新
    """
    try:
        # 1. 记忆检索
        memory_store = MemoryStore()
        context_chunks = await memory_store.retrieve_memory(
            query=request.question,
            user_id=request.user_id
        )
        
        # 2. 规划模块
        planner = Planner()
        plan_steps = await planner.generate_plan(
            query=request.question,
            context_chunks=context_chunks
        )
        
        # 3. Agent 执行
        react_agent = ReactAgent()
        execution_result = await react_agent.execute_plan(
            query=request.question,
            plan_steps=plan_steps,
            context_chunks=context_chunks
        )
        
        # 4. 记忆更新
        memory_updater = MemoryUpdater()
        memory_traces = await memory_updater.update_memory(
            query=request.question,
            plan_steps=plan_steps,
            execution_result=execution_result,
            user_id=request.user_id
        )
        
        return QueryResponse(
            answer=execution_result["final_answer"],
            plan_steps=plan_steps,
            intermediate_results=execution_result["intermediate_results"],
            memory_traces=memory_traces
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}") 