#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求Schema抽象层 - 使用大模型和embedding模型进行智能匹配
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

from services.llm_provider import LLMProvider


class DemandCategory(Enum):
    """需求类别枚举"""
    PERFORMANCE = "performance"      # 性能相关
    CAMERA = "camera"               # 拍照相关
    BATTERY = "battery"             # 续航相关
    SCREEN = "screen"               # 屏幕相关
    PORTABILITY = "portability"     # 便携相关
    BUILD_QUALITY = "build_quality" # 做工相关
    PRICE = "price"                 # 价格相关
    BRAND = "brand"                 # 品牌相关
    USAGE_SCENARIO = "usage_scenario" # 使用场景
    FEATURE = "feature"             # 功能特性


class DemandPriority(Enum):
    """需求优先级枚举"""
    CRITICAL = "critical"    # 关键需求
    IMPORTANT = "important"  # 重要需求
    NORMAL = "normal"        # 一般需求
    OPTIONAL = "optional"    # 可选需求


@dataclass
class DemandSegment:
    """需求片段 - 最小可匹配单元"""
    category: DemandCategory
    priority: DemandPriority
    keywords: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'category': self.category.value,
            'priority': self.priority.value,
            'keywords': self.keywords,
            'synonyms': self.synonyms,
            'constraints': self.constraints,
            'weight': self.weight,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DemandSegment':
        """从字典创建需求片段"""
        return cls(
            category=DemandCategory(data['category']),
            priority=DemandPriority(data['priority']),
            keywords=data.get('keywords', []),
            synonyms=data.get('synonyms', []),
            constraints=data.get('constraints', {}),
            weight=data.get('weight', 1.0),
            description=data.get('description', '')
        )


@dataclass
class DemandSchema:
    """需求Schema - 完整的用户需求结构"""
    segments: List[DemandSegment] = field(default_factory=list)
    budget_range: Optional[Tuple[float, float]] = None
    brand_preferences: Dict[str, float] = field(default_factory=dict)
    usage_scenarios: List[str] = field(default_factory=list)
    completeness_score: float = 0.0
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_segment(self, segment: DemandSegment):
        """添加需求片段"""
        self.segments.append(segment)
    
    def get_segments_by_category(self, category: DemandCategory) -> List[DemandSegment]:
        """按类别获取需求片段"""
        return [seg for seg in self.segments if seg.category == category]
    
    def get_critical_segments(self) -> List[DemandSegment]:
        """获取关键需求片段"""
        return [seg for seg in self.segments if seg.priority == DemandPriority.CRITICAL]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'segments': [seg.to_dict() for seg in self.segments],
            'budget_range': self.budget_range,
            'brand_preferences': self.brand_preferences,
            'usage_scenarios': self.usage_scenarios,
            'completeness_score': self.completeness_score,
            'confidence_score': self.confidence_score,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DemandSchema':
        """从字典创建需求Schema"""
        segments = [DemandSegment.from_dict(seg_data) for seg_data in data.get('segments', [])]
        budget_range = tuple(data['budget_range']) if data.get('budget_range') else None
        
        return cls(
            segments=segments,
            budget_range=budget_range,
            brand_preferences=data.get('brand_preferences', {}),
            usage_scenarios=data.get('usage_scenarios', []),
            completeness_score=data.get('completeness_score', 0.0),
            confidence_score=data.get('confidence_score', 0.0),
            metadata=data.get('metadata', {})
        )


