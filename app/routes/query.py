# 查询入口（用户提问）
from flask import Blueprint, request, jsonify, Response, stream_with_context
from typing import Dict, Any, List
import asyncio

from core.memory.memory_store import MemoryStore
from core.planning.planner import Planner
from core.react_executor.react_agent import ReactAgent
from core.memory.memory_updater import MemoryUpdater
import logging

bp = Blueprint('oncall_query_api', __name__, url_prefix='/api/v1/query')

@bp.route("/", methods=['POST'], strict_slashes=False)
@bp.route("/stream", methods=['POST'], strict_slashes=False)
def query_endpoint():
    """
    用户查询处理主入口
    完整流程：记忆检索 -> 规划 -> 执行 -> 记忆更新
    """
    logger = logging.getLogger(__name__)
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
        
        # 检查是否是流式请求
        if request.path.endswith('/stream'):
            # 流式响应
            def generate():
                # 模拟流式输出
                answer = execution_result["final_answer"]
                for i in range(0, len(answer), 10):
                    yield answer[i:i+10]
                    # 添加一个小延迟来模拟流式效果
                    import time
                    time.sleep(0.1)
            return Response(stream_with_context(generate()), content_type='text/plain')
        else:
            # 标准JSON响应
            return jsonify({
                'answer': execution_result["final_answer"],
                'plan_steps': plan_steps,
                'intermediate_results': execution_result["intermediate_results"],
                'memory_traces': memory_traces
            })
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500