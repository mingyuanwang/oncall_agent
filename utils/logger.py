# 日志工具
import logging
from typing import Dict, Any

def setup_logger(name: str, level: int = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def log_event(logger, event: str, data: Dict[str, Any] = None):
    if data:
        logger.info(f"{event}: {data}")
    else:
        logger.info(event) 