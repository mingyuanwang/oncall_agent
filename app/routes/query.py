# 查询入口（用户提问）
from flask import Blueprint, request, jsonify, Response, stream_with_context
from typing import Dict, Any, List
import asyncio

from core.memory.memory_store import MemoryStore
from core.planning.planner import Planner
from core.react_executor.react_agent import ReactAgent
from core.memory.memory_updater import MemoryUpdater
from utils.logging_config import get_logger

logger = get_logger(__name__)

bp = Blueprint('oncall_query_api', __name__, url_prefix='/api/v1/query')

@bp.route("/", methods=['POST'], strict_slashes=False)
@bp.route("/stream", methods=['POST'], strict_slashes=False)
def query_endpoint():
    """
    用户查询处理主入口
    完整流程：记忆检索 -> 规划 -> 执行 -> 记忆更新
    """

    try:
        data = request.get_json()
        logger.info(f"收到查询请求: {data.get('question')}")
        if not data or 'question' not in data:
            logger.error("查询请求缺少必要字段: question")
            return jsonify({'error': 'Missing required field: question'}), 400

        # 1. 记忆检索
        logger.info("开始记忆检索")
        memory_store = MemoryStore()
        context_chunks = asyncio.run(memory_store.retrieve_memory(
            query=data['question'],
            user_id=data.get('user_id', 'default')
        ))
        logger.info(f"记忆检索完成，检索到 {len(context_chunks)} 个相关片段")
        
        # 2. 规划模块
        logger.info("开始规划步骤")
        planner = Planner()
        plan_steps = asyncio.run(planner.generate_plan(
            query=data['question'],
            context_chunks=context_chunks
        ))
        logger.info(f"规划完成，生成 {len(plan_steps)} 个执行步骤：{plan_steps}")

        # 3. Agent 执行
        logger.info("开始执行计划")
        react_agent = ReactAgent()
        execution_result = asyncio.run(react_agent.execute_plan(
            query=data['question'],
            plan_steps=plan_steps,
            context_chunks=context_chunks
        ))
        logger.info(f"计划执行完成，执行结果: {execution_result.get('success')}")
        
        # 4. 记忆更新
        logger.info("开始记忆更新")
        memory_updater = MemoryUpdater()
        memory_traces = asyncio.run(memory_updater.update_memory(
            query=data['question'],
            plan_steps=plan_steps,
            execution_result=execution_result,
            user_id=data.get('user_id', 'default')
        ))
        logger.info(f"记忆更新完成，更新 {len(memory_traces)} 条记忆轨迹")
        
        # 检查是否是流式请求
        if request.path.endswith('/stream'):
            logger.info("返回流式响应")
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
            logger.info("返回标准JSON响应")
            # 标准JSON响应
            return jsonify({
                'answer': execution_result["final_answer"],
                'plan_steps': plan_steps,
                'intermediate_results': execution_result["intermediate_results"],
                'memory_traces': memory_traces
            })
        
    except Exception as e:
        logger.error(f"查询处理失败: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500