class DemandSchemaRegistry:
    """需求Schema注册表 - 管理所有预定义的需求片段"""
    
    def __init__(self):
        self.segments: Dict[str, DemandSegment] = {}
        self._initialize_default_segments()
    
    def _initialize_default_segments(self):
        """初始化默认需求片段"""
        
        # 性能相关片段
        self.register_segment(DemandSegment(
            category=DemandCategory.PERFORMANCE,
            priority=DemandPriority.IMPORTANT,
            keywords=['性能', '速度', '流畅', '快'],
            synonyms=['游戏性能', '处理器', 'CPU', 'GPU', '内存'],
            constraints={'min_cpu_score': 0.7},
            weight=0.8,
            description="对手机性能有较高要求"
        ))
        
        self.register_segment(DemandSegment(
            category=DemandCategory.PERFORMANCE,
            priority=DemandPriority.CRITICAL,
            keywords=['游戏', '电竞', '王者荣耀', '吃鸡'],
            synonyms=['手游', '游戏手机', '高性能'],
            constraints={'min_cpu_score': 0.8, 'min_ram': 8},
            weight=0.9,
            description="专门用于游戏的高性能需求"
        ))
        
        # 拍照相关片段
        self.register_segment(DemandSegment(
            category=DemandCategory.CAMERA,
            priority=DemandPriority.IMPORTANT,
            keywords=['拍照', '摄影', '相机'],
            synonyms=['摄像头', '像素', '画质', '夜景'],
            constraints={'min_camera_mp': 48},
            weight=0.8,
            description="对拍照功能有要求"
        ))
        
        self.register_segment(DemandSegment(
            category=DemandCategory.CAMERA,
            priority=DemandPriority.CRITICAL,
            keywords=['专业摄影', '摄影爱好者', '拍照好'],
            synonyms=['人像', '广角', '长焦', '夜景模式'],
            constraints={'min_camera_mp': 50, 'camera_features': ['夜景', '人像']},
            weight=0.95,
            description="专业摄影需求"
        ))
        
        # 续航相关片段
        self.register_segment(DemandSegment(
            category=DemandCategory.BATTERY,
            priority=DemandPriority.IMPORTANT,
            keywords=['续航', '电池', '持久'],
            synonyms=['充电', '快充', '无线充电'],
            constraints={'min_battery_mah': 4000},
            weight=0.8,
            description="对续航能力有要求"
        ))
        
        self.register_segment(DemandSegment(
            category=DemandCategory.BATTERY,
            priority=DemandPriority.CRITICAL,
            keywords=['续航久', '电池大', '一天不用充电'],
            synonyms=['超长续航', '大电池'],
            constraints={'min_battery_mah': 5000},
            weight=0.9,
            description="对续航有极高要求"
        ))
        
        # 便携相关片段
        self.register_segment(DemandSegment(
            category=DemandCategory.PORTABILITY,
            priority=DemandPriority.IMPORTANT,
            keywords=['轻薄', '便携', '轻便'],
            synonyms=['重量', '尺寸', '厚度'],
            constraints={'max_weight_g': 180, 'max_screen_size': 6.5},
            weight=0.8,
            description="对便携性有要求"
        ))
        
        # 价格相关片段
        self.register_segment(DemandSegment(
            category=DemandCategory.PRICE,
            priority=DemandPriority.CRITICAL,
            keywords=['性价比', '便宜', '实惠'],
            synonyms=['价格', '预算', '经济'],
            constraints={'max_price': 3000},
            weight=0.9,
            description="对价格敏感"
        ))
        
        # 品牌相关片段
        self.register_segment(DemandSegment(
            category=DemandCategory.BRAND,
            priority=DemandPriority.IMPORTANT,
            keywords=['苹果', 'iPhone', 'Apple'],
            synonyms=['iOS', '苹果生态'],
            constraints={'brand': 'Apple'},
            weight=0.8,
            description="偏好苹果品牌"
        ))
        
        self.register_segment(DemandSegment(
            category=DemandCategory.BRAND,
            priority=DemandPriority.IMPORTANT,
            keywords=['华为', 'Huawei'],
            synonyms=['鸿蒙', '麒麟'],
            constraints={'brand': 'Huawei'},
            weight=0.8,
            description="偏好华为品牌"
        ))
        
        # 使用场景片段
        self.register_segment(DemandSegment(
            category=DemandCategory.USAGE_SCENARIO,
            priority=DemandPriority.IMPORTANT,
            keywords=['商务', '办公', '工作'],
            synonyms=['会议', '邮件', '文档'],
            constraints={'features': ['商务', '办公']},
            weight=0.8,
            description="商务办公使用场景"
        ))
        
        self.register_segment(DemandSegment(
            category=DemandCategory.USAGE_SCENARIO,
            priority=DemandPriority.IMPORTANT,
            keywords=['日常', '生活', '普通'],
            synonyms=['刷视频', '聊天', '购物'],
            constraints={},
            weight=0.6,
            description="日常使用场景"
        ))
    
    def register_segment(self, segment: DemandSegment):
        """注册需求片段"""
        segment_id = f"{segment.category.value}_{segment.priority.value}_{len(self.segments)}"
        self.segments[segment_id] = segment
    
    def get_all_segments(self) -> List[DemandSegment]:
        """获取所有需求片段"""
        return list(self.segments.values())
    
    def get_segments_by_category(self, category: DemandCategory) -> List[DemandSegment]:
        """按类别获取需求片段"""
        return [seg for seg in self.segments.values() if seg.category == category]


