#!/usr/bin/env python3
"""简单的日志测试脚本，用于验证新日志配置"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_config import get_logger

# 获取日志记录器
logger = get_logger(__name__)

def test_basic_logging():
    """测试基本日志功能"""
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    try:
        raise ValueError("测试异常")
    except Exception as e:
        logger.exception("这是异常信息")

if __name__ == "__main__":
    test_basic_logging()
    print("日志测试完成")