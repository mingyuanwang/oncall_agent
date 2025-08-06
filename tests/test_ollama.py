#!/usr/bin/env python3
"""测试Ollama本地服务"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置Ollama模型名称
os.environ['MODEL_NAME'] = 'qwen3:4b'
print(f"已设置MODEL_NAME环境变量: {os.environ.get('MODEL_NAME')}")

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
print(f"已添加项目根目录到Python路径: {project_root}")
print(f"当前Python路径: {sys.path}")

from models.llm_inference import LLMInference
from app.config import Config
print(f"Config.MODEL_NAME: {Config.MODEL_NAME}")
print(f"环境变量MODEL_NAME: {os.environ.get('MODEL_NAME')}")

async def test_ollama():
    """测试Ollama服务"""
    print("正在测试Ollama本地服务...")
    
    # 初始化LLM推理器
    # 设置模型名称为llama3
    os.environ['MODEL_NAME'] = 'llama3'
    llm = LLMInference()
    print(f"使用提供商: {llm.provider}")
    print(f"模型名称: {llm.model_name}")
    print(f"Ollama URL: {llm.ollama_url}")
    
    # 测试简单对话
    try:
        response = await llm.generate_response("你好，请介绍一下Python爬虫的基本概念")
        print(f"\n响应: {response}")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

async def test_chat_completion():
    """测试聊天完成功能"""
    print("\n正在测试聊天完成功能...")
    
    llm = LLMInference()
    messages = [
        {"role": "user", "content": "写一个Python爬虫来抓取网页标题"}
    ]
    
    try:
        response = await llm.chat_completion(messages)
        print(f"\n聊天响应: {response}")
        return True
    except Exception as e:
        print(f"聊天测试失败: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("=== Ollama本地服务测试 ===")
        
        # 测试基本响应
        success1 = await test_ollama()
        
        # 测试聊天完成
        success2 = await test_chat_completion()
        
        if success1 and success2:
            print("\n✅ 所有测试通过！Ollama服务正常工作")
        else:
            print("\n❌ 部分测试失败，请检查Ollama服务是否运行")
            print("请确保：")
            print("1. Ollama已安装并运行 (ollama serve)")
            print("2. llama3模型已下载 (ollama pull llama3)")
            print("3. 服务端口为 11434")
    
    asyncio.run(main())