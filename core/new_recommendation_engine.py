#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新的推荐引擎
整合向量化、匹配和雷达图生成功能
"""

from typing import List, Dict, Any, Tuple
from database.sample_data import PhoneSpec
from core.vectorization_engine import VectorizationEngine, PhonePerformanceVector
from core.demand_vectorization import DemandVectorizationEngine, UserDemandVector
from core.vector_matching import VectorMatchingEngine
from utils.dynamic_radar import DynamicRadarChartGenerator
import os
from datetime import datetime


class NewRecommendationEngine:
    """新的推荐引擎"""
    
    def __init__(self):
        self.vectorization_engine = VectorizationEngine()
        self.demand_engine = DemandVectorizationEngine()
        self.matching_engine = VectorMatchingEngine()
        self.radar_generator = DynamicRadarChartGenerator()
        
        # 缓存向量化结果
        self._phone_vectors_cache = {}
    
    def recommend(self, phones: List[PhoneSpec], user_input: str, 
                 top_n: int = 5, generate_charts: bool = True) -> Dict[str, Any]:
        """完整的推荐流程"""
        print("🚀 开始新的推荐流程...")
        
        # 1. 向量化用户需求（包含预算信息）
        print("🎯 分析用户需求...")
        demand_vector, budget_info = self.demand_engine.vectorize_demand(user_input)
        
        # 显示需求分析结果
        demand_summary = self.demand_engine.get_demand_summary(demand_vector)
        print(f"需求分析: {demand_summary}")
        print(f"关注维度: {demand_vector.focus_dimensions}")
        
        # 显示预算信息
        if budget_info.get('has_budget'):
            if budget_info.get('target_price'):
                print(f"预算分析: 目标价格 ¥{budget_info['target_price']}，容差 {budget_info['tolerance']:.1%}")
            else:
                print(f"预算分析: ¥{budget_info['min_budget']} - ¥{budget_info['max_budget']}")
        else:
            print("预算分析: 未指定具体预算")
        
        # 2. 向量化所有手机（传入预算信息）
        print("📊 向量化手机参数...")
        phones_with_vectors = self._vectorize_phones(phones, budget_info)
        
        # 3. 计算匹配分数并排名
        print("🔍 计算匹配分数...")
        ranked_phones = self.matching_engine.rank_phones_by_demand(
            phones_with_vectors, demand_vector
        )
        
        # 4. 生成推荐理由
        print("💡 生成推荐理由...")
        for rec in ranked_phones[:top_n]:
            reasons = self.matching_engine.get_recommendation_reasons(
                rec['phone_vector'], demand_vector
            )
            rec['reasons'] = reasons
        
        # 5. 生成图表（如果需要）
        chart_paths = {}
        if generate_charts and ranked_phones:
            print("📈 生成可视化图表...")
            chart_paths = self.radar_generator.generate_all_charts(
                ranked_phones, demand_vector
            )
        
        # 6. 构建返回结果
        result = {
            'recommendations': ranked_phones[:top_n],
            'demand_analysis': {
                'summary': demand_summary,
                'focus_dimensions': demand_vector.focus_dimensions,
                'demand_vector': demand_vector.to_dict(),
                'budget_info': budget_info
            },
            'chart_paths': chart_paths,
            'total_phones_analyzed': len(phones),
            'matching_statistics': self._get_matching_statistics(ranked_phones)
        }
        
        print(f"✅ 推荐完成！分析了 {len(phones)} 款手机，推荐 {len(result['recommendations'])} 款")
        return result
    
    def _vectorize_phones(self, phones: List[PhoneSpec], budget_info: Dict = None) -> List[Tuple[PhoneSpec, PhonePerformanceVector]]:
        """向量化手机列表（支持预算信息）"""
        phones_with_vectors = []
        
        for phone in phones:
            # 检查缓存（考虑预算信息）
            if budget_info and budget_info.get('has_budget'):
                phone_key = f"{phone.name}_{phone.cpu}_{phone.price}_budget_{budget_info.get('target_price', 0)}"
            else:
                phone_key = f"{phone.name}_{phone.cpu}_{phone.price}"
            
            if phone_key in self._phone_vectors_cache:
                phone_vector = self._phone_vectors_cache[phone_key]
            else:
                phone_vector = self.vectorization_engine.vectorize_phone(phone, budget_info)
                self._phone_vectors_cache[phone_key] = phone_vector
            
            phones_with_vectors.append((phone, phone_vector))
        
        return phones_with_vectors
    
    def _get_matching_statistics(self, ranked_phones: List[Dict]) -> Dict[str, Any]:
        """获取匹配统计信息"""
        if not ranked_phones:
            return {}
        
        scores = [rec['match_score'] for rec in ranked_phones]
        
        return {
            'total_recommendations': len(ranked_phones),
            'average_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'score_distribution': {
                'excellent': len([s for s in scores if s >= 0.8]),
                'good': len([s for s in scores if 0.6 <= s < 0.8]),
                'fair': len([s for s in scores if 0.4 <= s < 0.6]),
                'poor': len([s for s in scores if s < 0.4])
            }
        }
    
    def get_detailed_analysis(self, phone: PhoneSpec, user_input: str) -> Dict[str, Any]:
        """获取单个手机的详细分析"""
        # 向量化手机
        phone_vector = self.vectorization_engine.vectorize_phone(phone)
        
        # 向量化需求
        demand_vector, budget_info = self.demand_engine.vectorize_demand(user_input)
        
        # 计算匹配分数
        match_score = self.matching_engine.calculate_match_score(phone_vector, demand_vector)
        
        # 获取详细匹配分析
        detailed_analysis = self.matching_engine.get_detailed_match_analysis(
            phone_vector, demand_vector
        )
        
        return {
            'phone': phone,
            'phone_vector': phone_vector.to_dict(),
            'demand_vector': demand_vector.to_dict(),
            'match_score': match_score,
            'detailed_analysis': detailed_analysis,
            'budget_info': budget_info
        }
    
    def find_similar_phones(self, target_phone: PhoneSpec, 
                          all_phones: List[PhoneSpec],
                          similarity_threshold: float = 0.7) -> List[Dict]:
        """查找相似的手机"""
        # 向量化目标手机
        target_vector = self.vectorization_engine.vectorize_phone(target_phone)
        
        # 向量化所有手机
        phones_with_vectors = self._vectorize_phones(all_phones)
        
        # 查找相似手机
        similar_phones = self.matching_engine.find_similar_phones(
            target_vector, phones_with_vectors, similarity_threshold
        )
        
        return similar_phones
    
    def compare_phones(self, phone1: PhoneSpec, phone2: PhoneSpec, 
                      user_input: str = "") -> Dict[str, Any]:
        """比较两款手机"""
        # 向量化手机
        vector1 = self.vectorization_engine.vectorize_phone(phone1)
        vector2 = self.vectorization_engine.vectorize_phone(phone2)
        
        # 计算相似度
        similarity = self.matching_engine.calculate_similarity_score(vector1, vector2)
        
        # 如果有用户需求，计算匹配分数
        match_scores = {}
        if user_input:
            demand_vector = self.demand_engine.vectorize_demand(user_input)
            match_scores['phone1'] = self.matching_engine.calculate_match_score(vector1, demand_vector)
            match_scores['phone2'] = self.matching_engine.calculate_match_score(vector2, demand_vector)
        
        # 生成对比图表
        chart_paths = {}
        if user_input:
            recommendations = [
                {'phone': phone1, 'phone_vector': vector1, 'match_score': match_scores.get('phone1', 0)},
                {'phone': phone2, 'phone_vector': vector2, 'match_score': match_scores.get('phone2', 0)}
            ]
            chart_paths = self.radar_generator.generate_all_charts(
                recommendations, demand_vector
            )
        
        return {
            'phone1': {
                'phone': phone1,
                'vector': vector1.to_dict(),
                'match_score': match_scores.get('phone1', 0)
            },
            'phone2': {
                'phone': phone2,
                'vector': vector2.to_dict(),
                'match_score': match_scores.get('phone2', 0)
            },
            'similarity_score': similarity,
            'chart_paths': chart_paths
        }
    
    def get_phone_vector(self, phone: PhoneSpec) -> PhonePerformanceVector:
        """获取单个手机的向量"""
        return self.vectorization_engine.vectorize_phone(phone)
    
    def get_demand_vector(self, user_input: str) -> UserDemandVector:
        """获取用户需求向量"""
        demand_vector, _ = self.demand_engine.vectorize_demand(user_input)
        return demand_vector
    
    def clear_cache(self):
        """清除向量化缓存"""
        self._phone_vectors_cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            'cached_phones': len(self._phone_vectors_cache),
            'cache_keys': list(self._phone_vectors_cache.keys())
        } 