# 自学习更新入口
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio

from core.memory.memory_updater import MemoryUpdater
from core.learning.learner import Learner
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/train", tags=["train"])

class TrainingRequest(BaseModel):
    data: str
    feedback: str = ""
    user_id: str = "default"
    training_type: str = "general"  # general, feedback, batch

class TrainingResponse(BaseModel):
    status: str
    message: str
    updated_memories: int
    learning_metrics: Dict[str, Any]

@router.post("/", response_model=TrainingResponse)
async def train_endpoint(request: TrainingRequest):
    """
    自学习更新入口
    支持多种学习模式：反馈学习、批量学习等
    """
    try:
        # 1. 记忆更新
        memory_updater = MemoryUpdater()
        
        # 2. 学习模块
        learner = Learner()
        
        if request.training_type == "feedback":
            # 反馈学习模式
            result = await learner.learn_from_feedback(
                data=request.data,
                feedback=request.feedback,
                user_id=request.user_id
            )
        elif request.training_type == "batch":
            # 批量学习模式
            result = await learner.batch_learn(
                data=request.data,
                user_id=request.user_id
            )
        else:
            # 通用学习模式
            result = await learner.general_learn(
                data=request.data,
                user_id=request.user_id
            )
        
        return TrainingResponse(
            status="success",
            message="Training completed successfully",
            updated_memories=result.get("updated_memories", 0),
            learning_metrics=result.get("metrics", {})
        )
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.post("/feedback")
async def feedback_endpoint(request: TrainingRequest):
    """
    用户反馈处理
    用于改进模型和记忆质量
    """
    try:
        memory_updater = MemoryUpdater()
        
        # 处理用户反馈
        success = await memory_updater.update_memory_with_feedback(
            memory_id=request.data,  # 这里假设 data 字段包含 memory_id
            feedback={"feedback": request.feedback, "user_id": request.user_id}
        )
        
        if success:
            return {"status": "success", "message": "Feedback processed successfully"}
        else:
            return {"status": "error", "message": "Failed to process feedback"}
            
    except Exception as e:
        logger.error(f"Feedback processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Feedback processing failed: {str(e)}")

@router.get("/status")
async def training_status():
    """
    获取训练状态
    """
    return {
        "status": "ready",
        "last_training": "2024-01-01T00:00:00",
        "total_memories": 0,
        "learning_enabled": True
    } 