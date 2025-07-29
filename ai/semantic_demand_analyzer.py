#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义需求分析器 - 使用LLM进行语义理解和参数提取
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from services.llm_provider import LLMProvider


@dataclass
class SemanticDemand:
    """语义需求分析结果"""
    # 核心需求
    primary_requirements: List[str] = field(default_factory=list)
    secondary_requirements: List[str] = field(default_factory=list)
    
    # 参数偏好（动态权重）
    parameter_preferences: Dict[str, float] = field(default_factory=dict)
    
    # 预算信息
    budget_info: Dict[str, Any] = field(default_factory=dict)
    
    # 品牌偏好
    brand_preferences: Dict[str, float] = field(default_factory=dict)
    
    # 使用场景
    usage_scenarios: List[str] = field(default_factory=list)
    
    # 优先级排序
    priority_order: List[str] = field(default_factory=list)
    
    # 需求完整性评分
    completeness_score: float = 0.0
    
    # 需要澄清的问题
    clarification_questions: List[str] = field(default_factory=list)
    
    # 推荐策略
    recommendation_strategy: str = "balanced"


class SemanticDemandAnalyzer:
    """语义需求分析器"""
    
    def __init__(self):
        self.llm_provider = LLMProvider()
        
        # 参数映射表
        self.parameter_mapping = {
            '性能': ['cpu_performance', 'memory_capacity', 'gpu_performance'],
            '拍照': ['camera_quality', 'camera_features'],
            '续航': ['battery_capacity', 'charging_speed'],
            '屏幕': ['screen_quality', 'screen_size'],
            '便携': ['weight_portability', 'size_portability'],
            '做工': ['build_quality', 'design_appeal'],
            '价格': ['price_value'],
            '散热': ['heat_control'],
            '网络': ['network_stability'],
            '软件': ['software_optimization'],
            '耐用': ['durability']
        }
    
    def analyze_demand(self, user_input: str, conversation_history: List[Dict] = None) -> SemanticDemand:
        """语义分析用户需求"""
        
        # 构建分析提示
        prompt = self._build_analysis_prompt(user_input, conversation_history)
        
        try:
            # 调用LLM进行语义分析
            response = self.llm_provider._make_api_request(prompt, "")
            
            if response:
                # 解析LLM响应
                demand = self._parse_llm_response(response, user_input)
                return demand
            else:
                # LLM调用失败，使用回退分析
                return self._fallback_analysis(user_input)
                
        except Exception as e:
            print(f"⚠️ 语义分析失败: {e}")
            return self._fallback_analysis(user_input)
    
    def _build_analysis_prompt(self, user_input: str, conversation_history: List[Dict] = None) -> str:
        """构建语义分析提示"""
        
        # 构建对话上下文
        context = ""
        if conversation_history:
            context = "对话历史:\n"
            for msg in conversation_history[-5:]:  # 最近5条消息
                role = "用户" if msg.get('role') == 'user' else "系统"
                context += f"{role}: {msg.get('content', '')}\n"
        
        prompt = f"""
你是一个专业的手机需求分析专家。请分析用户的需求并提取关键信息。

{context}
用户当前需求: {user_input}

请从以下维度分析用户需求:

1. 核心需求识别:
   - 主要需求: 用户最关心的功能或特性
   - 次要需求: 用户提到的其他需求
   - 隐含需求: 从用户描述中推断出的需求

2. 参数偏好分析:
   - 性能相关: CPU、内存、GPU等
   - 拍照相关: 摄像头质量、功能等
   - 续航相关: 电池容量、充电速度等
   - 屏幕相关: 屏幕质量、尺寸等
   - 便携相关: 重量、尺寸等
   - 其他: 做工、设计、价格等

3. 预算分析:
   - 明确预算: 具体价格范围
   - 隐含预算: 从需求推断的预算倾向
   - 预算偏好: 严格/灵活

4. 品牌偏好:
   - 明确偏好: 直接提到的品牌
   - 隐含偏好: 从需求推断的品牌倾向

5. 使用场景:
   - 主要用途: 游戏、拍照、商务等
   - 使用环境: 室内、户外、旅行等

6. 需求完整性评估:
   - 信息完整度: 0-1评分
   - 需要澄清的问题

请返回JSON格式的分析结果:
{{
    "primary_requirements": ["主要需求1", "主要需求2"],
    "secondary_requirements": ["次要需求1", "次要需求2"],
    "parameter_preferences": {{
        "cpu_performance": 0.8,
        "camera_quality": 0.9,
        "battery_capacity": 0.7,
        "price_value": 0.6
    }},
    "budget_info": {{
        "has_budget": true,
        "min_budget": 3000,
        "max_budget": 5000,
        "preference": "灵活"
    }},
    "brand_preferences": {{
        "Apple": 0.8,
        "Samsung": 0.6
    }},
    "usage_scenarios": ["游戏", "拍照"],
    "priority_order": ["拍照", "性能", "续航"],
    "completeness_score": 0.7,
    "clarification_questions": ["您更注重拍照质量还是拍照功能？"],
    "recommendation_strategy": "balanced"
}}

注意:
- 权重范围0-1，表示用户对该参数的重视程度
- 如果用户描述不完整，推测合理的默认值
- 根据用户语言风格和需求推断隐含偏好
- 生成有针对性的澄清问题
"""
        
        return prompt
    
    def _parse_llm_response(self, response: str, user_input: str) -> SemanticDemand:
        """解析LLM响应"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                demand = SemanticDemand()
                demand.primary_requirements = data.get('primary_requirements', [])
                demand.secondary_requirements = data.get('secondary_requirements', [])
                demand.parameter_preferences = data.get('parameter_preferences', {})
                demand.budget_info = data.get('budget_info', {})
                demand.brand_preferences = data.get('brand_preferences', {})
                demand.usage_scenarios = data.get('usage_scenarios', [])
                demand.priority_order = data.get('priority_order', [])
                demand.completeness_score = data.get('completeness_score', 0.5)
                demand.clarification_questions = data.get('clarification_questions', [])
                demand.recommendation_strategy = data.get('recommendation_strategy', 'balanced')
                
                return demand
            else:
                # 无法解析JSON，使用回退分析
                return self._fallback_analysis(user_input)
                
        except Exception as e:
            print(f"⚠️ LLM响应解析失败: {e}")
            return self._fallback_analysis(user_input)
    
    def _fallback_analysis(self, user_input: str) -> SemanticDemand:
        """回退分析 - 当LLM分析失败时使用"""
        demand = SemanticDemand()
        
        # 简单的关键词分析
        input_lower = user_input.lower()
        
        # 基础需求识别
        if '拍照' in input_lower or '摄影' in input_lower:
            demand.primary_requirements.append('拍照')
            demand.parameter_preferences['camera_quality'] = 0.8
            demand.parameter_preferences['camera_features'] = 0.7
        
        if '游戏' in input_lower or '性能' in input_lower:
            demand.primary_requirements.append('性能')
            demand.parameter_preferences['cpu_performance'] = 0.8
            demand.parameter_preferences['gpu_performance'] = 0.7
        
        if '续航' in input_lower or '电池' in input_lower:
            demand.primary_requirements.append('续航')
            demand.parameter_preferences['battery_capacity'] = 0.8
        
        if '轻薄' in input_lower or '便携' in input_lower:
            demand.primary_requirements.append('便携')
            demand.parameter_preferences['weight_portability'] = 0.8
            demand.parameter_preferences['size_portability'] = 0.7
        
        # 预算分析
        budget_match = re.search(r'(\d+)[k千]-(\d+)[k千]', user_input)
        if budget_match:
            min_budget = int(budget_match.group(1)) * 1000
            max_budget = int(budget_match.group(2)) * 1000
            demand.budget_info = {
                'has_budget': True,
                'min_budget': min_budget,
                'max_budget': max_budget,
                'preference': '灵活'
            }
        
        # 默认完整性评分
        demand.completeness_score = 0.6
        
        return demand
    
    def generate_clarification_questions(self, demand: SemanticDemand) -> List[str]:
        """生成澄清问题"""
        questions = []
        
        # 如果需求不完整，生成澄清问题
        if demand.completeness_score < 0.7:
            if not demand.primary_requirements:
                questions.append("您最关心手机的哪个方面？比如拍照、性能、续航等")
            
            if not demand.budget_info.get('has_budget'):
                questions.append("您大概的预算范围是多少？")
            
            if not demand.usage_scenarios:
                questions.append("您主要用手机做什么？比如游戏、拍照、工作等")
        
        # 基于当前需求生成细化问题
        if '拍照' in demand.primary_requirements:
            questions.append("您更注重拍照质量还是拍照功能？比如夜景、人像、广角等")
        
        if '性能' in demand.primary_requirements:
            questions.append("您主要玩什么类型的游戏？或者有其他性能要求吗？")
        
        if '续航' in demand.primary_requirements:
            questions.append("您一天大概用多长时间手机？需要快充吗？")
        
        return questions
    
    def update_demand_with_clarification(self, original_demand: SemanticDemand, 
                                       clarification_response: str) -> SemanticDemand:
        """根据澄清回答更新需求"""
        
        # 构建更新提示
        prompt = f"""
基于用户的澄清回答，更新需求分析。

原始需求分析:
{json.dumps(original_demand.__dict__, ensure_ascii=False, indent=2)}

用户澄清回答: {clarification_response}

请更新需求分析，返回更新后的JSON格式结果。
"""
        
        try:
            response = self.llm_provider._make_api_request(prompt, "")
            if response:
                # 解析更新后的需求
                updated_demand = self._parse_llm_response(response, clarification_response)
                return updated_demand
            else:
                return original_demand
        except Exception as e:
            print(f"⚠️ 需求更新失败: {e}")
            return original_demand 