class VectorMatcher:
    """向量匹配器 - 集成embedding模型"""
    
    def __init__(self):
        self.embedding_model = None
        self.segment_embeddings = {}
        self.llm_provider = LLMProvider()
    
    def load_embedding_model(self, model_path: str):
        """加载embedding模型"""
        # TODO: 实现embedding模型加载
        print(f"🔄 加载embedding模型: {model_path}")
        pass
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的向量表示"""
        # TODO: 实现向量化
        # 临时返回随机向量
        import random
        return [random.random() for _ in range(384)]
    
    def compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算向量相似度"""
        import numpy as np
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def match_demands(self, user_input: str, segments: List[DemandSegment]) -> List[Tuple[DemandSegment, float]]:
        """使用大模型进行语义匹配"""
        # 构建匹配提示
        prompt = self._build_matching_prompt(user_input, segments)
        
        try:
            response = self.llm_provider._make_api_request(prompt, "")
            if response:
                return self._parse_matching_response(response, segments)
            else:
                return self._fallback_matching(user_input, segments)
        except Exception as e:
            print(f"⚠️ 语义匹配失败: {e}")
            return self._fallback_matching(user_input, segments)
    
    def _build_matching_prompt(self, user_input: str, segments: List[DemandSegment]) -> str:
        """构建匹配提示"""
        
        # 构建需求片段信息
        segments_info = []
        for i, segment in enumerate(segments):
            segment_info = f"{i+1}. 类别: {segment.category.value}, 优先级: {segment.priority.value}\n"
            segment_info += f"   关键词: {', '.join(segment.keywords)}\n"
            segment_info += f"   同义词: {', '.join(segment.synonyms)}\n"
            segment_info += f"   描述: {segment.description}\n"
            segments_info.append(segment_info)
        
        prompt = f"""
你是一个专业的手机需求分析专家。请分析用户输入与预定义需求片段的匹配程度。

用户输入: {user_input}

可匹配的需求片段:
{chr(10).join(segments_info)}

请分析用户输入与每个需求片段的匹配程度，返回JSON格式结果:
{{
    "matches": [
        {{
            "segment_index": 数字(对应上面的编号),
            "match_score": 0.0-1.0,
            "match_reason": "匹配原因"
        }}
    ]
}}

匹配规则:
1. 考虑语义相似性，不仅仅是关键词匹配
2. 理解用户表达的真实意图
3. 考虑上下文和隐含需求
4. 匹配分数0.0-1.0，表示匹配程度

只返回JSON，不要其他内容。
"""
        
        return prompt
    
    def _parse_matching_response(self, response: str, segments: List[DemandSegment]) -> List[Tuple[DemandSegment, float]]:
        """解析匹配响应"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                results = []
                
                for match in data.get('matches', []):
                    segment_index = match['segment_index'] - 1
                    if 0 <= segment_index < len(segments):
                        results.append((segments[segment_index], match['match_score']))
                
                results.sort(key=lambda x: x[1], reverse=True)
                return results
            else:
                return self._fallback_matching("", segments)
                
        except Exception as e:
            print(f"⚠️ 匹配响应解析失败: {e}")
            return self._fallback_matching("", segments)
    
    def _fallback_matching(self, user_input: str, segments: List[DemandSegment]) -> List[Tuple[DemandSegment, float]]:
        """回退匹配"""
        results = []
        user_input_lower = user_input.lower()
        
        for segment in segments:
            score = 0.0
            
            # 关键词匹配
            for keyword in segment.keywords:
                if keyword.lower() in user_input_lower:
                    score += 0.3
            
            # 同义词匹配
            for synonym in segment.synonyms:
                if synonym.lower() in user_input_lower:
                    score += 0.2
            
            if score > 0:
                results.append((segment, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results


class DemandSchemaMatcher:
    """需求Schema匹配器 - 使用大模型进行智能匹配"""
    
    def __init__(self):
        self.registry = DemandSchemaRegistry()
        self.vector_matcher = VectorMatcher()
        self.llm_provider = LLMProvider()
    
    def parse_user_demand(self, user_input: str, conversation_history: List[Dict] = None) -> DemandSchema:
        """解析用户需求为Schema"""
        schema = DemandSchema()
        
        # 1. 使用大模型进行语义匹配
        all_segments = self.registry.get_all_segments()
        matched_segments = self.vector_matcher.match_demands(user_input, all_segments)
        
        # 2. 添加匹配的片段
        for segment, score in matched_segments:
            if score > 0.2:  # 匹配阈值
                schema.add_segment(segment)
        
        # 3. 使用大模型提取预算信息
        budget_info = self._extract_budget_info_llm(user_input)
        if budget_info:
            schema.budget_range = budget_info
        
        # 4. 使用大模型提取品牌偏好
        brand_prefs = self._extract_brand_preferences_llm(user_input)
        schema.brand_preferences.update(brand_prefs)
        
        # 5. 使用大模型提取使用场景
        usage_scenarios = self._extract_usage_scenarios_llm(user_input)
        schema.usage_scenarios.extend(usage_scenarios)
        
        # 6. 计算完整性评分
        schema.completeness_score = self._calculate_completeness(schema)
        
        # 7. 计算置信度
        schema.confidence_score = self._calculate_confidence(matched_segments)
        
        return schema
    
    def _extract_budget_info_llm(self, user_input: str) -> Optional[Tuple[float, float]]:
        """使用大模型提取预算信息"""
        prompt = f"""
