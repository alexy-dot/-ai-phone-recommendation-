#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM服务提供者
集成大语言模型API，提供智能对话和需求理解能力
支持Gemini、Kimi和Ark API
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """LLM配置"""
    api_key: str
    model_name: str = "gemini-pro"
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/models"
    max_tokens: int = 1000
    temperature: float = 0.7
    api_type: str = "gemini"  # gemini, kimi, ark

class LLMProvider:
    """LLM服务提供者"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or self._load_default_config()
        self.conversation_history: List[Dict] = []
    
    def _load_default_config(self) -> LLMConfig:
        """加载默认配置"""
        # 首先尝试从配置文件加载
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                print(f"✅ 成功加载配置文件: {config_file}")
                print(f"📋 配置内容: {config_data}")
                
                # 检查API类型
                if 'ARK_API_KEY' in config_data:
                    print("🔧 检测到Ark API配置")
                    # Ark API配置
                    config = LLMConfig(
                        api_key=config_data.get('ARK_API_KEY', ''),
                        model_name=config_data.get('LLM_MODEL_NAME', 'doubao-seed-1-6-250615'),
                        base_url=config_data.get('LLM_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3'),
                        max_tokens=config_data.get('max_tokens', 1000),
                        temperature=config_data.get('temperature', 0.7),
                        api_type="ark"
                    )
                elif config_data.get('LLM_MODEL_NAME', '').startswith('kimi'):
                    print("🔧 检测到Kimi API配置")
                    # Kimi API配置
                    config = LLMConfig(
                        api_key=config_data.get('GEMINI_API_KEY', ''),
                        model_name=config_data.get('LLM_MODEL_NAME', 'kimi-k2-250711'),
                        base_url="https://kimi.moonshot.cn/api/chat",
                        max_tokens=config_data.get('max_tokens', 1000),
                        temperature=config_data.get('temperature', 0.7),
                        api_type="kimi"
                    )
                else:
                    print("🔧 检测到Gemini API配置")
                    # Gemini API配置
                    config = LLMConfig(
                        api_key=config_data.get('GEMINI_API_KEY', ''),
                        model_name=config_data.get('LLM_MODEL_NAME', 'gemini-pro'),
                        base_url=config_data.get('base_url', 'https://generativelanguage.googleapis.com/v1beta/models'),
                        max_tokens=config_data.get('max_tokens', 1000),
                        temperature=config_data.get('temperature', 0.7),
                        api_type="gemini"
                    )
                
                print(f"🔑 API密钥长度: {len(config.api_key)} 字符")
                print(f"🤖 模型名称: {config.model_name}")
                print(f"🌐 API地址: {config.base_url}")
                print(f"📡 API类型: {config.api_type}")
                return config
            except Exception as e:
                print(f"❌ 加载配置文件失败: {e}")
        
        # 如果配置文件不存在或加载失败，尝试环境变量
        api_key = os.getenv('ARK_API_KEY') or os.getenv('GEMINI_API_KEY', '')
        if not api_key:
            print("⚠️ 警告: 未找到配置文件或环境变量，LLM功能将不可用")
        else:
            print("🔧 从环境变量加载API密钥")
        
        return LLMConfig(api_key=api_key)
    
    def _make_api_request(self, prompt: str, context: str = "") -> Optional[str]:
        """发送API请求"""
        if not self.config.api_key:
            return None
        
        try:
            # 根据API类型选择请求方法
            if self.config.api_type == "ark":
                return self._make_ark_request(prompt, context)
            elif self.config.api_type == "kimi":
                return self._make_kimi_request(prompt, context)
            else:
                return self._make_gemini_request(prompt, context)
        except Exception as e:
            print(f"LLM API请求失败: {e}")
            return None

    def _make_ark_request(self, prompt: str, context: str = "") -> Optional[str]:
        """发送Ark API请求 - 使用正确的API调用方式"""
        try:
            from openai import OpenAI
            
            # 初始化Ark客户端
            client = OpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key,
                timeout=60.0
            )
            
            # 构建消息
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            print(f"正在发送Ark API请求到: {self.config.base_url}")
            print(f"使用模型: {self.config.model_name}")
            
            # 发送请求
            completion = client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            print(f"API请求成功")
            
            # 返回响应内容
            if completion.choices and completion.choices[0].message:
                return completion.choices[0].message.content
            
            return None
            
        except Exception as e:
            print(f"Ark API请求失败: {e}")
            return None

    def _make_kimi_request(self, prompt: str, context: str = "") -> Optional[str]:
        """发送Kimi API请求"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}"
            }
            
            data = {
                "messages": [
                    {"role": "user", "content": f"{context}\n\n{prompt}"}
                ],
                "model": self.config.model_name,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": False  # 添加stream参数
            }
            
            print(f"正在发送Kimi API请求到: {self.config.base_url}")
            print(f"使用模型: {self.config.model_name}")
            
            response = requests.post(
                self.config.base_url,
                headers=headers,
                json=data,
                timeout=60,  # 增加超时时间到60秒
                verify=True  # 确保SSL验证
            )
            
            print(f"API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"API响应内容: {result}")
                if 'choices' in result and result['choices']:
                    return result['choices'][0]['message']['content']
                else:
                    print(f"API响应格式异常: {result}")
            else:
                print(f"API请求失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
            
            return None
            
        except requests.exceptions.Timeout:
            print("Kimi API请求超时，请检查网络连接")
            return None
        except requests.exceptions.ConnectionError:
            print("无法连接到Kimi API服务器，请检查网络连接")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Kimi API请求异常: {e}")
            return None
        except Exception as e:
            print(f"Kimi API请求未知错误: {e}")
            return None

    def _make_gemini_request(self, prompt: str, context: str = "") -> Optional[str]:
        """发送Gemini API请求"""
        url = f"{self.config.base_url}/{self.config.model_name}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        full_prompt = f"{context}\n\n用户: {prompt}\n\n助手:"
        
        data = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_tokens,
            }
        }
        
        response = requests.post(
            url,
            headers=headers,
            params={"key": self.config.api_key},
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and result['candidates']:
                return result['candidates'][0]['content']['parts'][0]['text']
        
        return None
    
    def understand_intent(self, user_input: str, context: str = "") -> Dict[str, Any]:
        """理解用户意图"""
        # 首先尝试LLM API
        if self.is_available():
            prompt = f"""
请分析以下用户输入的意图和关键信息，返回JSON格式的结果：

用户输入: {user_input}

请返回包含以下字段的JSON:
{{
    "intent": "查询|比较|澄清|闲聊",
    "budget_min": 数字或null,
    "budget_max": 数字或null,
    "preferences": ["偏好1", "偏好2"],
    "priority": "性能|拍照|续航|便携|价格|外观",
    "clarification_needed": true/false,
    "confidence": 0.0-1.0
}}

只返回JSON，不要其他内容。
"""
            
            response = self._make_api_request(prompt, context)
            if response and response.strip():  # 确保response不为None且不为空字符串
                try:
                    return json.loads(response.strip())
                except json.JSONDecodeError:
                    print(f"JSON解析失败，响应内容: {response}")
                    pass
        
        # 如果LLM不可用或失败，使用本地回退
        print("🔄 使用本地意图理解引擎")
        return self.get_fallback_response("understand_intent", user_input=user_input)
    
    def generate_clarification_question(self, unclear_aspect: str, context: str = "", conversation_history: List[Dict] = None) -> str:
        """生成智能澄清问题"""
        # 首先尝试LLM API
        if self.is_available():
            # 构建更智能的提示词
            history_context = ""
            if conversation_history:
                recent_messages = conversation_history[-3:]  # 最近3条消息
                history_context = "\n".join([f"用户: {msg.get('user', '')}" for msg in recent_messages])
            
            prompt = f"""
你是一个专业的手机导购助手。用户的需求中"{unclear_aspect}"方面不够明确，请生成一个自然、友好、个性化的澄清问题。

对话历史:
{history_context}

当前上下文: {context}

要求:
1. 问题要自然、友好，像真人导购一样
2. 避免重复之前问过的问题
3. 根据对话历史调整问题风格
4. 问题要具体、有针对性
5. 可以结合用户之前提到的其他信息

请生成一个简洁、自然的澄清问题，直接返回问题内容，不要其他解释。
"""
            
            response = self._make_api_request(prompt)
            if response and response.strip():  # 确保response不为None且不为空字符串
                return response.strip()
        
        # 如果LLM不可用或失败，使用智能本地回退
        print("🔄 使用智能本地澄清问题生成")
        return self._smart_fallback_clarification_question(unclear_aspect, context, conversation_history)
    
    def _smart_fallback_clarification_question(self, unclear_aspect: str, context: str = "", conversation_history: List[Dict] = None) -> str:
        """智能本地澄清问题回退"""
        import random
        
        # 检查是否已经问过类似问题
        asked_questions = []
        if conversation_history:
            for msg in conversation_history:
                if 'system' in msg and '澄清' in str(msg.get('system', '')):
                    asked_questions.append(str(msg.get('system', '')))
        
        # 根据不同的不清楚方面生成多样化的问题
        question_templates = {
            "budget": [
                "您的预算大概是多少呢？",
                "请问您能接受的价格范围是？",
                "您希望购买什么价位的手机？",
                "价格方面您有什么考虑吗？",
                "您觉得什么价位的手机比较合适？",
                "您能告诉我大概的预算范围吗？",
                "价格对您来说重要吗？",
                "您希望控制在什么价格区间？"
            ],
            "performance": [
                "您主要用手机做什么呢？游戏、工作还是日常使用？",
                "您对手机性能有什么特殊要求吗？",
                "您会玩大型游戏吗？",
                "平时使用手机主要是哪些场景？",
                "您希望手机运行速度怎么样？",
                "您需要处理复杂的任务吗？",
                "您对手机流畅度有什么要求？",
                "您会同时运行多个应用吗？"
            ],
            "camera": [
                "您更注重夜景拍摄还是广角拍摄？",
                "拍照方面，您更看重哪个功能？",
                "您主要用手机拍什么类型的照片？",
                "您对拍照有什么特殊需求吗？",
                "您希望手机拍照效果怎么样？",
                "您经常拍照吗？",
                "您对相机功能有什么偏好吗？",
                "您希望拍出什么样的照片？"
            ],
            "battery": [
                "您对续航有什么要求？",
                "您希望手机能用多久？",
                "快充功能对您重要吗？",
                "您平时使用手机的时间长吗？",
                "您希望电池续航怎么样？",
                "您经常外出吗？",
                "您对充电速度有要求吗？",
                "您希望多久充一次电？"
            ],
            "portability": [
                "您更偏好大屏还是小屏手机？",
                "便携性对您来说重要吗？",
                "您希望手机轻便一些还是功能更全面？",
                "您平时会把手机放在哪里？",
                "您对手机尺寸有什么偏好吗？",
                "您希望手机容易携带吗？",
                "您对手机重量有要求吗？",
                "您喜欢单手操作吗？"
            ],
            "appearance": [
                "您对外观有什么偏好吗？",
                "您喜欢什么颜色的手机？",
                "您更看重手机的设计还是功能？",
                "您对手机外观有什么要求吗？",
                "您希望手机看起来怎么样？",
                "您对手机材质有偏好吗？",
                "您希望手机时尚一些吗？",
                "您对手机造型有什么想法？"
            ],
            "brand": [
                "您对品牌有什么偏好吗？",
                "您更倾向于哪个品牌的手机？",
                "您有什么品牌偏好或忌讳吗？",
                "您希望购买什么品牌的手机？",
                "您对手机品牌有什么考虑吗？",
                "您有喜欢的手机品牌吗？",
                "您对某些品牌有偏见吗？",
                "您希望尝试新品牌吗？"
            ],
            "usage_scenario": [
                "您主要用手机做什么呢？",
                "您平时使用手机的场景有哪些？",
                "您希望手机能满足哪些需求？",
                "您使用手机的主要目的是什么？",
                "您希望手机在哪些方面表现突出？",
                "您的生活中哪些场景需要用到手机？",
                "您希望手机成为什么样的工具？",
                "您对手机有什么期待？"
            ]
        }
        
        # 根据上下文调整问题类型
        if unclear_aspect == "general_preference":
            # 如果是一般偏好，根据上下文选择最合适的问题类型
            if "拍照" in context or "相机" in context:
                unclear_aspect = "camera"
            elif "游戏" in context or "性能" in context:
                unclear_aspect = "performance"
            elif "续航" in context or "电池" in context:
                unclear_aspect = "battery"
            elif "轻便" in context or "大屏" in context:
                unclear_aspect = "portability"
            else:
                unclear_aspect = "usage_scenario"
        
        # 获取问题模板
        templates = question_templates.get(unclear_aspect, question_templates["usage_scenario"])
        
        # 避免重复问题
        available_questions = [q for q in templates if not any(q in asked for asked in asked_questions)]
        
        if not available_questions:
            # 如果所有模板都用过了，生成一个通用但个性化的问题
            return f"关于{unclear_aspect}方面，您还有什么特殊要求吗？"
        
        # 随机选择一个未问过的问题
        return random.choice(available_questions)
    
    def generate_recommendation_explanation(self, phone_name: str, reasons: List[str], 
                                         user_demand: str) -> str:
        """生成推荐解释"""
        # 首先尝试LLM API
        if self.is_available():
            prompt = f"""
请为以下手机推荐生成一个自然、详细的解释：

手机: {phone_name}
推荐理由: {', '.join(reasons)}
用户需求: {user_demand}

请生成一段自然的推荐解释，说明为什么这款手机适合用户的需求。
"""
            
            response = self._make_api_request(prompt)
            if response and response.strip():  # 确保response不为None且不为空字符串
                return response.strip()
        
        # 如果LLM不可用或失败，使用本地回退
        print("🔄 使用本地推荐解释生成")
        return self.get_fallback_response("generate_recommendation_explanation", 
                                        phone_name=phone_name, reasons=reasons, user_demand=user_demand)
    
    def generate_comparison_report(self, phones: List[Dict], user_demand: str) -> str:
        """生成对比报告"""
        # 首先尝试LLM API
        if self.is_available():
            phone_info = "\n".join([
                f"- {phone['name']}: ¥{phone['price']}, {phone['cpu']}, {phone['camera_mp']}MP"
                for phone in phones
            ])
            
            prompt = f"""
请为以下手机生成一个详细的对比分析报告：

用户需求: {user_demand}

对比手机:
{phone_info}

请从性能、拍照、续航、便携性、价格等方面进行详细对比分析，给出购买建议。
"""
            
            response = self._make_api_request(prompt)
            if response and response.strip():  # 确保response不为None且不为空字符串
                return response.strip()
        
        # 如果LLM不可用或失败，使用本地回退
        print("🔄 使用本地对比报告生成")
        return self.get_fallback_response("generate_comparison_report", phones=phones, user_demand=user_demand)
    
    def is_available(self) -> bool:
        """检查LLM服务是否可用"""
        if not self.config.api_key:
            return False
        
        # 对于Ark API，我们直接返回True，因为我们已经测试过它可以工作
        if self.config.api_type == "ark":
            return True
        
        # 尝试简单的网络连接测试
        try:
            if self.config.api_type == "kimi":
                response = requests.get(self.config.base_url, timeout=5)
            else:
                response = requests.get("https://generativelanguage.googleapis.com", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_fallback_response(self, method: str, **kwargs) -> Any:
        """获取本地回退响应"""
        if method == "understand_intent":
            return self._fallback_understand_intent(kwargs.get('user_input', ''))
        elif method == "generate_clarification_question":
            return self._fallback_clarification_question(kwargs.get('unclear_aspect', ''))
        elif method == "generate_recommendation_explanation":
            return self._fallback_recommendation_explanation(
                kwargs.get('phone_name', ''),
                kwargs.get('reasons', []),
                kwargs.get('user_demand', '')
            )
        elif method == "generate_comparison_report":
            return self._fallback_comparison_report(
                kwargs.get('phones', []),
                kwargs.get('user_demand', '')
            )
        return None
    
    def _fallback_understand_intent(self, user_input: str) -> Dict[str, Any]:
        """本地意图理解回退"""
        # 简单的关键词匹配
        user_input_lower = user_input.lower()
        
        # 预算提取
        budget_min = None
        budget_max = None
        if '预算' in user_input or '价格' in user_input:
            import re
            # 匹配数字范围
            budget_patterns = [
                r'(\d+)-(\d+)',  # 3000-4000
                r'(\d+)到(\d+)',  # 3000到4000
                r'(\d+)以下',     # 4000以下
                r'(\d+)以内',     # 4000以内
                r'(\d+)以上',     # 3000以上
            ]
            
            for pattern in budget_patterns:
                matches = re.findall(pattern, user_input)
                if matches:
                    if len(matches[0]) == 2:
                        budget_min = int(matches[0][0])
                        budget_max = int(matches[0][1])
                    else:
                        if '以下' in user_input or '以内' in user_input:
                            budget_max = int(matches[0])
                        elif '以上' in user_input:
                            budget_min = int(matches[0])
                    break
        
        # 偏好提取
        preferences = []
        preference_keywords = {
            '拍照': ['拍照', '相机', '摄像', '摄影'],
            '性能': ['性能', '游戏', '处理器', 'cpu', '发热'],
            '续航': ['续航', '电池', '充电'],
            '便携': ['便携', '轻便', '重量', '尺寸'],
            '外观': ['外观', '颜值', '设计', '颜色']
        }
        
        for category, keywords in preference_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                preferences.append(category)
        
        # 优先级判断
        priority = None
        if preferences:
            priority = preferences[0]
        
        return {
            "intent": "查询",
            "budget_min": budget_min,
            "budget_max": budget_max,
            "preferences": preferences,
            "priority": priority,
            "clarification_needed": len(preferences) < 2 or (budget_min is None and budget_max is None),
            "confidence": 0.7
        }
    
    def _fallback_clarification_question(self, unclear_aspect: str) -> str:
        """本地澄清问题回退"""
        questions = {
            "budget": "您的预算大概是多少呢？",
            "performance": "您对手机性能有什么特殊要求吗？",
            "camera": "您更注重夜景拍摄还是广角拍摄？",
            "battery": "您对续航有什么要求？",
            "portability": "您更偏好大屏还是小屏手机？",
            "appearance": "您对外观有什么偏好吗？"
        }
        return questions.get(unclear_aspect, "能详细说明一下您的需求吗？")
    
    def _fallback_recommendation_explanation(self, phone_name: str, reasons: List[str], user_demand: str) -> str:
        """本地推荐解释回退"""
        return f"我推荐{phone_name}，因为{', '.join(reasons)}。这款手机应该能满足您的需求。"
    
    def _fallback_comparison_report(self, phones: List[Dict], user_demand: str) -> str:
        """本地对比报告回退"""
        if not phones:
            return "暂无对比数据"
        
        report = f"基于您的需求'{user_demand}'，我为您对比了{len(phones)}款手机：\n\n"
        
        for i, phone in enumerate(phones, 1):
            report += f"{i}. {phone.get('name', '未知型号')}\n"
            report += f"   价格: ¥{phone.get('price', '未知')}\n"
            report += f"   处理器: {phone.get('cpu', '未知')}\n"
            report += f"   摄像头: {phone.get('camera_mp', '未知')}MP\n"
            if 'battery_mah' in phone:
                report += f"   电池: {phone['battery_mah']}mAh\n"
            report += "\n"
        
        report += "建议您根据预算和具体需求选择最适合的机型。"
        return report 