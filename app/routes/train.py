# 自学习更新入口
from flask import Blueprint, request, jsonify, abort
from typing import Dict, Any, List
import asyncio

from core.memory.memory_updater import MemoryUpdater
from core.learning.learner import Learner
from utils.logging_config import get_logger

logger = get_logger(__name__)

bp = Blueprint('train', __name__, url_prefix='/api/v1/train')

@bp.route("/", methods=['POST'])
def train_endpoint():
    data = request.get_json()
    if not data or 'data' not in data:
        return jsonify({'error': 'Missing required field: data'}), 400
    """
    自学习更新入口
    支持多种学习模式：反馈学习、批量学习等
    """
    try:
        # 1. 记忆更新
        memory_updater = MemoryUpdater()
        
        # 2. 学习模块
        learner = Learner()
        
        training_type = data.get('training_type', 'general')
        if training_type == "feedback":
            # 反馈学习模式
            result = asyncio.run(learner.learn_from_feedback(
                data=data['data'],
                feedback=data.get('feedback', ''),
                user_id=data.get('user_id', 'default')
            ))
        elif training_type == "batch":
            # 批量学习模式
            result = asyncio.run(learner.batch_learn(
                data=data['data'],
                user_id=data.get('user_id', 'default')
            ))
        else:
            # 通用学习模式
            result = asyncio.run(learner.general_learn(
                data=request.data,
                user_id=request.user_id
            ))
        
        asyncio.run(memory_updater.update_memory(
            data=result,
            user_id=data.get('user_id', 'default')
        ))

        return jsonify({
            "status": "success",
            "message": "Training completed successfully",
            "updated_memories": result.get("updated_memories", 0),
            "learning_metrics": result.get("metrics", {})
        })
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@bp.route("/feedback", methods=['POST'])
def feedback_endpoint():
    """
    用户反馈处理
    用于改进模型和记忆质量
    """
    try:
        data = request.get_json()
        if not data or 'memory_id' not in data or 'feedback' not in data:
            return jsonify({'error': 'Missing required fields: memory_id or feedback'}), 400
        memory_updater = MemoryUpdater()
        
        # 处理用户反馈
        success = asyncio.run(memory_updater.update_memory_with_feedback(
            memory_id=data['memory_id'],
            feedback={"feedback": data['feedback'], "user_id": data.get('user_id', 'default')}
        ))
        
        if success:
            return {"status": "success", "message": "Feedback processed successfully"}
        else:
            return {"status": "error", "message": "Failed to process feedback"}
            
    except Exception as e:
        logger.error(f"Feedback processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Feedback processing failed: {str(e)}")

@bp.route("/status", methods=['GET'])
def training_status():
    """
    获取训练状态
    """
    return {
        "status": "ready",
        "last_training": "2024-01-01T00:00:00",
        "total_memories": 0,
        "learning_enabled": True
    }