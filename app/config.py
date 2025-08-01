# 配置项（API key/路径等）
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/memory.db")
    LOGS_PATH = os.getenv("LOGS_PATH", "data/logs")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo") 