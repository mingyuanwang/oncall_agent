# 查询入口（用户提问）
from flask import Blueprint, request, jsonify, Response, stream_with_context
from typing import Dict, Any, List, Tuple
import asyncio
import json

from core.memory.memory_store import MemoryStore
from core.planning.planner import Planner
from core.react_executor.react_agent import ReactAgent
from core.memory.memory_updater import MemoryUpdater
from utils.logging_config import get_logger

logger = get_logger(__name__)

bp = Blueprint('oncall_query_api', __name__, url_prefix='/api/v1/query')



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
            def error_stream():
                yield json.dumps({
                      'stage': 'error',
                    'status': 'failed',
                    'message': '请求参数错误',
                'details': {
                    'error_type': '缺少必填字段',
                    'required_field': 'question',
                    'description': '请提供您想要查询的问题内容'
                }
                }, ensure_ascii=False) + '\n'
            return Response(
                stream_with_context(error_stream()),
                content_type='application/jsonlines',
                status=400
            )

        logger.info("返回流式响应")
        
        def generate_stream():
            # 1. 记忆检索阶段
            yield json.dumps({
                'stage': 'memory_retrieval',
                'status': 'started',
                'message': '正在查找相关信息',
                'details': {
                    'description': '系统正在搜索与您的问题相关的历史记录和上下文信息'
                }
            }, ensure_ascii=False) + '\n'
            
            # 执行记忆检索
            memory_store = MemoryStore()
            context_chunks = asyncio.run(memory_store.retrieve_memory(
                query=data['question'],
                user_id=data.get('user_id', 'default')
            ))
            yield json.dumps({
                'stage': 'memory_retrieval',
                'status': 'completed',
                'message': '信息检索完成',
                'details': {
                    'description': f'找到 {len(context_chunks)} 个相关信息片段',
                    'context_count': len(context_chunks),
                    'next_step': '正在为您制定解决方案'
                }
            }, ensure_ascii=False) + '\n'
            
            # 2. 规划阶段
            yield json.dumps({
                'stage': 'planning',
                'status': 'started',
                'message': '正在制定解决方案',
                'details': {
                    'description': '系统正在分析信息并生成解决问题的步骤计划'
                }
            }, ensure_ascii=False) + '\n'
            
            # 执行规划
            planner = Planner()
            plan_steps = asyncio.run(planner.generate_plan(
                query=data['question'],
                context_chunks=context_chunks
            ))
            yield json.dumps({
                'stage': 'planning',
                'status': 'completed',
                'message': '解决方案已生成',
                'details': {
                    'description': f'已创建 {len(plan_steps)} 个执行步骤',
                    'step_count': len(plan_steps),
                    'steps': [{'step': i+1, 'action': step} for i, step in enumerate(plan_steps)]
                }
            }, ensure_ascii=False) + '\n'
            
            # 3. 执行阶段
            yield json.dumps({
                'stage': 'execution',
                'status': 'started',
                'message': '正在执行解决方案',
                'details': {
                    'description': '系统正在按照计划步骤解决您的问题'
                }
            }, ensure_ascii=False) + '\n'
            
            # 执行计划
            react_agent = ReactAgent()
            execution_result = asyncio.run(react_agent.execute_plan(
                query=data['question'],
                plan_steps=plan_steps,
                context_chunks=context_chunks
            ))
            yield json.dumps({
                'stage': 'execution',
                'status': 'completed',
                'message': '解决方案执行完成',
                'details': {
                    'description': '问题解决步骤已执行完毕',
                    'success': execution_result.get('success'),
                    'intermediate_steps': len(execution_result.get('intermediate_results', [])),
                    'key_findings': execution_result.get('intermediate_results', [])[-1] if execution_result.get('intermediate_results') else 'No intermediate findings'
                }
            }, ensure_ascii=False) + '\n'
            
            # 4. 记忆更新阶段
            yield json.dumps({
                'stage': 'memory_update',
                'status': 'started',
                'message': '正在保存对话记录',
                'details': {
                    'description': '系统正在记录本次交互的重要信息以便将来参考'
                }
            }, ensure_ascii=False) + '\n'
            
            # 执行记忆更新
            memory_updater = MemoryUpdater()
            memory_traces = asyncio.run(memory_updater.update_memory(
                query=data['question'],
                plan_steps=plan_steps,
                execution_result=execution_result,
                user_id=data.get('user_id', 'default')
            ))
            yield json.dumps({
                'stage': 'memory_update',
                'status': 'completed',
                'message': '对话记录已保存',
                'details': {
                    'description': f'已更新 {len(memory_traces)} 条记忆信息',
                    'trace_count': len(memory_traces),
                    'memory_type': 'episodic'
                }
            }, ensure_ascii=False) + '\n'
            
            # 最终结果阶段
            formatted_answer = execution_result['final_answer']
            yield json.dumps({
                'stage': 'final_result',
                'status': 'completed',
                'message': '查询处理完成',
                'details': {
                    'description': '您的问题已处理完毕，以下是结果摘要',
                    'answer': formatted_answer,
                    'process_summary': [
                        f'1. 找到 {len(context_chunks)} 条相关信息',
                        f'2. 生成 {len(plan_steps)} 个解决步骤',
                        f'3. 完成执行并保存 {len(memory_traces)} 条记录'
                    ]
                }
            }, ensure_ascii=False) + '\n'
            
        return Response(
            stream_with_context(generate_stream()),
            content_type='application/jsonlines'
        )
        
    except Exception as e:
        logger.error(f"查询处理失败: {str(e)}")
        def error_stream():
            yield json.dumps({
                'stage': 'error',
                'status': 'failed',
                'message': 'Internal server error',
                'error': str(e)
            }) + '\n'
        return Response(
            stream_with_context(error_stream()),
            content_type='application/jsonlines',
            status=500
        )