请从用户输入中提取预算信息。

用户输入: {user_input}

请分析用户提到的预算信息，返回JSON格式:
{{
    "has_budget": true/false,
    "min_budget": 数字(最低预算，单位元),
    "max_budget": 数字(最高预算，单位元),
    "confidence": 0.0-1.0
}}

注意:
1. 理解各种表达方式，如"3000左右"、"不超过5000"、"5000以上"等
2. 如果没有明确预算信息，返回has_budget: false
3. 预算单位统一为元
4. confidence表示提取的置信度

只返回JSON，不要其他内容。
"""
        
        try:
            response = self.llm_provider._make_api_request(prompt, "")
            if response:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    if data.get('has_budget', False):
                        min_budget = data.get('min_budget', 0)
                        max_budget = data.get('max_budget', float('inf'))
                        return (min_budget, max_budget)
        except Exception as e:
            print(f"⚠️ 预算信息提取失败: {e}")
        
        return None
    
    def _extract_brand_preferences_llm(self, user_input: str) -> Dict[str, float]:
        """使用大模型提取品牌偏好"""
        prompt = f"""
请从用户输入中提取品牌偏好信息。

用户输入: {user_input}

请分析用户提到的品牌偏好，返回JSON格式:
{{
    "brand_preferences": {{
        "Apple": 0.0-1.0,
        "Huawei": 0.0-1.0,
        "Xiaomi": 0.0-1.0,
        "Samsung": 0.0-1.0,
        "OPPO": 0.0-1.0,
        "vivo": 0.0-1.0
    }}
}}

