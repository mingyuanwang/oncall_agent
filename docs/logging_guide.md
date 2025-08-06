# 日志配置使用指南

## 概述

本项目现在使用新的日志配置模块 (`utils/logging_config.py`)，提供了更灵活和强大的日志功能。该模块支持多种日志级别、格式化输出和文件存储。

## 日志级别

日志级别从低到高依次为：
- DEBUG: 详细的调试信息
- INFO: 一般性信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误信息

## 使用方法

在需要记录日志的模块中，按以下方式导入和使用日志记录器：

```python
from utils.logging_config import get_logger

logger = get_logger(__name__)

# 记录不同级别的日志
logger.debug("这是调试信息")
logger.info("这是普通信息")
logger.warning("这是警告信息")
logger.error("这是错误信息")

# 记录异常信息
try:
    # 一些可能出错的代码
    pass
except Exception as e:
    logger.exception("发生了异常")
```

## 配置详情

日志配置在 `utils/logging_config.py` 文件中定义，主要包括：

1. 三种格式化器：
   - standard: 标准格式，包含时间、日志级别、模块名和消息
   - detailed: 详细格式，包含时间、日志级别、模块名、函数名、行号和消息
   - simple: 简单格式，只包含日志级别和消息

2. 两种处理器：
   - default: 控制台输出处理器
   - file: 文件输出处理器，日志文件存储在 `data/logs/app.log`

3. 根日志记录器配置了INFO级别和两种处理器

## 日志文件

日志文件存储在 `data/logs/app.log`，会自动按日期轮转。