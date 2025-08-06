# Memory Agent Project

## 目录结构

```
memory_agent_project/
├── README.md
├── requirements.txt
├── app/                            # 主程序入口与路由管理
│   ├── main.py                     # FastAPI/Flask 入口
│   ├── config.py                   # 配置项（API key/路径等）
│   └── routes/
│       ├── query.py                # 查询入口（用户提问）
│       └── train.py                # 自学习更新入口
├── core/                           # 系统核心逻辑
│   ├── memory/
│   │   ├── episodic_memory.py      # 短期/长期记忆结构
│   │   ├── memory_builder.py       # 记忆构建/更新模块
│   │   └── memory_optimizer.py     # 记忆优化与清洗
│   ├── retrieval/
│   │   ├── semantic_matcher.py     # 向量召回/语义匹配
│   │   ├── query_expander.py       # 查询扩展模块
│   │   └── reranker.py             # 结果重排模块
│   ├── planning/
│   │   ├── planner.py              # 任务规划器（大模型驱动）
│   │   └── decision_engine.py      # 策略与多方案评估
│   ├── react_executor/
│   │   ├── reasoner.py             # 推理模块
│   │   ├── actor.py                # 动作执行器（工具调用）
│   │   └── observer.py             # 工具结果观察/反馈处理
│   ├── learning/
│   │   ├── trajectory_extractor.py # 执行轨迹提取（记忆轨迹）
│   │   ├── knowledge_integrator.py # 多步经验融合
│   │   └── learner.py              # 自学习模块主逻辑
├── data/                           # 本地知识数据
│   ├── memory.db                   # SQLite 数据库
│   └── faiss_index                 # FAISS 向量索引文件
│   └── logs/                       # 执行轨迹、反馈等日志
├── models/                         # 本地模型或调用 OpenAI/HuggingFace 等接口
│   ├── embedding_model.py
│   ├── llm_inference.py
│   └── tool_wrappers.py            # 第三方工具封装
├── utils/
│   ├── logger.py
│   ├── schema.py                   # 通用数据结构定义（pydantic）
│   └── helpers.py
└── tests/                          # 单元测试与集成测试
    └── ...
```

## 简介

Memory Agent Project 是一个智能体记忆管理、推理与规划的 Python 项目，基于 FastAPI/Flask 构建，支持本地向量数据库和自学习能力。 
# 安装依赖
pip install -r requirements.txt

# 如果FAISS安装失败，可以单独安装
pip install faiss-cpu

# 初始化FAISS索引目录
python scripts/init_faiss.py

# 运行服务

## 普通启动
python app/main.py

## Debug启动
python app/main.py --debug