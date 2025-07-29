#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token优化器 - 解决token超出限制问题
提供多种优化策略和解决方案
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import tiktoken

@dataclass
class TokenUsage:
    """Token使用情况"""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    limit: int
    usage_ratio: float
    risk_level: str

@dataclass
class OptimizationResult:
    """优化结果"""
    original_tokens: int
    optimized_tokens: int
    reduction_ratio: float
    optimization_methods: List[str]
    warnings: List[str]

class TokenOptimizer:
    """Token优化器"""
    
    def __init__(self):
        # 使用GPT-4的编码器
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
        # Token限制配置
        self.limits = {
            'gpt-4': {
                'input_limit': 8192,
                'output_limit': 4096,
                'total_limit': 8192,
                'safe_threshold': 0.8  # 80%安全阈值
            },
            'gpt-3.5-turbo': {
                'input_limit': 4096,
                'output_limit': 4096,
                'total_limit': 4096,
                'safe_threshold': 0.8
            },
            'gemini-pro': {
                'input_limit': 30720,
                'output_limit': 2048,
                'total_limit': 30720,
                'safe_threshold': 0.8
            }
        }
    
    def analyze_token_usage(self, text: str, model: str = 'gpt-4') -> TokenUsage:
        """分析token使用情况"""
        tokens = self.encoding.encode(text)
        token_count = len(tokens)
        limit = self.limits[model]['total_limit']
        usage_ratio = token_count / limit
        
        # 确定风险等级
        if usage_ratio <= 0.5:
            risk_level = 'low'
        elif usage_ratio <= 0.8:
            risk_level = 'medium'
        elif usage_ratio <= 0.95:
            risk_level = 'high'
        else:
            risk_level = 'critical'
        
        return TokenUsage(
            input_tokens=token_count,
            output_tokens=0,
            total_tokens=token_count,
            limit=limit,
            usage_ratio=usage_ratio,
            risk_level=risk_level
        )
    
    def optimize_system_prompt(self, prompt: str, target_ratio: float = 0.3) -> OptimizationResult:
        """优化系统提示词"""
        original_tokens = len(self.encoding.encode(prompt))
        optimized_prompt = prompt
        methods_used = []
        warnings = []
        
        # 1. 移除重复内容
        if self._has_repetition(prompt):
            optimized_prompt = self._remove_repetition(optimized_prompt)
            methods_used.append("移除重复内容")
        
        # 2. 简化表达
        optimized_prompt = self._simplify_expressions(optimized_prompt)
        methods_used.append("简化表达")
        
        # 3. 移除不必要的修饰词
        optimized_prompt = self._remove_unnecessary_modifiers(optimized_prompt)
        methods_used.append("移除不必要修饰词")
        
        # 4. 如果还是太长，进行摘要
        optimized_tokens = len(self.encoding.encode(optimized_prompt))
        if optimized_tokens > original_tokens * target_ratio:
            optimized_prompt = self._summarize_prompt(optimized_prompt)
            methods_used.append("摘要压缩")
            warnings.append("提示词被大幅压缩，可能影响效果")
        
        optimized_tokens = len(self.encoding.encode(optimized_prompt))
        reduction_ratio = (original_tokens - optimized_tokens) / original_tokens
        
        return OptimizationResult(
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            reduction_ratio=reduction_ratio,
            optimization_methods=methods_used,
            warnings=warnings
        )
    
    def optimize_phone_data(self, phones: List[Dict], max_phones: int = 10) -> OptimizationResult:
        """优化手机数据"""
        original_data = json.dumps(phones, ensure_ascii=False, indent=2)
        original_tokens = len(self.encoding.encode(original_data))
        methods_used = []
        warnings = []
        
        # 1. 限制手机数量
        if len(phones) > max_phones:
            phones = phones[:max_phones]
            methods_used.append(f"限制手机数量为{max_phones}款")
            warnings.append(f"只显示前{max_phones}款手机")
        
        # 2. 只保留关键字段
        optimized_phones = []
        for phone in phones:
            optimized_phone = {
                'name': phone.get('name', ''),
                'price': phone.get('price', 0),
                'cpu': phone.get('cpu', ''),
                'ram_gb': phone.get('ram_gb', 0),
                'storage_gb': phone.get('storage_gb', 0),
                'camera_mp': phone.get('camera_mp', 0),
                'battery_mah': phone.get('battery_mah', 0),
                'rating': phone.get('rating', 0)
            }
            optimized_phones.append(optimized_phone)
        
        methods_used.append("只保留关键字段")
        
        # 3. 压缩JSON格式
        optimized_data = json.dumps(optimized_phones, ensure_ascii=False, separators=(',', ':'))
        optimized_tokens = len(self.encoding.encode(optimized_data))
        reduction_ratio = (original_tokens - optimized_tokens) / original_tokens
        
        return OptimizationResult(
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            reduction_ratio=reduction_ratio,
            optimization_methods=methods_used,
            warnings=warnings
        )
    
    def optimize_conversation_context(self, context: str, max_history: int = 3) -> OptimizationResult:
        """优化对话上下文"""
        original_tokens = len(self.encoding.encode(context))
        methods_used = []
        warnings = []
        
        # 1. 限制历史长度
        lines = context.split('\n')
        if len(lines) > max_history * 2:  # 每条对话2行
            lines = lines[-max_history * 2:]
            methods_used.append(f"限制对话历史为{max_history}轮")
            warnings.append("部分对话历史被截断")
        
        # 2. 移除空行和重复内容
        optimized_lines = []
        for line in lines:
            line = line.strip()
            if line and line not in optimized_lines:
                optimized_lines.append(line)
        
        methods_used.append("移除空行和重复内容")
        
        # 3. 简化表达
        optimized_context = '\n'.join(optimized_lines)
        optimized_context = self._simplify_expressions(optimized_context)
        methods_used.append("简化表达")
        
        optimized_tokens = len(self.encoding.encode(optimized_context))
        reduction_ratio = (original_tokens - optimized_tokens) / original_tokens
        
        return OptimizationResult(
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            reduction_ratio=reduction_ratio,
            optimization_methods=methods_used,
            warnings=warnings
        )
    
    def create_chunked_request(self, full_request: str, model: str = 'gpt-4') -> List[str]:
        """创建分块请求"""
        limit = self.limits[model]['total_limit']
        safe_limit = int(limit * 0.8)  # 80%安全阈值
        
        tokens = self.encoding.encode(full_request)
        if len(tokens) <= safe_limit:
            return [full_request]
        
        # 分割请求
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        lines = full_request.split('\n')
        for line in lines:
            line_tokens = len(self.encoding.encode(line + '\n'))
            
            if current_tokens + line_tokens > safe_limit:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
                current_tokens = line_tokens
            else:
                current_chunk += line + '\n'
                current_tokens += line_tokens
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_optimization_strategies(self) -> Dict[str, List[str]]:
        """获取优化策略"""
        return {
            'prompt_optimization': [
                "精简系统提示词，只保留核心指令",
                "移除重复和冗余内容",
                "使用更简洁的表达方式",
                "将复杂指令分解为简单指令"
            ],
            'data_optimization': [
                "限制数据量，只传递必要信息",
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
            'request_chunking': [
                "将大请求分割为多个小请求",
                "使用流式处理",
                "实现请求队列管理",
                "使用异步处理减少同步等待"
            ],
            'model_selection': [
                "根据任务复杂度选择合适的模型",
                "使用更高效的模型版本",
                "实现模型降级策略",
                "考虑使用本地模型"
            ]
        }
    
    def _has_repetition(self, text: str) -> bool:
        """检查是否有重复内容"""
        sentences = re.split(r'[。！？]', text)
        unique_sentences = set()
        for sentence in sentences:
            if sentence.strip():
                unique_sentences.add(sentence.strip())
        return len(unique_sentences) < len([s for s in sentences if s.strip()])
    
    def _remove_repetition(self, text: str) -> str:
        """移除重复内容"""
        sentences = re.split(r'[。！？]', text)
        unique_sentences = []
        for sentence in sentences:
            if sentence.strip() and sentence.strip() not in unique_sentences:
                unique_sentences.append(sentence.strip())
        return '。'.join(unique_sentences) + '。'
    
    def _simplify_expressions(self, text: str) -> str:
        """简化表达"""
        # 移除不必要的修饰词
        patterns = [
            (r'非常|特别|极其|十分', ''),
            (r'一般来说|通常情况下|一般而言', ''),
            (r'需要注意的是|值得注意的是|重要的是', ''),
            (r'请确保|请务必|请一定', '请'),
            (r'详细地|仔细地|认真地', ''),
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _remove_unnecessary_modifiers(self, text: str) -> str:
        """移除不必要的修饰词"""
        # 移除冗余的形容词和副词
        patterns = [
            (r'优秀的|出色的|卓越的', '好的'),
            (r'重要的|关键的|核心的', '重要的'),
            (r'详细的|全面的|完整的', '详细的'),
            (r'专业的|权威的|可靠的', '专业的'),
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _summarize_prompt(self, prompt: str) -> str:
        """摘要压缩提示词"""
        # 提取关键指令
        key_instructions = []
        
        # 查找任务描述
        task_patterns = [
            r'你的任务是[^。]*',
            r'你需要[^。]*',
            r'请[^。]*',
        ]
        
        for pattern in task_patterns:
            matches = re.findall(pattern, prompt)
            key_instructions.extend(matches)
        
        # 如果没有找到关键指令，使用前几句话
        if not key_instructions:
            sentences = re.split(r'[。！？]', prompt)
            key_instructions = sentences[:3]
        
        return '。'.join(key_instructions) + '。'

class TokenLimitHandler:
    """Token限制处理器"""
    
    def __init__(self):
        self.optimizer = TokenOptimizer()
        self.fallback_strategies = {
            'chunk_request': self._chunk_request_strategy,
            'reduce_context': self._reduce_context_strategy,
            'use_simpler_model': self._use_simpler_model_strategy,
            'cache_response': self._cache_response_strategy
        }
    
    def handle_token_limit(self, request_data: Dict, model: str = 'gpt-4') -> Dict:
        """处理token限制"""
        # 分析当前token使用情况
        full_request = self._build_full_request(request_data)
        usage = self.optimizer.analyze_token_usage(full_request, model)
        
        if usage.risk_level == 'low':
            return {'strategy': 'direct', 'data': request_data}
        
        # 根据风险等级选择策略
        if usage.risk_level == 'medium':
            return self._apply_optimization_strategy(request_data, usage)
        elif usage.risk_level == 'high':
            return self._apply_aggressive_strategy(request_data, usage)
        else:  # critical
            return self._apply_emergency_strategy(request_data, usage)
    
    def _build_full_request(self, request_data: Dict) -> str:
        """构建完整请求"""
        parts = []
        
        if 'system_prompt' in request_data:
            parts.append(request_data['system_prompt'])
        
        if 'context' in request_data:
            parts.append(f"上下文: {request_data['context']}")
        
        if 'user_input' in request_data:
            parts.append(f"用户: {request_data['user_input']}")
        
        if 'phone_data' in request_data:
            parts.append(f"手机数据: {json.dumps(request_data['phone_data'], ensure_ascii=False)}")
        
        return '\n\n'.join(parts)
    
    def _apply_optimization_strategy(self, request_data: Dict, usage: TokenUsage) -> Dict:
        """应用优化策略"""
        optimized_data = request_data.copy()
        
        # 优化系统提示词
        if 'system_prompt' in optimized_data:
            result = self.optimizer.optimize_system_prompt(optimized_data['system_prompt'])
            if result.reduction_ratio > 0.2:
                optimized_data['optimization_warnings'] = result.warnings
        
        # 优化手机数据
        if 'phone_data' in optimized_data:
            result = self.optimizer.optimize_phone_data(optimized_data['phone_data'])
            optimized_data['phone_data'] = result.optimized_data if hasattr(result, 'optimized_data') else optimized_data['phone_data']
        
        # 优化上下文
        if 'context' in optimized_data:
            result = self.optimizer.optimize_conversation_context(optimized_data['context'])
            optimized_data['context'] = result.optimized_context if hasattr(result, 'optimized_context') else optimized_data['context']
        
        return {
            'strategy': 'optimization',
            'data': optimized_data,
            'warnings': optimized_data.get('optimization_warnings', [])
        }
    
    def _apply_aggressive_strategy(self, request_data: Dict, usage: TokenUsage) -> Dict:
        """应用激进策略"""
        # 分块处理
        chunks = self.optimizer.create_chunked_request(
            self._build_full_request(request_data)
        )
        
        return {
            'strategy': 'chunking',
            'chunks': chunks,
            'warnings': ['请求被分割为多个部分处理']
        }
    
    def _apply_emergency_strategy(self, request_data: Dict, usage: TokenUsage) -> Dict:
        """应用紧急策略"""
        # 使用最简单的回退方案
        return {
            'strategy': 'fallback',
            'data': {
                'user_input': request_data.get('user_input', ''),
                'system_prompt': '你是手机推荐助手。请根据用户需求推荐手机。'
            },
            'warnings': ['使用简化模式，功能可能受限']
        }
    
    def _chunk_request_strategy(self, request_data: Dict) -> List[Dict]:
        """分块请求策略"""
        chunks = self.optimizer.create_chunked_request(
            self._build_full_request(request_data)
        )
        
        chunked_requests = []
        for i, chunk in enumerate(chunks):
            chunked_requests.append({
                'chunk_id': i,
                'data': {'user_input': chunk}
            })
        
        return chunked_requests
    
    def _reduce_context_strategy(self, request_data: Dict) -> Dict:
        """减少上下文策略"""
        optimized_data = request_data.copy()
        
        # 只保留最近的对话
        if 'context' in optimized_data:
            result = self.optimizer.optimize_conversation_context(
                optimized_data['context'], max_history=1
            )
            optimized_data['context'] = result.optimized_context if hasattr(result, 'optimized_context') else ''
        
        return optimized_data
    
    def _use_simpler_model_strategy(self, request_data: Dict) -> Dict:
        """使用更简单模型策略"""
        return {
            'strategy': 'model_downgrade',
            'data': request_data,
            'target_model': 'gpt-3.5-turbo'
        }
    
    def _cache_response_strategy(self, request_data: Dict) -> Dict:
        """缓存响应策略"""
        # 生成缓存键
        cache_key = hash(str(request_data.get('user_input', '')))
        
        return {
            'strategy': 'cache',
            'cache_key': cache_key,
            'data': request_data
        } 