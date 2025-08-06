# 大语言模型推理
from typing import Dict, Any, List, Optional
import asyncio
import json
import aiohttp
import openai
from app.config import Config

class LLMInference:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.model_name = Config.MODEL_NAME or "qwen3:4b"
        self.ollama_url = Config.OLLAMA_URL or "http://localhost:11434/api/chat"
        self.client = None
        
        # 如果提供了OpenAI API key，使用OpenAI
        if self.api_key:
            try:
                self.client = openai.AsyncOpenAI(api_key=self.api_key)
                self.provider = "openai"
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.provider = "ollama"
        else:
            # 默认使用Ollama
            self.provider = "ollama"
            print(f"Using Ollama at {self.ollama_url}")
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Dict[str, Any] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """生成响应"""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            if self.provider == "openai" and self.client:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
            else:
                # 使用Ollama本地服务
                return await self._call_ollama(messages, max_tokens, temperature)
                
        except Exception as e:
            print(f"LLM inference failed: {e}")
            return f"生成响应时出错：{str(e)}"
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """聊天完成"""
        try:
            if self.provider == "openai" and self.client:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
            else:
                # 使用Ollama本地服务
                return await self._call_ollama(messages, max_tokens, temperature)
                
        except Exception as e:
            print(f"Chat completion failed: {e}")
            return f"聊天完成时出错：{str(e)}"
    
    async def generate_structured_response(
        self, 
        prompt: str, 
        expected_format: str = "JSON"
    ) -> Dict[str, Any]:
        """生成结构化响应"""
        try:
            structured_prompt = f"""
{prompt}

请以{expected_format}格式返回响应。
"""
            
            response = await self.generate_response(structured_prompt)
            
            if expected_format.upper() == "JSON":
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse JSON response", "raw": response}
            else:
                return {"response": response}
                
        except Exception as e:
            return {"error": f"Structured response generation failed: {str(e)}"}
    
    async def _call_ollama(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """调用本地Ollama服务"""
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.ollama_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["message"]["content"]
                    else:
                        error = await response.text()
                        return f"Ollama请求失败: {error}"
        except Exception as e:
            print(f"Ollama调用失败: {e}")
            return f"调用本地Ollama服务时出错: {str(e)}"
            
    async def generate_with_system_prompt(
        self, 
        system_prompt: str, 
        user_prompt: str
    ) -> str:
        """使用系统提示词生成响应"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            return await self.chat_completion(messages)
            
        except Exception as e:
            print(f"System prompt generation failed: {e}")
            return f"使用系统提示词生成时出错：{str(e)}"