import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass
from core.data_processor import NormalizedPhoneVector
from core.demand_analyzer import UserDemand

@dataclass
class RecommendationResult:
    """推荐结果"""
    phone: NormalizedPhoneVector
    similarity_score: float
    rank: int
    match_reasons: List[str]

class RecommendationEngine:
    """推荐引擎"""
    
    def __init__(self):
        self.similarity_methods = {
            'euclidean': self._euclidean_similarity,
            'cosine': self._cosine_similarity,
            'weighted_euclidean': self._weighted_euclidean_similarity
        }
    
    def _euclidean_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """欧氏距离相似度"""
        distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))
        # 转换为相似度 (距离越小，相似度越高)
        return 1 / (1 + distance)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = np.sqrt(sum(a ** 2 for a in vec1))
        norm2 = np.sqrt(sum(b ** 2 for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)
    
    def _weighted_euclidean_similarity(self, vec1: List[float], vec2: List[float], weights: List[float]) -> float:
        """加权欧氏距离相似度"""
        weighted_distance = np.sqrt(sum(w * (a - b) ** 2 for a, b, w in zip(vec1, vec2, weights)))
        return 1 / (1 + weighted_distance)
    
    def _filter_by_budget(self, phones: List[NormalizedPhoneVector], demand: UserDemand) -> List[NormalizedPhoneVector]:
        """根据预算过滤手机"""
        if demand.budget_min is None and demand.budget_max is None:
            return phones
        
        filtered_phones = []
        for phone in phones:
            price = phone.original_data['price']
            
            # 检查价格是否在预算范围内
            if demand.budget_min is not None and price < demand.budget_min:
                continue
            if demand.budget_max is not None and price > demand.budget_max:
                continue
            
            filtered_phones.append(phone)
        
        return filtered_phones
    
    def _calculate_similarity(self, demand_vector: List[float], phone_vector: List[float], 
                            demand: UserDemand, method: str = 'weighted_euclidean') -> float:
        """计算相似度"""
        if method == 'weighted_euclidean':
            # 使用需求权重作为相似度计算的权重
            weights = [
                demand.performance_weight,
                demand.camera_weight,
                demand.battery_weight,
                demand.portability_weight,
                demand.price_weight,
                demand.appearance_weight
            ]
            return self._weighted_euclidean_similarity(demand_vector, phone_vector, weights)
        else:
            return self.similarity_methods[method](demand_vector, phone_vector)
    
    def _generate_match_reasons(self, demand: UserDemand, phone: NormalizedPhoneVector) -> List[str]:
        """生成匹配原因"""
        reasons = []
        
        # 检查各维度是否匹配用户偏好
        if demand.performance_weight > 0.3 and phone.performance_score > 0.7:
            reasons.append("性能强劲")
        
        if demand.camera_weight > 0.3 and phone.camera_score > 0.7:
            reasons.append("拍照优秀")
        
        if demand.battery_weight > 0.3 and phone.battery_score > 0.7:
            reasons.append("续航持久")
        
        if demand.portability_weight > 0.3 and phone.portability_score > 0.7:
            reasons.append("便携轻巧")
        
        if demand.price_weight > 0.3 and phone.price_score > 0.7:
            reasons.append("性价比高")
        
        if demand.appearance_weight > 0.3 and phone.appearance_score > 0.7:
            reasons.append("外观精美")
        
        # 检查预算匹配
        if demand.budget_min and demand.budget_max:
            price = phone.original_data['price']
            if demand.budget_min <= price <= demand.budget_max:
                reasons.append("预算合适")
        
        # 检查特殊偏好
        for preference in demand.preferences:
            if preference == '轻薄' and phone.portability_score > 0.8:
                reasons.append("轻薄便携")
            elif preference == '拍照' and phone.camera_score > 0.8:
                reasons.append("拍照出色")
            elif preference == '续航' and phone.battery_score > 0.8:
                reasons.append("续航强劲")
            elif preference == '性能' and phone.performance_score > 0.8:
                reasons.append("性能卓越")
        
        return reasons if reasons else ["综合表现良好"]
    
    def _apply_sorting_factors(self, results: List[RecommendationResult]) -> List[RecommendationResult]:
        """应用排序因子（销量、好评度等）"""
        for result in results:
            phone = result.phone
            original_data = phone.original_data
            
            # 计算综合评分
            rating_factor = original_data['rating'] / 5.0  # 评分因子
            sales_factor = min(original_data['sales'] / 10000, 1.0)  # 销量因子
            
            # 调整相似度分数
            result.similarity_score *= (0.7 + 0.2 * rating_factor + 0.1 * sales_factor)
        
        # 重新排序
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # 更新排名
        for i, result in enumerate(results):
            result.rank = i + 1
        
        return results
    
    def recommend(self, phones: List[NormalizedPhoneVector], demand: UserDemand, 
                 top_n: int = 5, method: str = 'weighted_euclidean') -> List[RecommendationResult]:
        """推荐算法主函数"""
        
        # 1. 预算过滤
        filtered_phones = self._filter_by_budget(phones, demand)
        
        if not filtered_phones:
            return []
        
        # 2. 将需求转换为向量
        demand_vector = [
            demand.performance_weight,
            demand.camera_weight,
            demand.battery_weight,
            demand.portability_weight,
            demand.price_weight,
            demand.appearance_weight
        ]
        
        # 3. 计算相似度
        results = []
        for phone in filtered_phones:
            phone_vector = [
                phone.performance_score,
                phone.camera_score,
                phone.battery_score,
                phone.portability_score,
                phone.price_score,
                phone.appearance_score
            ]
            
            similarity = self._calculate_similarity(demand_vector, phone_vector, demand, method)
            match_reasons = self._generate_match_reasons(demand, phone)
            
            results.append(RecommendationResult(
                phone=phone,
                similarity_score=similarity,
                rank=0,
                match_reasons=match_reasons
            ))
        
        # 4. 应用排序因子
        results = self._apply_sorting_factors(results)
        
        # 5. 返回Top N结果
        return results[:top_n]
    
    def get_recommendation_summary(self, results: List[RecommendationResult]) -> Dict:
        """获取推荐结果摘要"""
        if not results:
            return {"message": "未找到符合条件的手机"}
        
        summary = {
            "total_recommendations": len(results),
            "top_recommendation": {
                "name": results[0].phone.name,
                "score": round(results[0].similarity_score, 3),
                "price": results[0].phone.original_data['price'],
                "reasons": results[0].match_reasons
            },
            "all_recommendations": []
        }
        
        for result in results:
            summary["all_recommendations"].append({
                "rank": result.rank,
                "name": result.phone.name,
                "score": round(result.similarity_score, 3),
                "price": result.phone.original_data['price'],
                "reasons": result.match_reasons
            })
        
        return summary 