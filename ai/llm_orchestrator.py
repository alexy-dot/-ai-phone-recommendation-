#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM编排器 - 统一管理所有大模型调用
完全基于大模型的智能系统核心
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from services.llm_provider import LLMProvider

@dataclass
class ConversationMemory:
    """对话记忆"""
    session_id: str
    history: List[Dict] = field(default_factory=list)
    user_preferences: Dict = field(default_factory=dict)
    asked_questions: List[str] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)

@dataclass
class AIResponse:
    """AI响应"""
    message: str
    clarification_question: Optional[str] = None
    recommendations: List[Dict] = field(default_factory=list)
    confidence: float = 0.0
    next_action: str = "continue"
    metadata: Dict = field(default_factory=dict)

class LLMOrchestrator:
    """大模型编排器 - 统一管理所有LLM调用"""
    
    def __init__(self):
        self.llm_provider = LLMProvider()
        self.conversation_memories: Dict[str, ConversationMemory] = {}
    
    def get_or_create_memory(self, session_id: str) -> ConversationMemory:
        """获取或创建对话记忆"""
        if session_id not in self.conversation_memories:
            self.conversation_memories[session_id] = ConversationMemory(session_id=session_id)
        return self.conversation_memories[session_id]
    
    def process_user_input(self, user_input: str, session_id: str, available_phones: List[Dict] = None) -> AIResponse:
        """处理用户输入 - 完全基于大模型（同步版本）"""
        
        # 获取对话记忆
        memory = self.get_or_create_memory(session_id)
        
        # 更新对话历史
        memory.history.append({
            'user': user_input,
            'timestamp': datetime.now().isoformat(),
            'type': 'user_input'
        })
        
        # 构建上下文
        context = self._build_context(memory, available_phones)
        
        # 1. 意图理解和需求提取
        intent_analysis = self._analyze_intent_and_demand(user_input, context)
        
        # 2. 根据意图生成响应
        if intent_analysis.get('needs_clarification'):
            response = self._generate_clarification_response(memory, intent_analysis, context)
        elif intent_analysis.get('ready_for_recommendation'):
            response = self._generate_recommendation_response(memory, intent_analysis, context, available_phones)
        elif intent_analysis.get('needs_comparison'):
            response = self._generate_comparison_response(memory, intent_analysis, context, available_phones)
        else:
            response = self._generate_general_response(memory, intent_analysis, context)
        
        # 更新记忆
        memory.last_update = datetime.now()
        if response.clarification_question:
            memory.asked_questions.append(response.clarification_question)
        
        return response
    
    def _build_context(self, memory: ConversationMemory, available_phones: List[Dict] = None) -> str:
        """构建对话上下文"""
        context_parts = []
        
        # 对话历史
        if memory.history:
            recent_history = memory.history[-5:]  # 最近5条
            history_text = "\n".join([
                f"用户: {msg['user']}" for msg in recent_history if msg['type'] == 'user_input'
            ])
            context_parts.append(f"对话历史:\n{history_text}")
        
        # 用户偏好
        if memory.user_preferences:
            preferences_text = ", ".join([f"{k}: {v}" for k, v in memory.user_preferences.items()])
            context_parts.append(f"用户偏好: {preferences_text}")
        
        # 已问过的问题
        if memory.asked_questions:
            asked_text = ", ".join(memory.asked_questions[-3:])  # 最近3个问题
            context_parts.append(f"已问过的问题: {asked_text}")
        
        # 可用手机信息
        if available_phones:
            phone_summary = f"可用手机数量: {len(available_phones)}"
            if available_phones:
                price_range = f"价格范围: ¥{min(p['price'] for p in available_phones)} - ¥{max(p['price'] for p in available_phones)}"
                phone_summary += f", {price_range}"
            context_parts.append(phone_summary)
        
        return "\n".join(context_parts)
    
    def _analyze_intent_and_demand(self, user_input: str, context: str) -> Dict[str, Any]:
        """分析意图和需求 - 完全基于大模型"""
        
        prompt = f"""
        作为专业的手机推荐专家，请分析用户的输入，理解其意图和需求。

        用户输入: {user_input}
        对话上下文: {context}

        请返回JSON格式的完整分析:
        {{
            "intent": "查询|比较|澄清|闲聊|购买",
            "needs_clarification": true/false,
            "ready_for_recommendation": true/false,
            "needs_comparison": true/false,
            "demand": {{
                "budget": {{
                    "min": 数字或null,
                    "max": 数字或null,
                    "preference": "严格|灵活|无要求"
                }},
                "performance": {{
                    "level": "低端|中端|高端|旗舰",
                    "usage": ["游戏", "工作", "日常"],
                    "priority": 1-10
                }},
                "camera": {{
                    "quality": "一般|良好|优秀|专业",
                    "features": ["夜景", "人像", "广角", "微距"],
                    "priority": 1-10
                }},
                "battery": {{
                    "capacity": "小|中|大",
                    "charging": "慢充|快充|无线充",
                    "priority": 1-10
                }},
                "design": {{
                    "size": "小屏|中屏|大屏",
                    "weight": "轻|中|重",
                    "style": "商务|时尚|简约",
                    "priority": 1-10
                }},
                "brand": {{
                    "preferences": ["品牌1", "品牌2"],
                    "avoid": ["品牌1", "品牌2"],
                    "priority": 1-10
                }},
                "special_requirements": ["特殊要求1", "特殊要求2"]
            }},
            "confidence": 0.0-1.0,
            "missing_info": ["缺失信息1", "缺失信息2"]
        }}

        只返回JSON，不要其他内容。
        """
        
        try:
            response = self._call_llm(prompt)
            if response and response.strip():  # 确保response不为None且不为空字符串
                return json.loads(response.strip())
            else:
                raise Exception("LLM返回空响应")
        except Exception as e:
            print(f"意图分析失败: {e}")
            return {
                "intent": "查询",
                "needs_clarification": True,
                "ready_for_recommendation": False,
                "confidence": 0.5,
                "missing_info": ["预算", "使用需求"]
            }
    
    def _generate_clarification_response(self, memory: ConversationMemory, intent_analysis: Dict, context: str) -> AIResponse:
        """生成澄清响应"""
        
        missing_info = intent_analysis.get('missing_info', [])
        
        prompt = f"""
        作为专业的手机导购，请生成一个自然、友好、有针对性的澄清问题。

        对话上下文: {context}
        缺失信息: {missing_info}
        已问过的问题: {memory.asked_questions}

        要求:
        1. 问题要自然、友好，像真人导购一样
        2. 避免重复已问过的问题
        3. 根据用户特点调整问题风格
        4. 问题要有针对性，能帮助收集关键信息
        5. 可以结合用户之前提到的信息

        请直接返回问题内容，不要其他解释。
        """
        
        try:
            question = self._call_llm(prompt)
            return AIResponse(
                message=f"我理解您的需求，让我为您推荐合适的手机。{question}",
                clarification_question=question,
                confidence=intent_analysis.get('confidence', 0.5),
                next_action="clarify"
            )
        except Exception as e:
            print(f"生成澄清问题失败: {e}")
            return AIResponse(
                message="能详细说明一下您的需求吗？比如预算、使用场景等。",
                clarification_question="能详细说明一下您的需求吗？",
                confidence=0.5,
                next_action="clarify"
            )
    
    def _generate_recommendation_response(self, memory: ConversationMemory, intent_analysis: Dict, context: str, available_phones: List[Dict]) -> AIResponse:
        """生成推荐响应"""
        
        demand = intent_analysis.get('demand', {})
        
        # 构建推荐提示词
        phones_info = []
        for i, phone in enumerate(available_phones[:20]):  # 限制前20款
            phones_info.append(f"{i+1}. {phone['name']} - ¥{phone['price']} - {phone['cpu']} - {phone['camera_mp']}MP")
        
        prompt = f"""
        作为专业的手机推荐专家，请根据用户需求推荐最适合的手机。

        用户需求: {json.dumps(demand, ensure_ascii=False, indent=2)}
        对话上下文: {context}

        可用手机:
        {chr(10).join(phones_info)}

        请返回JSON格式的推荐结果:
        {{
            "recommendations": [
                {{
                    "rank": 1,
                    "phone_id": "手机ID",
                    "name": "手机名称",
                    "price": "价格",
                    "score": 0.0-1.0,
                    "reasons": ["推荐理由1", "推荐理由2"],
                    "explanation": "详细的推荐解释"
                }}
            ],
            "summary": "推荐总结",
            "confidence": 0.0-1.0
        }}

        要求:
        1. 推荐3-5款最适合的手机
        2. 每款手机都要有详细的推荐理由
        3. 考虑用户的预算、偏好和特殊需求
        4. 提供个性化的推荐解释

        只返回JSON，不要其他内容。
        """
        
        try:
            response = self._call_llm(prompt)
            if response and response.strip():  # 确保response不为None且不为空字符串
                result = json.loads(response.strip())
                
                return AIResponse(
                    message=result.get('summary', '根据您的需求，我为您推荐以下手机：'),
                    recommendations=result.get('recommendations', []),
                    confidence=result.get('confidence', 0.8),
                    next_action="recommend",
                    metadata={'recommendation_count': len(result.get('recommendations', []))}
                )
            else:
                raise Exception("LLM返回空响应")
        except Exception as e:
            print(f"生成推荐失败: {e}")
            return AIResponse(
                message="抱歉，我暂时无法为您推荐手机，请稍后再试。",
                confidence=0.3,
                next_action="error"
            )
    
    def _generate_comparison_response(self, memory: ConversationMemory, intent_analysis: Dict, context: str, available_phones: List[Dict]) -> AIResponse:
        """生成对比响应"""
        
        prompt = f"""
        作为专业的手机对比专家，请为用户提供详细的手机对比分析。

        用户需求: {json.dumps(intent_analysis.get('demand', {}), ensure_ascii=False, indent=2)}
        对话上下文: {context}

        请生成一个详细的对比分析报告，包括性能、拍照、续航、价格等方面的对比。
        """
        
        try:
            comparison = self._call_llm(prompt)
            return AIResponse(
                message=comparison,
                confidence=0.8,
                next_action="compare"
            )
        except Exception as e:
            print(f"生成对比失败: {e}")
            return AIResponse(
                message="抱歉，我暂时无法为您提供对比分析，请稍后再试。",
                confidence=0.3,
                next_action="error"
            )
    
    def _generate_general_response(self, memory: ConversationMemory, intent_analysis: Dict, context: str) -> AIResponse:
        """生成一般响应"""
        
        prompt = f"""
        作为专业的手机导购，请对用户的输入做出友好、专业的回应。

        用户输入: {memory.history[-1]['user'] if memory.history else ''}
        对话上下文: {context}

        请生成一个自然、友好的回应。
        """
        
        try:
            response = self._call_llm(prompt)
            return AIResponse(
                message=response,
                confidence=0.7,
                next_action="chat"
            )
        except Exception as e:
            print(f"生成一般响应失败: {e}")
            return AIResponse(
                message="您好！我是您的手机推荐助手，有什么可以帮助您的吗？",
                confidence=0.5,
                next_action="chat"
            )
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM（同步版本）"""
        try:
            # 直接使用同步方法
            response = self.llm_provider._make_api_request(prompt, "")
            
            # 检查响应是否有效
            if response and response.strip():
                return response.strip()
            else:
                print("⚠️ LLM API返回空响应，使用回退处理")
                return ""
        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            return ""
    
    def update_user_preferences(self, session_id: str, preferences: Dict):
        """更新用户偏好"""
        memory = self.get_or_create_memory(session_id)
        memory.user_preferences.update(preferences)
    
    def get_conversation_summary(self, session_id: str) -> Dict:
        """获取对话摘要"""
        memory = self.get_or_create_memory(session_id)
        return {
            'session_id': session_id,
            'message_count': len(memory.history),
            'preferences': memory.user_preferences,
            'asked_questions_count': len(memory.asked_questions),
            'last_update': memory.last_update.isoformat()
        } 