注意:
1. 0.0表示强烈不喜欢，1.0表示强烈喜欢
2. 0.5表示中性态度
3. 理解各种表达方式，如"喜欢苹果"、"不要小米"、"华为不错"等
4. 只返回用户明确提到的品牌

只返回JSON，不要其他内容。
"""
        
        try:
            response = self.llm_provider._make_api_request(prompt, "")
            if response:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return data.get('brand_preferences', {})
        except Exception as e:
            print(f"⚠️ 品牌偏好提取失败: {e}")
        
        return {}
    
    def _extract_usage_scenarios_llm(self, user_input: str) -> List[str]:
        """使用大模型提取使用场景"""
        prompt = f"""
请从用户输入中提取使用场景信息。

用户输入: {user_input}

请分析用户提到的使用场景，返回JSON格式:
{{
    "usage_scenarios": ["场景1", "场景2"]
}}

常见使用场景:
- 游戏: 手游、电竞、娱乐游戏
- 拍照: 摄影、自拍、记录生活
- 商务: 办公、会议、邮件处理
- 日常: 刷视频、聊天、购物
- 学习: 网课、阅读、笔记
- 旅行: 导航、拍照、记录

只返回JSON，不要其他内容。
"""
        
        try:
            response = self.llm_provider._make_api_request(prompt, "")
            if response:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return data.get('usage_scenarios', [])
        except Exception as e:
            print(f"⚠️ 使用场景提取失败: {e}")
        
        return []
    
    def _calculate_completeness(self, schema: DemandSchema) -> float:
        """计算需求完整性评分"""
        score = 0.0
        
        # 基础分数
        if schema.segments:
            score += 0.3
        
        # 预算信息
        if schema.budget_range:
            score += 0.3
        
        # 品牌偏好
        if schema.brand_preferences:
            score += 0.2
        
        # 使用场景
        if schema.usage_scenarios:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_confidence(self, matched_segments: List[Tuple[DemandSegment, float]]) -> float:
        """计算匹配置信度"""
        if not matched_segments:
            return 0.0
        
        # 基于匹配分数和数量计算置信度
        total_score = sum(score for _, score in matched_segments)
        avg_score = total_score / len(matched_segments)
        
        return min(avg_score, 1.0)
    
    def generate_clarification_questions_llm(self, schema: DemandSchema, user_input: str) -> List[str]:
        """使用大模型生成澄清问题"""
        prompt = f"""
你是一个专业的手机推荐顾问。请根据用户的需求分析，生成有针对性的澄清问题。

用户输入: {user_input}

需求分析:
- 已识别需求: {[seg.description for seg in schema.segments]}
- 预算范围: {schema.budget_range}
- 品牌偏好: {schema.brand_preferences}
- 使用场景: {schema.usage_scenarios}
- 完整性评分: {schema.completeness_score}

请生成3-5个澄清问题，帮助用户完善需求。返回JSON格式:
{{
    "questions": [
        {{
            "question": "问题内容",
            "purpose": "问题目的",
            "priority": "high/medium/low"
        }}
    ]
}}

问题生成原则:
1. 针对缺失的关键信息
2. 细化已识别的需求
3. 考虑用户的使用场景
4. 语言自然友好
5. 避免重复已有信息

只返回JSON，不要其他内容。
"""
        
        try:
            response = self.llm_provider._make_api_request(prompt, "")
            if response:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    questions = []
                    for q in data.get('questions', []):
                        questions.append(q['question'])
                    return questions
        except Exception as e:
            print(f"⚠️ 澄清问题生成失败: {e}")
        
        # 回退到简单问题
        return self._generate_fallback_questions(schema)
    
    def _generate_fallback_questions(self, schema: DemandSchema) -> List[str]:
        """生成回退澄清问题"""
        questions = []
        
        if schema.completeness_score < 0.7:
            if not schema.segments:
                questions.append("您最关心手机的哪个方面？比如拍照、性能、续航等")
            
            if not schema.budget_range:
                questions.append("您大概的预算范围是多少？")
            
            if not schema.brand_preferences:
                questions.append("您有品牌偏好吗？比如苹果、华为、小米等")
        
        return questions 