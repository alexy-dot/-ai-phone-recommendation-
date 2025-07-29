#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Schema的推荐引擎 - 使用大模型进行智能推荐
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from ai.demand_schema import DemandSchema, DemandSchemaMatcher, DemandCategory
from services.llm_provider import LLMProvider
from database.sample_data import PhoneSpec


@dataclass
class SchemaRecommendationResult:
    """Schema推荐结果"""
    recommendations: List[Dict[str, Any]]
    demand_schema: DemandSchema
    clarification_questions: List[str]
    recommendation_strategy: str
    confidence_score: float
    match_details: List[Dict[str, Any]]
    next_steps: List[str]


class SchemaBasedRecommendationEngine:
    """基于Schema的推荐引擎"""
    
    def __init__(self):
        self.schema_matcher = DemandSchemaMatcher()
        self.llm_provider = LLMProvider()
        
        # 推荐策略配置
        self.strategies = {
            'schema_precise': {'name': 'Schema精确推荐', 'description': '基于完整Schema的精确匹配'},
            'schema_smart': {'name': 'Schema智能推荐', 'description': '基于部分Schema的智能推测'},
            'schema_guided': {'name': 'Schema引导推荐', 'description': '基于Schema的引导式推荐'},
            'fallback': {'name': '回退推荐', 'description': '当Schema匹配失败时的回退方案'}
        }
    
    def recommend(self, phones: List[PhoneSpec], user_input: str, 
                 conversation_history: List[Dict] = None, top_n: int = 5) -> SchemaRecommendationResult:
        """基于Schema的智能推荐"""
        
        print("🧠 开始基于Schema的智能推荐...")
        
        # 1. 解析用户需求为Schema
        print("📝 解析用户需求为Schema...")
        demand_schema = self.schema_matcher.parse_user_demand(user_input, conversation_history)
        
        print(f"   识别需求片段: {len(demand_schema.segments)} 个")
        print(f"   Schema完整性: {demand_schema.completeness_score:.2f}")
        print(f"   匹配置信度: {demand_schema.confidence_score:.2f}")
        
        # 2. 生成澄清问题
        clarification_questions = self.schema_matcher.generate_clarification_questions_llm(
            demand_schema, user_input
        )
        
        # 3. 基于Schema完整性选择推荐策略
        if demand_schema.completeness_score >= 0.8 and demand_schema.confidence_score >= 0.7:
            # Schema完整且置信度高，进行精确推荐
            print("✅ Schema完整，进行精确推荐...")
            recommendations, strategy = self._schema_precise_recommendation(phones, demand_schema, top_n)
            confidence_score = 0.9
        elif demand_schema.completeness_score >= 0.6:
            # Schema基本完整，进行智能推测推荐
            print("🤔 Schema基本完整，智能推测推荐...")
            recommendations, strategy = self._schema_smart_recommendation(phones, demand_schema, top_n)
            confidence_score = 0.7
        else:
            # Schema不完整，进行引导式推荐
            print("💡 Schema不完整，引导式推荐...")
            recommendations, strategy = self._schema_guided_recommendation(phones, demand_schema, top_n)
            confidence_score = 0.5
        
        # 4. 生成匹配详情
        match_details = self._generate_match_details(recommendations, demand_schema)
        
        # 5. 确定下一步行动
        next_steps = self._determine_next_steps(demand_schema, clarification_questions)
        
        result = SchemaRecommendationResult(
            recommendations=recommendations,
            demand_schema=demand_schema,
            clarification_questions=clarification_questions,
            recommendation_strategy=strategy,
            confidence_score=confidence_score,
            match_details=match_details,
            next_steps=next_steps
        )
        
        print(f"✅ Schema推荐完成！策略: {strategy}, 置信度: {confidence_score:.2f}")
        return result
    
    def _schema_precise_recommendation(self, phones: List[PhoneSpec], schema: DemandSchema, top_n: int) -> Tuple[List[Dict[str, Any]], str]:
        """基于完整Schema的精确推荐"""
        
        # 使用大模型进行精确推荐
        prompt = self._build_precise_recommendation_prompt(phones, schema, top_n)
        
        try:
            response = self.llm_provider._make_api_request(prompt, "")
            if response:
                recommendations = self._parse_recommendation_response(response, phones)
                return recommendations, 'schema_precise'
            else:
                return self._fallback_recommendation(phones, schema, top_n), 'fallback'
        except Exception as e:
            print(f"⚠️ Schema精确推荐失败: {e}")
            return self._fallback_recommendation(phones, schema, top_n), 'fallback'
    
    def _schema_smart_recommendation(self, phones: List[PhoneSpec], schema: DemandSchema, top_n: int) -> Tuple[List[Dict[str, Any]], str]:
        """基于部分Schema的智能推测推荐"""
        
        # 基于现有Schema信息进行智能推测
        scored_phones = []
        
        for phone in phones:
            # 计算Schema匹配分数
            match_score = self._calculate_schema_match_score(phone, schema)
            
            scored_phones.append({
                'phone': phone,
                'match_score': match_score,
                'match_reasons': self._generate_schema_match_reasons(phone, schema),
                'recommendation_type': 'schema_smart'
            })
        
        # 排序并返回前N个
        scored_phones.sort(key=lambda x: x['match_score'], reverse=True)
        return scored_phones[:top_n], 'schema_smart'
    
    def _schema_guided_recommendation(self, phones: List[PhoneSpec], schema: DemandSchema, top_n: int) -> Tuple[List[Dict[str, Any]], str]:
        """基于Schema的引导式推荐"""
        
        # 基于有限Schema信息推荐多样化选择
        recommendations = []
        
        # 1. 如果有预算信息，推荐不同价位的代表产品
        if schema.budget_range:
            price_ranges = self._get_price_ranges_by_budget(phones, schema.budget_range)
            for price_range in price_ranges[:2]:  # 推荐2个价位段
                representative = self._find_representative_phone_by_schema(phones, price_range, schema)
                if representative:
                    recommendations.append({
                        'phone': representative,
                        'match_score': 0.6,
                        'match_reasons': [f"作为{price_range['name']}的代表产品"],
                        'recommendation_type': 'schema_representative'
                    })
        
        # 2. 如果有品牌偏好，推荐相关品牌产品
        if schema.brand_preferences:
            for brand, preference in schema.brand_preferences.items():
                if preference > 0.5:  # 正面偏好
                    brand_phone = self._find_brand_phone(phones, brand)
                    if brand_phone:
                        recommendations.append({
                            'phone': brand_phone,
                            'match_score': 0.7,
                            'match_reasons': [f"符合您的品牌偏好: {brand}"],
                            'recommendation_type': 'schema_brand_match'
                        })
        
        # 3. 如果有需求片段，推荐相关产品
        if schema.segments:
            for segment in schema.segments[:2]:  # 最多2个片段
                related_phone = self._find_segment_related_phone(phones, segment, schema)
                if related_phone:
                    recommendations.append({
                        'phone': related_phone,
                        'match_score': 0.7,
                        'match_reasons': [f"符合您的{segment.description}"],
                        'recommendation_type': 'schema_segment_match'
                    })
        
        # 4. 推荐热门产品作为补充
        popular_phones = self._get_popular_phones(phones, top_n=2)
        for phone in popular_phones:
            recommendations.append({
                'phone': phone,
                'match_score': 0.5,
                'match_reasons': ["热门选择，用户评价良好"],
                'recommendation_type': 'schema_popular'
            })
        
        return recommendations[:top_n], 'schema_guided'
    
    def _calculate_schema_match_score(self, phone: PhoneSpec, schema: DemandSchema) -> float:
        """计算Schema匹配分数"""
        total_score = 0.0
        total_weight = 0.0
        
        # 1. 需求片段匹配
        for segment in schema.segments:
            segment_score = self._calculate_segment_match_score(phone, segment)
            total_score += segment_score * segment.weight
            total_weight += segment.weight
        
        # 2. 预算匹配
        if schema.budget_range:
            budget_score = self._calculate_budget_match_score(phone, schema.budget_range)
            total_score += budget_score * 0.3
            total_weight += 0.3
        
        # 3. 品牌偏好匹配
        if schema.brand_preferences:
            brand_score = self._calculate_brand_match_score(phone, schema.brand_preferences)
            total_score += brand_score * 0.2
            total_weight += 0.2
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _calculate_segment_match_score(self, phone: PhoneSpec, segment) -> float:
        """计算需求片段匹配分数"""
        category = segment.category
        
        if category == DemandCategory.PERFORMANCE:
            return self._score_performance_match(phone, segment.constraints)
        elif category == DemandCategory.CAMERA:
            return self._score_camera_match(phone, segment.constraints)
        elif category == DemandCategory.BATTERY:
            return self._score_battery_match(phone, segment.constraints)
        elif category == DemandCategory.PORTABILITY:
            return self._score_portability_match(phone, segment.constraints)
        elif category == DemandCategory.PRICE:
            return self._score_price_match(phone, segment.constraints)
        else:
            return 0.7  # 默认分数
    
    def _score_performance_match(self, phone: PhoneSpec, constraints: Dict) -> float:
        """性能匹配评分"""
        score = 0.0
        
        # CPU评分
        cpu_score = self._get_cpu_score(phone.cpu)
        min_cpu_score = constraints.get('min_cpu_score', 0)
        if cpu_score >= min_cpu_score:
            score += 0.4
        
        # 内存评分
        min_ram = constraints.get('min_ram', 0)
        if phone.ram_gb >= min_ram:
            score += 0.3
        
        # 其他性能指标
        score += 0.3
        
        return min(score, 1.0)
    
    def _score_camera_match(self, phone: PhoneSpec, constraints: Dict) -> float:
        """拍照匹配评分"""
        score = 0.0
        
        # 摄像头像素
        min_camera_mp = constraints.get('min_camera_mp', 0)
        if phone.camera_mp >= min_camera_mp:
            score += 0.5
        
        # 摄像头功能
        camera_features = constraints.get('camera_features', [])
        if camera_features:
            score += 0.3
        
        # 其他拍照指标
        score += 0.2
        
        return min(score, 1.0)
    
    def _score_battery_match(self, phone: PhoneSpec, constraints: Dict) -> float:
        """续航匹配评分"""
        score = 0.0
        
        # 电池容量
        min_battery_mah = constraints.get('min_battery_mah', 0)
        if phone.battery_mah >= min_battery_mah:
            score += 0.6
        
        # 充电速度
        score += 0.4
        
        return min(score, 1.0)
    
    def _score_portability_match(self, phone: PhoneSpec, constraints: Dict) -> float:
        """便携性匹配评分"""
        score = 0.0
        
        # 重量
        max_weight_g = constraints.get('max_weight_g', float('inf'))
        if phone.weight_g <= max_weight_g:
            score += 0.5
        
        # 屏幕尺寸
        max_screen_size = constraints.get('max_screen_size', float('inf'))
        if phone.screen_size_inch <= max_screen_size:
            score += 0.5
        
        return min(score, 1.0)
    
    def _score_price_match(self, phone: PhoneSpec, constraints: Dict) -> float:
        """价格匹配评分"""
        max_price = constraints.get('max_price', float('inf'))
        if phone.price <= max_price:
            return 1.0
        else:
            return 0.3
    
    def _get_cpu_score(self, cpu: str) -> float:
        """获取CPU评分"""
        cpu_scores = {
            'A17 Pro': 0.95, 'A16': 0.90, 'A15': 0.85,
            'Snapdragon 8 Gen 3': 0.92, 'Snapdragon 8 Gen 2': 0.88,
            'Dimensity 9300': 0.90, 'Dimensity 9200': 0.85
        }
        return cpu_scores.get(cpu, 0.7)
    
    def _calculate_budget_match_score(self, phone: PhoneSpec, budget_range: Tuple[float, float]) -> float:
        """计算预算匹配分数"""
        min_budget, max_budget = budget_range
        price = phone.price
        
        if min_budget <= price <= max_budget:
            return 1.0
        elif price < min_budget:
            return 0.3
        else:
            return 0.2
    
    def _calculate_brand_match_score(self, phone: PhoneSpec, brand_preferences: Dict[str, float]) -> float:
        """计算品牌匹配分数"""
        phone_brand = self._extract_brand(phone.name)
        
        if phone_brand in brand_preferences:
            return brand_preferences[phone_brand]
        else:
            return 0.5  # 中性分数
    
    def _extract_brand(self, phone_name: str) -> str:
        """提取手机品牌"""
        brand_keywords = {
            'iPhone': 'Apple',
            'Samsung': 'Samsung',
            'Huawei': 'Huawei',
            'Xiaomi': 'Xiaomi',
            'OPPO': 'OPPO',
            'vivo': 'vivo'
        }
        
        for keyword, brand in brand_keywords.items():
            if keyword.lower() in phone_name.lower():
                return brand
        
        return 'Other'
    
    def _build_precise_recommendation_prompt(self, phones: List[PhoneSpec], schema: DemandSchema, top_n: int) -> str:
        """构建精确推荐提示"""
        
        # 构建手机信息
        phones_info = []
        for i, phone in enumerate(phones):
            phone_info = f"{i+1}. {phone.name} - ¥{phone.price} - {phone.cpu} - {phone.camera_mp}MP - {phone.battery_mah}mAh - 评分:{phone.rating}"
            phones_info.append(phone_info)
        
        # 构建Schema信息
        schema_info = f"""
需求Schema分析:
- 需求片段: {[seg.description for seg in schema.segments]}
- 预算范围: {schema.budget_range}
- 品牌偏好: {schema.brand_preferences}
- 使用场景: {schema.usage_scenarios}
- 完整性评分: {schema.completeness_score}
"""
        
        prompt = f"""
作为专业的手机推荐专家，请根据用户的需求Schema推荐最适合的手机。

{schema_info}

可用手机 (共{len(phones)}款):
{chr(10).join(phones_info)}

请推荐{top_n}款最适合的手机，返回JSON格式:
{{
    "recommendations": [
        {{
            "phone_index": 数字(对应上面的编号),
            "match_score": 0.0-1.0,
            "match_reasons": ["理由1", "理由2"],
            "recommendation_type": "schema_precise"
        }}
    ]
}}

推荐要求:
1. 严格按照Schema中的需求进行匹配
2. 考虑预算、品牌偏好等约束条件
3. 提供详细的匹配理由
4. 按匹配度排序

只返回JSON，不要其他内容。
"""
        
        return prompt
    
    def _parse_recommendation_response(self, response: str, phones: List[PhoneSpec]) -> List[Dict[str, Any]]:
        """解析推荐响应"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                recommendations = []
                for rec in data.get('recommendations', []):
                    phone_index = rec['phone_index'] - 1
                    if 0 <= phone_index < len(phones):
                        recommendations.append({
                            'phone': phones[phone_index],
                            'match_score': rec.get('match_score', 0.7),
                            'match_reasons': rec.get('match_reasons', []),
                            'recommendation_type': rec.get('recommendation_type', 'schema_precise')
                        })
                
                return recommendations
            else:
                return []
                
        except Exception as e:
            print(f"⚠️ 推荐响应解析失败: {e}")
            return []
    
    def _fallback_recommendation(self, phones: List[PhoneSpec], schema: DemandSchema, top_n: int) -> List[Dict[str, Any]]:
        """回退推荐"""
        recommendations = []
        
        for i, phone in enumerate(phones[:top_n]):
            recommendations.append({
                'phone': phone,
                'match_score': 0.7 - i * 0.1,
                'match_reasons': ["综合表现良好"],
                'recommendation_type': 'fallback'
            })
        
        return recommendations
    
    def _get_price_ranges_by_budget(self, phones: List[PhoneSpec], budget_range: Tuple[float, float]) -> List[Dict]:
        """根据预算范围获取价格区间"""
        min_budget, max_budget = budget_range
        price_range = max_budget - min_budget
        
        if price_range > 0:
            ranges = [
                {'name': '预算下限', 'min': min_budget, 'max': min_budget + price_range * 0.3},
                {'name': '预算中位', 'min': min_budget + price_range * 0.3, 'max': min_budget + price_range * 0.7},
                {'name': '预算上限', 'min': min_budget + price_range * 0.7, 'max': max_budget}
            ]
        else:
            ranges = [{'name': '目标预算', 'min': min_budget, 'max': max_budget}]
        
        return ranges
    
    def _find_representative_phone_by_schema(self, phones: List[PhoneSpec], price_range: Dict, schema: DemandSchema) -> Optional[PhoneSpec]:
        """在价格区间内找到代表产品"""
        candidates = []
        
        for phone in phones:
            if price_range['min'] <= phone.price <= price_range['max']:
                # 计算Schema匹配评分
                score = self._calculate_schema_match_score(phone, schema)
                candidates.append((phone, score))
        
        if candidates:
            # 返回评分最高的
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None
    
    def _find_brand_phone(self, phones: List[PhoneSpec], brand: str) -> Optional[PhoneSpec]:
        """找到指定品牌的手机"""
        for phone in phones:
            if self._extract_brand(phone.name) == brand:
                return phone
        return None
    
    def _find_segment_related_phone(self, phones: List[PhoneSpec], segment, schema: DemandSchema) -> Optional[PhoneSpec]:
        """根据需求片段找到相关手机"""
        best_match = None
        best_score = 0.0
        
        for phone in phones:
            score = self._calculate_segment_match_score(phone, segment)
            if score > best_score:
                best_score = score
                best_match = phone
        
        return best_match
    
    def _get_popular_phones(self, phones: List[PhoneSpec], top_n: int) -> List[PhoneSpec]:
        """获取热门手机"""
        popular_candidates = []
        
        for phone in phones:
            # 基于评分和价格计算热度
            popularity_score = phone.rating * 0.7 + (phone.sales / 1000) * 0.3
            popular_candidates.append((phone, popularity_score))
        
        popular_candidates.sort(key=lambda x: x[1], reverse=True)
        return [phone for phone, _ in popular_candidates[:top_n]]
    
    def _generate_schema_match_reasons(self, phone: PhoneSpec, schema: DemandSchema) -> List[str]:
        """生成Schema匹配理由"""
        reasons = []
        
        # 基于需求片段生成理由
        for segment in schema.segments:
            if segment.category == DemandCategory.CAMERA and phone.camera_mp >= 50:
                reasons.append("拍照能力优秀")
            elif segment.category == DemandCategory.PERFORMANCE and self._get_cpu_score(phone.cpu) >= 0.8:
                reasons.append("性能配置强劲")
            elif segment.category == DemandCategory.BATTERY and phone.battery_mah >= 4500:
                reasons.append("续航表现良好")
        
        # 基于预算生成理由
        if schema.budget_range:
            price = phone.price
            min_budget, max_budget = schema.budget_range
            
            if min_budget <= price <= max_budget:
                reasons.append("价格符合预算")
        
        return reasons if reasons else ["综合表现均衡"]
    
    def _generate_match_details(self, recommendations: List[Dict[str, Any]], schema: DemandSchema) -> List[Dict[str, Any]]:
        """生成匹配详情"""
        details = []
        
        for rec in recommendations:
            phone = rec['phone']
            detail = {
                'phone_name': phone.name,
                'match_score': rec['match_score'],
                'match_reasons': rec['match_reasons'],
                'schema_analysis': {
                    'segments_matched': len([seg for seg in schema.segments if self._calculate_segment_match_score(phone, seg) > 0.5]),
                    'budget_match': self._calculate_budget_match_score(phone, schema.budget_range) if schema.budget_range else 0.5,
                    'brand_match': self._calculate_brand_match_score(phone, schema.brand_preferences) if schema.brand_preferences else 0.5
                }
            }
            details.append(detail)
        
        return details
    
    def _determine_next_steps(self, schema: DemandSchema, clarification_questions: List[str]) -> List[str]:
        """确定下一步行动"""
        next_steps = []
        
        if clarification_questions:
            next_steps.append("回答澄清问题以获得更精确的推荐")
        
        if schema.completeness_score < 0.7:
            next_steps.append("提供更多需求细节完善Schema")
        
        if schema.segments:
            next_steps.append("查看详细参数对比")
        
        next_steps.append("了解用户评价和体验")
        
        return next_steps 