#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量匹配引擎
实现手机性能向量与用户需求向量的匹配计算
"""

from typing import Dict, List, Tuple
from core.vectorization_engine import PhonePerformanceVector
from core.demand_vectorization import UserDemandVector


class VectorMatchingEngine:
    """向量匹配引擎"""
    
    def __init__(self):
        # 匹配算法配置
        self.matching_config = {
            'min_overlap_threshold': 0.1,  # 最小重叠阈值
            'weight_normalization': True,   # 是否进行权重归一化
            'bonus_for_perfect_match': 0.1  # 完美匹配的奖励分数
        }
    
    def calculate_match_score(self, phone_vector: PhonePerformanceVector, 
                            demand_vector: UserDemandVector) -> float:
        """计算匹配分数"""
        total_score = 0.0
        total_weight = 0.0
        overlap_count = 0
        
        # 获取向量字典
        phone_scores = phone_vector.to_dict()
        demand_weights = demand_vector.to_dict()
        
        for dimension in phone_scores:
            phone_score = phone_scores[dimension]
            demand_weight = demand_weights[dimension]
            
            # 重叠匹配：用户有需求的维度才参与计算
            if demand_weight > self.matching_config['min_overlap_threshold']:
                # 加权匹配分数
                match_score = phone_score * demand_weight
                total_score += match_score
                total_weight += demand_weight
                overlap_count += 1
        
        # 归一化分数
        if total_weight > 0:
            normalized_score = total_score / total_weight
            
            # 如果重叠维度较多，给予奖励
            if overlap_count >= 5:
                normalized_score += self.matching_config['bonus_for_perfect_match']
            
            return min(normalized_score, 1.0)
        else:
            return 0.0
    
    def get_focus_dimensions_scores(self, phone_vector: PhonePerformanceVector,
                                  demand_vector: UserDemandVector) -> Dict[str, float]:
        """获取用户关注维度的分数（用于雷达图）"""
        focus_scores = {}
        phone_scores = phone_vector.to_dict()
        
        for dimension in demand_vector.focus_dimensions:
            if dimension in phone_scores:
                focus_scores[dimension] = phone_scores[dimension]
        
        return focus_scores
    
    def get_detailed_match_analysis(self, phone_vector: PhonePerformanceVector,
                                  demand_vector: UserDemandVector) -> Dict:
        """获取详细的匹配分析"""
        phone_scores = phone_vector.to_dict()
        demand_weights = demand_vector.to_dict()
        
        analysis = {
            'overall_score': 0.0,
            'dimension_scores': {},
            'strengths': [],
            'weaknesses': [],
            'overlap_count': 0,
            'total_weight': 0.0
        }
        
        total_score = 0.0
        total_weight = 0.0
        overlap_count = 0
        
        for dimension in phone_scores:
            phone_score = phone_scores[dimension]
            demand_weight = demand_weights[dimension]
            
            if demand_weight > self.matching_config['min_overlap_threshold']:
                match_score = phone_score * demand_weight
                total_score += match_score
                total_weight += demand_weight
                overlap_count += 1
                
                # 记录维度分数
                analysis['dimension_scores'][dimension] = {
                    'phone_score': phone_score,
                    'demand_weight': demand_weight,
                    'match_score': match_score
                }
                
                # 判断强项和弱项
                if phone_score >= 0.8:
                    analysis['strengths'].append(dimension)
                elif phone_score <= 0.4:
                    analysis['weaknesses'].append(dimension)
        
        # 计算总体分数
        if total_weight > 0:
            analysis['overall_score'] = total_score / total_weight
            analysis['overlap_count'] = overlap_count
            analysis['total_weight'] = total_weight
        
        return analysis
    
    def rank_phones_by_demand(self, phones_with_vectors: List[Tuple], 
                            demand_vector: UserDemandVector) -> List[Dict]:
        """根据需求对手机进行排名"""
        ranked_phones = []
        
        for phone, phone_vector in phones_with_vectors:
            match_score = self.calculate_match_score(phone_vector, demand_vector)
            focus_scores = self.get_focus_dimensions_scores(phone_vector, demand_vector)
            detailed_analysis = self.get_detailed_match_analysis(phone_vector, demand_vector)
            
            ranked_phones.append({
                'phone': phone,
                'phone_vector': phone_vector,
                'match_score': match_score,
                'focus_scores': focus_scores,
                'detailed_analysis': detailed_analysis
            })
        
        # 按匹配分数排序
        ranked_phones.sort(key=lambda x: x['match_score'], reverse=True)
        
        return ranked_phones
    
    def get_recommendation_reasons(self, phone_vector: PhonePerformanceVector,
                                 demand_vector: UserDemandVector) -> List[str]:
        """获取推荐理由"""
        reasons = []
        phone_scores = phone_vector.to_dict()
        demand_weights = demand_vector.to_dict()
        
        # 维度名称映射
        dimension_names = {
            'cpu_performance': 'CPU性能',
            'camera_quality': '拍照质量',
            'battery_capacity': '电池容量',
            'weight_portability': '便携性',
            'price_value': '性价比',
            'screen_quality': '屏幕质量',
            'build_quality': '做工质量',
            'design_appeal': '设计外观',
            'gpu_performance': '游戏性能',
            'memory_capacity': '内存容量',
            'storage_speed': '存储速度',
            'camera_features': '拍照功能',
            'charging_speed': '充电速度',
            'screen_size': '屏幕尺寸',
            'size_portability': '尺寸便携',
            'heat_control': '散热控制',
            'network_stability': '网络稳定性',
            'software_optimization': '系统优化',
            'durability': '耐用性'
        }
        
        # 找出用户关注且手机表现优秀的维度
        for dimension, demand_weight in demand_weights.items():
            if demand_weight > 0.3:  # 用户比较关注的维度
                phone_score = phone_scores[dimension]
                if phone_score > 0.8:  # 手机在该维度表现优秀
                    dimension_name = dimension_names.get(dimension, dimension)
                    reasons.append(f"{dimension_name}优秀")
                elif phone_score > 0.6:  # 手机在该维度表现良好
                    dimension_name = dimension_names.get(dimension, dimension)
                    reasons.append(f"{dimension_name}良好")
        
        # 如果没有找到具体理由，提供通用理由
        if not reasons:
            overall_score = self.calculate_match_score(phone_vector, demand_vector)
            if overall_score > 0.8:
                reasons.append("综合性能优秀")
            elif overall_score > 0.6:
                reasons.append("综合性能良好")
            else:
                reasons.append("符合基本需求")
        
        return reasons[:3]  # 最多返回3个理由
    
    def calculate_similarity_score(self, phone_vector1: PhonePerformanceVector,
                                 phone_vector2: PhonePerformanceVector) -> float:
        """计算两个手机向量的相似度"""
        scores1 = phone_vector1.to_dict()
        scores2 = phone_vector2.to_dict()
        
        total_diff = 0.0
        dimension_count = 0
        
        for dimension in scores1:
            if dimension in scores2:
                diff = abs(scores1[dimension] - scores2[dimension])
                total_diff += diff
                dimension_count += 1
        
        if dimension_count > 0:
            avg_diff = total_diff / dimension_count
            # 相似度 = 1 - 平均差异
            similarity = 1.0 - avg_diff
            return max(0.0, min(1.0, similarity))
        
        return 0.0
    
    def find_similar_phones(self, target_phone_vector: PhonePerformanceVector,
                          all_phone_vectors: List[Tuple], 
                          similarity_threshold: float = 0.7) -> List[Dict]:
        """查找相似的手机"""
        similar_phones = []
        
        for phone, phone_vector in all_phone_vectors:
            similarity = self.calculate_similarity_score(target_phone_vector, phone_vector)
            
            if similarity >= similarity_threshold:
                similar_phones.append({
                    'phone': phone,
                    'phone_vector': phone_vector,
                    'similarity_score': similarity
                })
        
        # 按相似度排序
        similar_phones.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar_phones
    
    def get_demand_coverage_analysis(self, phone_vector: PhonePerformanceVector,
                                   demand_vector: UserDemandVector) -> Dict:
        """分析手机对用户需求的覆盖程度"""
        phone_scores = phone_vector.to_dict()
        demand_weights = demand_vector.to_dict()
        
        coverage_analysis = {
            'high_coverage': [],    # 高覆盖维度（手机分数高且用户需求高）
            'medium_coverage': [],  # 中等覆盖维度
            'low_coverage': [],     # 低覆盖维度
            'uncovered': [],        # 未覆盖维度（用户有需求但手机分数低）
            'coverage_score': 0.0   # 总体覆盖分数
        }
        
        total_coverage = 0.0
        total_demand = 0.0
        
        for dimension, demand_weight in demand_weights.items():
            if demand_weight > 0.1:  # 用户有需求的维度
                phone_score = phone_scores[dimension]
                coverage = phone_score * demand_weight
                total_coverage += coverage
                total_demand += demand_weight
                
                # 分类覆盖程度
                if phone_score >= 0.8 and demand_weight >= 0.5:
                    coverage_analysis['high_coverage'].append(dimension)
                elif phone_score >= 0.6 and demand_weight >= 0.3:
                    coverage_analysis['medium_coverage'].append(dimension)
                elif phone_score < 0.4 and demand_weight >= 0.3:
                    coverage_analysis['uncovered'].append(dimension)
                else:
                    coverage_analysis['low_coverage'].append(dimension)
        
        # 计算总体覆盖分数
        if total_demand > 0:
            coverage_analysis['coverage_score'] = total_coverage / total_demand
        
        return coverage_analysis 