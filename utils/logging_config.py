#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
"""
import logging
import logging.config
import os
from pathlib import Path

# 默认日志配置
DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'detailed',
            'class': 'logging.FileHandler',
            'filename': 'data/logs/app.log',
            'mode': 'a',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        '': {  # 根日志记录器
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

def setup_logging(log_level: str = None, log_file: str = None):
    """
    设置日志配置
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径
    """
    # 创建日志目录
    log_dir = Path('data/logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制默认配置
    config = DEFAULT_LOGGING_CONFIG.copy()
    
    # 如果指定了日志级别，则更新所有处理器的日志级别
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
        config['handlers']['default']['level'] = level
        config['handlers']['file']['level'] = level
        config['loggers']['']['level'] = level
    
    # 如果指定了日志文件，则更新文件处理器
    if log_file:
        config['handlers']['file']['filename'] = log_file
    
    # 应用配置
    logging.config.dictConfig(config)

def get_logger(name: str):
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)