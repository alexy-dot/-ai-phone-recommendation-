#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能推荐引擎 - 完全基于大模型的推荐算法
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from services.llm_provider import LLMProvider

@dataclass
class Recommendation:
    """推荐结果"""
    rank: int
    phone_id: str
    name: str
    price: float
    score: float
    reasons: List[str]
    explanation: str
    metadata: Dict = field(default_factory=dict)

@dataclass
class UserDemand:
    """用户需求"""
    budget: Dict[str, Any]
    performance: Dict[str, Any]
    camera: Dict[str, Any]
    battery: Dict[str, Any]
    design: Dict[str, Any]
    brand: Dict[str, Any]
    special_requirements: List[str]
    confidence: float

class IntelligentRecommendationEngine:
    """智能推荐引擎 - 大模型驱动"""
    
    def __init__(self):
        self.llm_provider = LLMProvider()
    
    async def recommend_phones(self, user_demand: UserDemand, available_phones: List[Dict]) -> List[Recommendation]:
        """智能推荐手机"""
        
        # 1. 大模型预筛选
        candidate_phones = await self._llm_pre_filter(user_demand, available_phones)
        
        # 2. 多维度智能评分
        scored_phones = await self._intelligent_scoring(user_demand, candidate_phones)
        
        # 3. 个性化排序
        ranked_phones = await self._personalized_ranking(user_demand, scored_phones)
        
        # 4. 生成推荐解释
        recommendations = await self._generate_explanations(user_demand, ranked_phones)
        
        return recommendations
    
    async def _llm_pre_filter(self, demand: UserDemand, phones: List[Dict]) -> List[Dict]:
        """大模型预筛选"""
        
        # 构建需求描述
        demand_description = self._build_demand_description(demand)
        
        # 构建手机信息
        phones_info = []
        for i, phone in enumerate(phones):
            phone_info = f"{i+1}. {phone['name']} - ¥{phone['price']} - {phone['cpu']} - {phone['camera_mp']}MP - {phone['battery_mah']}mAh"
            phones_info.append(phone_info)
        
        prompt = f"""
        作为手机推荐专家，请从以下手机中筛选出最适合用户需求的候选机型。

        用户需求:
        {demand_description}

        可用手机 (共{len(phones)}款):
        {chr(10).join(phones_info)}

        请返回JSON格式的筛选结果:
        {{
            "candidates": [
                {{
                    "phone_index": 数字(对应上面的编号),
                    "reason": "筛选理由",
                    "match_score": 0.0-1.0
                }}
            ],
            "total_candidates": 候选数量,
            "filtering_criteria": "筛选标准说明"
        }}

        要求:
        1. 根据用户预算、性能需求、拍照需求等进行筛选
        2. 选择10-15款最适合的候选机型
        3. 每款都要有筛选理由和匹配分数
        4. 考虑用户的特殊要求

        只返回JSON，不要其他内容。
        """
        
        try:
            response = await self._call_llm(prompt)
            if response and response.strip():  # 确保response不为None且不为空字符串
                result = json.loads(response.strip())
                
                # 根据筛选结果返回候选手机
                candidates = []
                for candidate in result.get('candidates', []):
                    phone_index = candidate['phone_index'] - 1  # 转换为0基索引
                    if 0 <= phone_index < len(phones):
                        phone = phones[phone_index].copy()
                        phone['match_score'] = candidate['match_score']
                        phone['filter_reason'] = candidate['reason']
                        candidates.append(phone)
                
                return candidates
            else:
                raise Exception("LLM返回空响应")
        except Exception as e:
            print(f"大模型预筛选失败: {e}")
            # 回退到简单筛选
            return self._fallback_filter(demand, phones)
    
    async def _intelligent_scoring(self, demand: UserDemand, candidate_phones: List[Dict]) -> List[Dict]:
        """多维度智能评分"""
        
        demand_description = self._build_demand_description(demand)
        
        # 构建评分提示词
        phones_info = []
        for phone in candidate_phones:
            phone_info = f"- {phone['name']}: ¥{phone['price']}, {phone['cpu']}, {phone['camera_mp']}MP, {phone['battery_mah']}mAh"
            phones_info.append(phone_info)
        
        prompt = f"""
        作为手机评分专家，请对候选手机进行多维度智能评分。

        用户需求:
        {demand_description}

        候选手机:
        {chr(10).join(phones_info)}

        请返回JSON格式的评分结果:
        {{
            "scored_phones": [
                {{
                    "phone_name": "手机名称",
                    "overall_score": 0.0-1.0,
                    "dimension_scores": {{
                        "budget_match": 0.0-1.0,
                        "performance_match": 0.0-1.0,
                        "camera_match": 0.0-1.0,
                        "battery_match": 0.0-1.0,
                        "design_match": 0.0-1.0,
                        "brand_match": 0.0-1.0
                    }},
                    "strengths": ["优势1", "优势2"],
                    "weaknesses": ["劣势1", "劣势2"],
                    "detailed_analysis": "详细分析"
                }}
            ]
        }}

        评分标准:
        1. 预算匹配度: 价格是否符合用户预算
        2. 性能匹配度: CPU、内存等是否满足性能需求
        3. 拍照匹配度: 摄像头配置是否满足拍照需求
        4. 续航匹配度: 电池容量和充电是否满足需求
        5. 设计匹配度: 尺寸、重量、外观是否符合偏好
        6. 品牌匹配度: 品牌是否符合用户偏好

        只返回JSON，不要其他内容。
        """
        
        try:
            response = await self._call_llm(prompt)
            if response and response.strip():  # 确保response不为None且不为空字符串
                result = json.loads(response.strip())
                
                # 将评分结果合并到手机数据中
                scored_phones = []
                for scored_phone in result.get('scored_phones', []):
                    # 找到对应的原始手机数据
                    for phone in candidate_phones:
                        if phone['name'] == scored_phone['phone_name']:
                            phone.update(scored_phone)
                            scored_phones.append(phone)
                            break
                
                return scored_phones
            else:
                raise Exception("LLM返回空响应")
        except Exception as e:
            print(f"智能评分失败: {e}")
            # 回退到简单评分
            return self._fallback_scoring(demand, candidate_phones)
    
    async def _personalized_ranking(self, demand: UserDemand, scored_phones: List[Dict]) -> List[Dict]:
        """个性化排序"""
        
        demand_description = self._build_demand_description(demand)
        
        # 构建排序提示词
        phones_info = []
        for phone in scored_phones:
            phone_info = f"- {phone['name']}: 总分{phone.get('final_score', 0):.2f}, 优势{phone.get('strengths', [])}"
            phones_info.append(phone_info)
        
        prompt = f"""
        作为手机推荐专家，请根据用户需求对已评分的手机进行个性化排序。

        用户需求:
        {demand_description}

        已评分手机:
        {chr(10).join(phones_info)}

        请返回JSON格式的排序结果:
        {{
            "ranked_phones": [
                {{
                    "rank": 1,
                    "phone_name": "手机名称",
                    "final_score": 0.0-1.0,
                    "ranking_reason": "排序理由",
                    "personalization_factors": ["个性化因素1", "个性化因素2"]
                }}
            ],
            "ranking_strategy": "排序策略说明"
        }}

        排序考虑因素:
        1. 用户预算偏好(严格/灵活)
        2. 各维度优先级权重
        3. 特殊需求匹配度
        4. 品牌偏好
        5. 性价比平衡

        只返回JSON，不要其他内容。
        """
        
        try:
            response = await self._call_llm(prompt)
            if response and response.strip():  # 确保response不为None且不为空字符串
                result = json.loads(response.strip())
                
                # 根据排序结果重新排列手机
                ranked_phones = []
                for ranked_phone in result.get('ranked_phones', []):
                    # 找到对应的手机数据
                    for phone in scored_phones:
                        if phone['name'] == ranked_phone['phone_name']:
                            phone['rank'] = ranked_phone['rank']
                            phone['final_score'] = ranked_phone['final_score']
                            phone['ranking_reason'] = ranked_phone['ranking_reason']
                            phone['personalization_factors'] = ranked_phone['personalization_factors']
                            ranked_phones.append(phone)
                            break
                
                return ranked_phones
            else:
                raise Exception("LLM返回空响应")
        except Exception as e:
            print(f"个性化排序失败: {e}")
            # 回退到简单排序
            return self._fallback_ranking(scored_phones)
    
    async def _generate_explanations(self, demand: UserDemand, ranked_phones: List[Dict]) -> List[Recommendation]:
        """生成推荐解释"""
        
        recommendations = []
        
        for i, phone in enumerate(ranked_phones[:5]):  # 取前5名
            # 生成个性化推荐解释
            explanation = await self._generate_phone_explanation(demand, phone, i + 1)
            
            recommendation = Recommendation(
                rank=i + 1,
                phone_id=phone.get('id', f"phone_{i}"),
                name=phone['name'],
                price=phone['price'],
                score=phone.get('final_score', phone.get('overall_score', 0.5)),
                reasons=phone.get('strengths', []),
                explanation=explanation,
                metadata={
                    'dimension_scores': phone.get('dimension_scores', {}),
                    'ranking_reason': phone.get('ranking_reason', ''),
                    'personalization_factors': phone.get('personalization_factors', [])
                }
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_phone_explanation(self, demand: UserDemand, phone: Dict, rank: int) -> str:
        """生成单个手机的推荐解释"""
        
        prompt = f"""
        作为专业的手机导购，请为这款手机生成个性化的推荐解释。

        用户需求:
        {self._build_demand_description(demand)}

        推荐手机 (第{rank}名):
        - 名称: {phone['name']}
        - 价格: ¥{phone['price']}
        - 总分: {phone.get('final_score', 0):.2f}
        - 优势: {phone.get('strengths', [])}
        - 劣势: {phone.get('weaknesses', [])}
        - 排序理由: {phone.get('ranking_reason', '')}

        请生成一段自然、详细的推荐解释，说明为什么这款手机适合用户的需求。
        解释要包含:
        1. 与用户需求的匹配点
        2. 主要优势说明
        3. 可能的注意事项
        4. 购买建议

        请直接返回解释内容，不要其他格式。
        """
        
        try:
            explanation = await self._call_llm(prompt)
            return explanation
        except Exception as e:
            print(f"生成推荐解释失败: {e}")
            return f"我推荐{phone['name']}，这款手机在多个方面都符合您的需求。"
    
    def _build_demand_description(self, demand: UserDemand) -> str:
        """构建需求描述"""
        description_parts = []
        
        # 预算
        budget = demand.budget
        if budget.get('min') or budget.get('max'):
            budget_desc = f"预算: ¥{budget.get('min', '不限')} - ¥{budget.get('max', '不限')} ({budget.get('preference', '灵活')})"
            description_parts.append(budget_desc)
        
        # 性能
        performance = demand.performance
        if performance.get('level'):
            perf_desc = f"性能需求: {performance['level']}级, 用途: {', '.join(performance.get('usage', []))}, 优先级: {performance.get('priority', 5)}"
            description_parts.append(perf_desc)
        
        # 拍照
        camera = demand.camera
        if camera.get('quality'):
            camera_desc = f"拍照需求: {camera['quality']}级, 功能: {', '.join(camera.get('features', []))}, 优先级: {camera.get('priority', 5)}"
            description_parts.append(camera_desc)
        
        # 续航
        battery = demand.battery
        if battery.get('capacity'):
            battery_desc = f"续航需求: {battery['capacity']}容量, 充电: {battery.get('charging', '标准')}, 优先级: {battery.get('priority', 5)}"
            description_parts.append(battery_desc)
        
        # 设计
        design = demand.design
        if design.get('size'):
            design_desc = f"设计偏好: {design['size']}, 重量: {design.get('weight', '标准')}, 风格: {design.get('style', '通用')}, 优先级: {design.get('priority', 5)}"
            description_parts.append(design_desc)
        
        # 品牌
        brand = demand.brand
        if brand.get('preferences') or brand.get('avoid'):
            brand_desc = f"品牌偏好: {', '.join(brand.get('preferences', []))}, 避免: {', '.join(brand.get('avoid', []))}, 优先级: {brand.get('priority', 5)}"
            description_parts.append(brand_desc)
        
        # 特殊要求
        if demand.special_requirements:
            special_desc = f"特殊要求: {', '.join(demand.special_requirements)}"
            description_parts.append(special_desc)
        
        return "\n".join(description_parts)
    
    async def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.llm_provider._make_api_request, prompt, "")
            
            # 检查响应是否有效
            if response and response.strip():
                return response.strip()
            else:
                print("⚠️ LLM API返回空响应，使用回退处理")
                return ""
        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            return ""
    
    def _fallback_filter(self, demand: UserDemand, phones: List[Dict]) -> List[Dict]:
        """回退筛选"""
        candidates = []
        for phone in phones:
            # 简单的预算筛选
            if demand.budget.get('max') and phone['price'] > demand.budget['max']:
                continue
            if demand.budget.get('min') and phone['price'] < demand.budget['min']:
                continue
            candidates.append(phone)
        return candidates[:15]  # 限制15款
    
    def _fallback_scoring(self, demand: UserDemand, phones: List[Dict]) -> List[Dict]:
        """回退评分"""
        for phone in phones:
            phone['overall_score'] = 0.5  # 默认分数
            phone['strengths'] = ['性价比不错']
            phone['weaknesses'] = ['需要进一步了解']
        return phones
    
    def _fallback_ranking(self, phones: List[Dict]) -> List[Dict]:
        """回退排序"""
        # 按价格排序
        phones.sort(key=lambda x: x['price'])
        for i, phone in enumerate(phones):
            phone['rank'] = i + 1
            phone['final_score'] = phone.get('overall_score', 0.5)
        return phones 