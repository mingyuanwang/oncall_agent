# 大语言模型推理
from typing import Dict, Any, List, Optional
import asyncio
import json
import openai
from app.config import Config

class LLMInference:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.model_name = Config.MODEL_NAME
        self.client = None
        
        if self.api_key:
            try:
                self.client = openai.AsyncOpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Dict[str, Any] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """生成响应"""
        try:
            if not self.client:
                return "LLM service not available"
            
            messages = [{"role": "user", "content": prompt}]
            
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
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
            if not self.client:
                return "LLM service not available"
            
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
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