#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token限制分析工具
分析当前系统的token使用情况和风险
"""

import json
import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import tiktoken

@dataclass
class TokenAnalysis:
    """Token分析结果"""
    total_tokens: int
    input_tokens: int
    output_tokens: int
    risk_level: str  # low, medium, high, critical
    risk_factors: List[str]
    recommendations: List[str]
    cost_estimate: float  # 估算成本（美元）

class TokenLimitAnalyzer:
    """Token限制分析器"""
    
    def __init__(self):
        # 使用GPT-4的编码器
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
        # Token限制配置
        self.limits = {
            'gpt-4': {
                'input_limit': 8192,
                'output_limit': 4096,
                'total_limit': 8192,
                'cost_per_1k_input': 0.03,
                'cost_per_1k_output': 0.06
            },
            'gpt-3.5-turbo': {
                'input_limit': 4096,
                'output_limit': 4096,
                'total_limit': 4096,
                'cost_per_1k_input': 0.0015,
                'cost_per_1k_output': 0.002
            }
        }
        
        # 风险阈值
        self.risk_thresholds = {
            'low': 0.3,      # 30%以下
            'medium': 0.6,   # 60%以下
            'high': 0.8,     # 80%以下
            'critical': 1.0  # 100%及以上
        }
    
    def analyze_system_prompt(self, system_prompt: str, model: str = 'gpt-4') -> TokenAnalysis:
        """分析系统提示的token使用情况"""
        tokens = self.encoding.encode(system_prompt)
        token_count = len(tokens)
        
        limit = self.limits[model]['input_limit']
        usage_ratio = token_count / limit
        
        risk_level = self._calculate_risk_level(usage_ratio)
        risk_factors = self._identify_risk_factors(system_prompt, token_count, limit)
        recommendations = self._generate_recommendations(system_prompt, token_count, limit)
        cost_estimate = self._estimate_cost(token_count, 0, model)
        
        return TokenAnalysis(
            total_tokens=token_count,
            input_tokens=token_count,
            output_tokens=0,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations,
            cost_estimate=cost_estimate
        )
    
    def analyze_user_input(self, user_input: str, context: str = "", model: str = 'gpt-4') -> TokenAnalysis:
        """分析用户输入的token使用情况"""
        full_input = f"Context: {context}\nUser: {user_input}" if context else user_input
        tokens = self.encoding.encode(full_input)
        token_count = len(tokens)
        
        limit = self.limits[model]['input_limit']
        usage_ratio = token_count / limit
        
        risk_level = self._calculate_risk_level(usage_ratio)
        risk_factors = self._identify_risk_factors(full_input, token_count, limit)
        recommendations = self._generate_recommendations(full_input, token_count, limit)
        cost_estimate = self._estimate_cost(token_count, 0, model)
        
        return TokenAnalysis(
            total_tokens=token_count,
            input_tokens=token_count,
            output_tokens=0,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations,
            cost_estimate=cost_estimate
        )
    
    def analyze_phone_data(self, phones: List[Dict], model: str = 'gpt-4') -> TokenAnalysis:
        """分析手机数据的token使用情况"""
        # 将手机数据转换为JSON字符串
        phone_data_str = json.dumps(phones, ensure_ascii=False, indent=2)
        tokens = self.encoding.encode(phone_data_str)
        token_count = len(tokens)
        
        limit = self.limits[model]['input_limit']
        usage_ratio = token_count / limit
        
        risk_level = self._calculate_risk_level(usage_ratio)
        risk_factors = self._identify_data_risk_factors(phones, token_count, limit)
        recommendations = self._generate_data_recommendations(phones, token_count, limit)
        cost_estimate = self._estimate_cost(token_count, 0, model)
        
        return TokenAnalysis(
            total_tokens=token_count,
            input_tokens=token_count,
            output_tokens=0,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations,
            cost_estimate=cost_estimate
        )
    
    def analyze_complete_request(self, system_prompt: str, user_input: str, 
                               context: str = "", phones: List[Dict] = None, 
                               model: str = 'gpt-4') -> TokenAnalysis:
        """分析完整请求的token使用情况"""
        # 组合所有输入
        full_input = system_prompt
        
        if context:
            full_input += f"\n\nContext: {context}"
        
        if phones:
            phone_data_str = json.dumps(phones, ensure_ascii=False, indent=2)
            full_input += f"\n\nPhone Data: {phone_data_str}"
        
        full_input += f"\n\nUser: {user_input}"
        
        tokens = self.encoding.encode(full_input)
        token_count = len(tokens)
        
        limit = self.limits[model]['total_limit']
        usage_ratio = token_count / limit
        
        risk_level = self._calculate_risk_level(usage_ratio)
        risk_factors = self._identify_complete_risk_factors(
            system_prompt, user_input, context, phones, token_count, limit
        )
        recommendations = self._generate_complete_recommendations(
            system_prompt, user_input, context, phones, token_count, limit
        )
        cost_estimate = self._estimate_cost(token_count, 0, model)
        
        return TokenAnalysis(
            total_tokens=token_count,
            input_tokens=token_count,
            output_tokens=0,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations,
            cost_estimate=cost_estimate
        )
    
    def _calculate_risk_level(self, usage_ratio: float) -> str:
        """计算风险等级"""
        if usage_ratio <= self.risk_thresholds['low']:
            return 'low'
        elif usage_ratio <= self.risk_thresholds['medium']:
            return 'medium'
        elif usage_ratio <= self.risk_thresholds['high']:
            return 'high'
        else:
            return 'critical'
    
    def _identify_risk_factors(self, text: str, token_count: int, limit: int) -> List[str]:
        """识别风险因素"""
        risk_factors = []
        
        if token_count > limit * 0.8:
            risk_factors.append("接近token限制")
        
        # 检查长文本
        if len(text) > 10000:
            risk_factors.append("文本过长")
        
        # 检查重复内容
        words = text.split()
        if len(set(words)) / len(words) < 0.3:
            risk_factors.append("内容重复度高")
        
        # 检查特殊字符
        special_chars = re.findall(r'[^\w\s]', text)
        if len(special_chars) > len(text) * 0.1:
            risk_factors.append("特殊字符过多")
        
        return risk_factors
    
    def _identify_data_risk_factors(self, phones: List[Dict], token_count: int, limit: int) -> List[str]:
        """识别数据风险因素"""
        risk_factors = []
        
        if token_count > limit * 0.8:
            risk_factors.append("手机数据量过大")
        
        if len(phones) > 50:
            risk_factors.append("手机数量过多")
        
        # 检查数据字段
        if phones:
            sample_phone = phones[0]
            field_count = len(sample_phone)
            if field_count > 20:
                risk_factors.append("手机字段过多")
        
        return risk_factors
    
    def _identify_complete_risk_factors(self, system_prompt: str, user_input: str, 
                                      context: str, phones: List[Dict], 
                                      token_count: int, limit: int) -> List[str]:
        """识别完整请求的风险因素"""
        risk_factors = []
        
        if token_count > limit * 0.8:
            risk_factors.append("总token使用量接近限制")
        
        # 分析各部分占比
        system_tokens = len(self.encoding.encode(system_prompt))
        user_tokens = len(self.encoding.encode(user_input))
        context_tokens = len(self.encoding.encode(context)) if context else 0
        phone_tokens = len(self.encoding.encode(json.dumps(phones, ensure_ascii=False))) if phones else 0
        
        if system_tokens / token_count > 0.5:
            risk_factors.append("系统提示占比过高")
        
        if phone_tokens / token_count > 0.6:
            risk_factors.append("手机数据占比过高")
        
        return risk_factors
    
    def _generate_recommendations(self, text: str, token_count: int, limit: int) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if token_count > limit * 0.8:
            recommendations.append("考虑缩短文本长度")
            recommendations.append("移除不必要的重复内容")
            recommendations.append("使用更简洁的表达")
        
        if len(text) > 10000:
            recommendations.append("将长文本分段处理")
            recommendations.append("提取关键信息")
        
        return recommendations
    
    def _generate_data_recommendations(self, phones: List[Dict], token_count: int, limit: int) -> List[str]:
        """生成数据优化建议"""
        recommendations = []
        
        if token_count > limit * 0.8:
            recommendations.append("减少手机数据量")
            recommendations.append("只保留必要字段")
            recommendations.append("使用数据压缩")
        
        if len(phones) > 50:
            recommendations.append("限制手机数量")
            recommendations.append("使用分页处理")
        
        return recommendations
    
    def _generate_complete_recommendations(self, system_prompt: str, user_input: str, 
                                         context: str, phones: List[Dict], 
                                         token_count: int, limit: int) -> List[str]:
        """生成完整请求的优化建议"""
        recommendations = []
        
        if token_count > limit * 0.8:
            recommendations.append("优化系统提示，减少冗余")
            recommendations.append("限制手机数据量")
            recommendations.append("简化上下文信息")
            recommendations.append("使用更高效的模型")
        
        # 具体建议
        system_tokens = len(self.encoding.encode(system_prompt))
        if system_tokens > limit * 0.3:
            recommendations.append("精简系统提示，保留核心指令")
        
        if phones and len(self.encoding.encode(json.dumps(phones, ensure_ascii=False))) > limit * 0.5:
            recommendations.append("只传递必要的手机信息")
            recommendations.append("使用预过滤减少数据量")
        
        return recommendations
    
    def _estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """估算成本"""
        model_config = self.limits[model]
        input_cost = (input_tokens / 1000) * model_config['cost_per_1k_input']
        output_cost = (output_tokens / 1000) * model_config['cost_per_1k_output']
        return input_cost + output_cost
    
    def get_optimization_strategies(self) -> Dict[str, List[str]]:
        """获取优化策略"""
        return {
            'system_prompt': [
                "精简系统提示，只保留核心指令",
                "移除重复和冗余内容",
                "使用更简洁的表达方式",
                "将复杂指令分解为简单指令"
            ],
            'data_management': [
                "实现数据预过滤，只传递相关数据",
                "使用数据压缩和摘要",
                "分页处理大量数据",
                "缓存常用数据减少重复传输"
            ],
            'context_optimization': [
                "限制上下文长度",
                "只保留最近的对话历史",
                "使用对话摘要替代完整历史",
                "实现智能上下文管理"
            ],
            'model_selection': [
                "根据任务复杂度选择合适的模型",
                "使用更高效的模型版本",
                "实现模型降级策略",
                "考虑使用本地模型"
            ],
            'architecture': [
                "实现分层处理架构",
                "使用微服务减少单次请求复杂度",
                "实现请求分片和合并",
                "使用异步处理减少同步等待"
            ]
        } 