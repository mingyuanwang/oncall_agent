# 查询入口（用户提问）
from flask import Blueprint, request, jsonify
from typing import Dict, Any, List
import asyncio

from core.memory.memory_store import MemoryStore
from core.planning.planner import Planner
from core.react_executor.react_agent import ReactAgent
from core.memory.memory_updater import MemoryUpdater

bp = Blueprint('oncall_query_api', __name__, url_prefix='/api/v1/query')

@bp.route("/", methods=['POST'], strict_slashes=False)
def query_endpoint():
    """
    用户查询处理主入口
    完整流程：记忆检索 -> 规划 -> 执行 -> 记忆更新
    """
    try:
        data = request.get_json()
        logger.info(f"Received query request: {data.get('question')}")
        if not data or 'question' not in data:
            return jsonify({'error': 'Missing required field: question'}), 400

        # 1. 记忆检索
        memory_store = MemoryStore()
        context_chunks = asyncio.run(memory_store.retrieve_memory(
            query=data['question'],
            user_id=data.get('user_id', 'default')
        ))
        logger.info(f"Retrieved {len(context_chunks)} context chunks for query")
        
        # 2. 规划模块
        planner = Planner()
        plan_steps = asyncio.run(planner.generate_plan(
            query=data['question'],
            context_chunks=context_chunks
        ))

        # 3. Agent 执行
        react_agent = ReactAgent()
        execution_result = asyncio.run(react_agent.execute_plan(
            query=data['question'],
            plan_steps=plan_steps,
            context_chunks=context_chunks
        ))
        logger.info(f"Query execution completed successfully")
        
        # 4. 记忆更新
        memory_updater = MemoryUpdater()
        memory_traces = asyncio.run(memory_updater.update_memory(
            query=data['question'],
            plan_steps=plan_steps,
            answer=execution_result['answer'],
            intermediate_results=execution_result['intermediate_steps'],
            user_id=data.get('user_id', 'default')
        ))
        
        return jsonify({
            'answer': execution_result["final_answer"],
            'plan_steps': plan_steps,
            'intermediate_results': execution_result["intermediate_results"],
            'memory_traces': memory_traces
        })
        
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        return jsonify({'error': str(e)}), 500