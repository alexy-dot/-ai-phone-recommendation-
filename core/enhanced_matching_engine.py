#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版匹配引擎
实现预过滤 + 向量化 + 精确排序的完整流程
"""

from typing import List, Dict, Any, Tuple
from database.sample_data import PhoneSpec
from core.vectorization_engine import VectorizationEngine, PhonePerformanceVector
from core.enhanced_demand_parser import EnhancedDemandParser, SpecificRequirement
from core.vector_matching import VectorMatchingEngine
from core.demand_vectorization import UserDemandVector
import math


class EnhancedMatchingEngine:
    """增强版匹配引擎"""
    
    def __init__(self):
        self.vectorization_engine = VectorizationEngine()
        self.demand_parser = EnhancedDemandParser()
        self.vector_matching_engine = VectorMatchingEngine()
        
        # 匹配配置
        self.matching_config = {
            'pre_filter_threshold': 0.3,      # 预过滤阈值
            'exact_match_bonus': 0.2,         # 精确匹配奖励
            'range_match_bonus': 0.1,         # 范围匹配奖励
            'minimum_requirement_penalty': 0.5, # 最低要求不满足惩罚
            'maximum_requirement_penalty': 0.3, # 最高要求超出惩罚
            'vector_weight': 0.7,             # 向量匹配权重
            'exact_weight': 0.3               # 精确匹配权重
        }
    
    def match_phones(self, phones: List[PhoneSpec], user_input: str, 
                    top_n: int = 5) -> List[Dict[str, Any]]:
        """完整的匹配流程"""
        print("🔍 开始增强版匹配流程...")
        
        # 1. 解析用户需求
        print("📝 解析用户需求...")
        demand_analysis = self.demand_parser.parse_demand(user_input)
        
        print(f"   需求摘要: {demand_analysis.demand_summary}")
        print(f"   具体需求数量: {len(demand_analysis.specific_requirements)}")
        print(f"   关注维度: {demand_analysis.focus_dimensions}")
        
        # 2. 预过滤 - 基于明确需求
        print("🔍 执行预过滤...")
        filtered_phones = self._pre_filter_phones(phones, demand_analysis.specific_requirements)
        print(f"   预过滤结果: {len(phones)} → {len(filtered_phones)} 款手机")
        
        if not filtered_phones:
            print("⚠️ 预过滤后无符合要求的手机，使用原始列表")
            filtered_phones = phones
        
        # 3. 向量化手机
        print("📊 向量化手机参数...")
        phones_with_vectors = self._vectorize_phones(filtered_phones, demand_analysis.budget_info)
        
        # 4. 创建UserDemandVector对象
        demand_vector = self._create_demand_vector(demand_analysis)
        
        # 5. 计算综合匹配分数
        print("🎯 计算综合匹配分数...")
        ranked_phones = self._calculate_comprehensive_scores(
            phones_with_vectors, demand_analysis, demand_vector
        )
        
        # 6. 生成推荐理由
        print("💡 生成推荐理由...")
        for rec in ranked_phones[:top_n]:
            reasons = self._generate_recommendation_reasons(
                rec['phone'], rec['phone_vector'], demand_analysis
            )
            rec['reasons'] = reasons
        
        print(f"✅ 匹配完成！推荐 {len(ranked_phones[:top_n])} 款手机")
        return ranked_phones[:top_n]
    
    def _create_demand_vector(self, demand_analysis) -> UserDemandVector:
        """创建UserDemandVector对象"""
        demand_vector = UserDemandVector()
        
        # 设置向量权重
        for dimension, weight in demand_analysis.vector_weights.items():
            if hasattr(demand_vector, dimension):
                setattr(demand_vector, dimension, weight)
        
        # 设置关注维度
        demand_vector.focus_dimensions = demand_analysis.focus_dimensions
        
        return demand_vector
    
    def _pre_filter_phones(self, phones: List[PhoneSpec], 
                          requirements: List[SpecificRequirement]) -> List[PhoneSpec]:
        """基于明确需求进行预过滤"""
        if not requirements:
            return phones
        
        filtered_phones = []
        
        for phone in phones:
            meets_all_requirements = True
            
            for req in requirements:
                if not self._check_requirement_match(phone, req):
                    meets_all_requirements = False
                    break
            
            if meets_all_requirements:
                filtered_phones.append(phone)
        
        return filtered_phones
    
    def _check_requirement_match(self, phone: PhoneSpec, requirement: SpecificRequirement) -> bool:
        """检查单个需求是否匹配"""
        phone_value = self._get_phone_value(phone, requirement.dimension)
        
        if requirement.requirement_type == 'exact':
            # 精确匹配
            tolerance = requirement.tolerance * requirement.value
            return abs(phone_value - requirement.value) <= tolerance
        
        elif requirement.requirement_type == 'range':
            # 范围匹配
            tolerance = requirement.tolerance * requirement.value
            return abs(phone_value - requirement.value) <= tolerance
        
        elif requirement.requirement_type == 'minimum':
            # 最低要求
            return phone_value >= requirement.value
        
        elif requirement.requirement_type == 'maximum':
            # 最高要求
            return phone_value <= requirement.value
        
        return True
    
    def _get_phone_value(self, phone: PhoneSpec, dimension: str) -> float:
        """获取手机在指定维度的数值"""
        dimension_mapping = {
            'storage_speed': phone.storage_gb,
            'memory_capacity': phone.ram_gb,
            'screen_size': phone.screen_size_inch,
            'battery_capacity': phone.battery_mah,
            'camera_quality': phone.camera_mp,
            'price_value': phone.price
        }
        
        return dimension_mapping.get(dimension, 0.0)
    
    def _vectorize_phones(self, phones: List[PhoneSpec], budget_info: Dict) -> List[Tuple[PhoneSpec, PhonePerformanceVector]]:
        """向量化手机列表"""
        phones_with_vectors = []
        
        for phone in phones:
            phone_vector = self.vectorization_engine.vectorize_phone(phone, budget_info)
            phones_with_vectors.append((phone, phone_vector))
        
        return phones_with_vectors
    
    def _calculate_comprehensive_scores(self, phones_with_vectors: List[Tuple[PhoneSpec, PhonePerformanceVector]], 
                                      demand_analysis, demand_vector: UserDemandVector) -> List[Dict[str, Any]]:
        """计算综合匹配分数"""
        results = []
        
        for phone, phone_vector in phones_with_vectors:
            # 1. 向量匹配分数
            vector_score = self.vector_matching_engine.calculate_match_score(
                phone_vector, demand_vector
            )
            
            # 2. 精确匹配分数
            exact_score = self._calculate_exact_match_score(phone, demand_analysis.specific_requirements)
            
            # 3. 综合分数
            comprehensive_score = (
                vector_score * self.matching_config['vector_weight'] +
                exact_score * self.matching_config['exact_weight']
            )
            
            # 4. 应用奖励和惩罚
            final_score = self._apply_bonuses_and_penalties(
                comprehensive_score, phone, demand_analysis.specific_requirements
            )
            
            results.append({
                'phone': phone,
                'phone_vector': phone_vector,
                'vector_score': vector_score,
                'exact_score': exact_score,
                'comprehensive_score': comprehensive_score,
                'match_score': final_score,
                'rank': 0  # 稍后设置
            })
        
        # 排序
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # 设置排名
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        return results
    
    def _calculate_exact_match_score(self, phone: PhoneSpec, requirements: List[SpecificRequirement]) -> float:
        """计算精确匹配分数"""
        if not requirements:
            return 0.5  # 默认分数
        
        total_score = 0.0
        total_weight = 0.0
        
        for req in requirements:
            phone_value = self._get_phone_value(phone, req.dimension)
            
            if req.requirement_type == 'exact':
                # 精确匹配
                tolerance = req.tolerance * req.value
                if tolerance <= 0:  # 防止除零错误
                    tolerance = req.value * 0.1  # 默认10%容差
                
                diff = abs(phone_value - req.value)
                if diff <= tolerance:
                    score = 1.0 - (diff / tolerance) * 0.3
                else:
                    score = max(0.0, 0.7 - (diff - tolerance) / req.value * 0.5)
            
            elif req.requirement_type == 'range':
                # 范围匹配
                tolerance = req.tolerance * req.value
                if tolerance <= 0:  # 防止除零错误
                    tolerance = req.value * 0.1  # 默认10%容差
                
                diff = abs(phone_value - req.value)
                if diff <= tolerance:
                    score = 1.0 - (diff / tolerance) * 0.2
                else:
                    score = max(0.0, 0.8 - (diff - tolerance) / req.value * 0.4)
            
            elif req.requirement_type == 'minimum':
                # 最低要求
                if phone_value >= req.value:
                    score = 1.0
                else:
                    score = max(0.0, phone_value / req.value) if req.value > 0 else 0.0
            
            elif req.requirement_type == 'maximum':
                # 最高要求
                if phone_value <= req.value:
                    score = 1.0
                else:
                    score = max(0.0, req.value / phone_value) if phone_value > 0 else 0.0
            
            else:
                score = 0.5
            
            # 权重分配（可以根据需求重要性调整）
            weight = 1.0
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _apply_bonuses_and_penalties(self, base_score: float, phone: PhoneSpec, 
                                   requirements: List[SpecificRequirement]) -> float:
        """应用奖励和惩罚"""
        final_score = base_score
        
        for req in requirements:
            phone_value = self._get_phone_value(phone, req.dimension)
            
            if req.requirement_type == 'exact':
                # 精确匹配奖励
                tolerance = req.tolerance * req.value
                if abs(phone_value - req.value) <= tolerance * 0.5:  # 非常接近
                    final_score += self.matching_config['exact_match_bonus']
            
            elif req.requirement_type == 'range':
                # 范围匹配奖励
                tolerance = req.tolerance * req.value
                if abs(phone_value - req.value) <= tolerance * 0.5:
                    final_score += self.matching_config['range_match_bonus']
            
            elif req.requirement_type == 'minimum':
                # 最低要求惩罚
                if phone_value < req.value:
                    final_score *= (1 - self.matching_config['minimum_requirement_penalty'])
            
            elif req.requirement_type == 'maximum':
                # 最高要求惩罚
                if phone_value > req.value:
                    final_score *= (1 - self.matching_config['maximum_requirement_penalty'])
        
        return min(max(final_score, 0.0), 1.0)
    
    def _generate_recommendation_reasons(self, phone: PhoneSpec, phone_vector: PhonePerformanceVector, 
                                       demand_analysis) -> List[str]:
        """生成推荐理由"""
        reasons = []
        
        # 基于具体需求的理由
        for req in demand_analysis.specific_requirements:
            phone_value = self._get_phone_value(phone, req.dimension)
            
            if req.requirement_type == 'exact':
                tolerance = req.tolerance * req.value
                if abs(phone_value - req.value) <= tolerance:
                    reasons.append(f"符合{req.value}{req.unit}需求")
            
            elif req.requirement_type == 'minimum':
                if phone_value >= req.value:
                    reasons.append(f"满足最低{req.value}{req.unit}要求")
            
            elif req.requirement_type == 'maximum':
                if phone_value <= req.value:
                    reasons.append(f"符合最高{req.value}{req.unit}限制")
        
        # 基于向量权重的理由
        dimension_names = {
            'cpu_performance': '性能',
            'camera_quality': '拍照',
            'battery_capacity': '续航',
            'weight_portability': '便携',
            'price_value': '性价比',
            'screen_quality': '屏幕',
            'build_quality': '做工',
            'design_appeal': '外观'
        }
        
        for dimension, weight in demand_analysis.vector_weights.items():
            if weight > 0.3:
                phone_score = getattr(phone_vector, dimension, 0.0)
                if phone_score > 0.7:
                    dimension_name = dimension_names.get(dimension, dimension)
                    reasons.append(f"{dimension_name}优秀")
        
        # 如果没有理由，添加默认理由
        if not reasons:
            reasons.append("综合性能良好")
        
        return reasons[:3]  # 最多3个理由 