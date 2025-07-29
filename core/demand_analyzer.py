import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.data_processor import NormalizedPhoneVector

@dataclass
class UserDemand:
    """用户需求结构"""
    # 预算范围
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    
    # 各维度权重 (0-1, 总和为1)
    performance_weight: float = 0.2
    camera_weight: float = 0.2
    battery_weight: float = 0.2
    portability_weight: float = 0.2
    price_weight: float = 0.1
    appearance_weight: float = 0.1
    
    # 特殊偏好
    preferences: List[str] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = []

class DemandParser:
    """需求解析器"""
    
    def __init__(self):
        # 关键词映射
        self.keyword_mapping = {
            # 性能相关
            '性能': ['性能', '速度', '流畅', '快', '处理器', 'cpu', '骁龙', '天玑', '麒麟', '发热'],
            '游戏': ['游戏', '电竞', '王者', '吃鸡', '原神'],
            
            # 拍照相关
            '拍照': ['拍照', '摄影', '相机', '摄像头', '像素', '夜景', '广角', '人像'],
            '影像': ['影像', '视频', '录像', 'vlog'],
            
            # 续航相关
            '续航': ['续航', '电池', '充电', '快充', '无线充电'],
            '省电': ['省电', '节能', '待机'],
            
            # 便携相关
            '轻薄': ['轻薄', '轻', '薄', '便携', '小巧'],
            '大屏': ['大屏', '大屏幕', '屏幕大'],
            '小屏': ['小屏', '小屏幕', '屏幕小'],
            
            # 价格相关
            '便宜': ['便宜', '性价比', '实惠', '经济'],
            '高端': ['高端', '旗舰', '顶级', '豪华'],
            
            # 外观相关
            '颜值': ['颜值', '外观', '好看', '漂亮', '时尚'],
            '品牌': ['品牌', '苹果', '华为', '小米', 'oppo', 'vivo']
        }
        
        # 预算关键词
        self.budget_keywords = ['预算', '价格', '价钱', '元', '块', '千', '万', '以下', '以内', '以上', '高于', '低于']
        
        # 优先级关键词
        self.priority_keywords = ['优先', '重要', '主要', '重点', '最']
    
    def extract_budget(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """提取预算范围"""
        # 匹配价格范围，如"3000-4000元"、"3000到4000"
        price_patterns = [
            r'(\d+)[-~到](\d+)[元块千]*',
            r'预算.*?(\d+)[-~到](\d+)[元块千]*',
            r'(\d+)千[-~到](\d+)千[元块]*',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            if matches:
                min_val, max_val = matches[0]
                min_val = int(min_val)
                max_val = int(max_val)
                
                # 处理"千"单位
                if '千' in text and min_val < 1000:
                    min_val *= 1000
                    max_val *= 1000
                
                return min_val, max_val
        
        # 新增：匹配 "XXXX以下" 或 "低于XXXX"
        under_patterns = [
            r'(\d+)[元块千]*[以内下]',
            r'低于(\d+)[元块千]*',
        ]
        for pattern in under_patterns:
            matches = re.findall(pattern, text)
            if matches:
                max_val = int(matches[0])
                if '千' in text and max_val < 1000:
                    max_val *= 1000
                return 0, max_val

        # 新增：匹配 "XXXX以上" 或 "高于XXXX"
        over_patterns = [
            r'(\d+)[元块千]*[以上外]',
            r'高于(\d+)[元块千]*',
        ]
        for pattern in over_patterns:
            matches = re.findall(pattern, text)
            if matches:
                min_val = int(matches[0])
                if '千' in text and min_val < 1000:
                    min_val *= 1000
                return min_val, 99999  # 设一个较大的上限

        # 匹配单个价格，如"3000元左右", "一万"
        single_patterns = [
            r'(\d+)[元块千]*左右',
            r'预算.*?(\d+)[元块千]*',
        ]
        
        for pattern in single_patterns:
            matches = re.findall(pattern, text)
            if matches:
                price = int(matches[0])
                if '千' in text and price < 1000:
                    price *= 1000
                return price * 0.8, price * 1.2
        
        return None, None
    
    def extract_preferences(self, text: str) -> List[str]:
        """提取用户偏好"""
        preferences = []
        
        for category, keywords in self.keyword_mapping.items():
            for keyword in keywords:
                if keyword in text:
                    preferences.append(category)
                    break
        
        return list(set(preferences))  # 去重
    
    def calculate_weights(self, preferences: List[str], text: str) -> Dict[str, float]:
        """根据偏好计算权重"""
        # 基础权重
        base_weights = {
            'performance': 0.2,
            'camera': 0.2,
            'battery': 0.2,
            'portability': 0.2,
            'price': 0.1,
            'appearance': 0.1
        }
        
        # 偏好权重调整
        preference_weights = {
            '性能': {'performance': 0.4, 'camera': 0.1, 'battery': 0.1, 'portability': 0.1, 'price': 0.1, 'appearance': 0.1},
            '游戏': {'performance': 0.5, 'battery': 0.2, 'camera': 0.1, 'portability': 0.1, 'price': 0.05, 'appearance': 0.05},
            '拍照': {'camera': 0.5, 'performance': 0.1, 'battery': 0.1, 'portability': 0.1, 'price': 0.1, 'appearance': 0.1},
            '影像': {'camera': 0.4, 'performance': 0.2, 'battery': 0.2, 'portability': 0.1, 'price': 0.05, 'appearance': 0.05},
            '续航': {'battery': 0.5, 'performance': 0.1, 'camera': 0.1, 'portability': 0.1, 'price': 0.1, 'appearance': 0.1},
            '省电': {'battery': 0.4, 'performance': 0.1, 'camera': 0.1, 'portability': 0.2, 'price': 0.1, 'appearance': 0.1},
            '轻薄': {'portability': 0.5, 'performance': 0.1, 'camera': 0.1, 'battery': 0.1, 'price': 0.1, 'appearance': 0.1},
            '大屏': {'portability': 0.3, 'camera': 0.2, 'battery': 0.2, 'performance': 0.1, 'price': 0.1, 'appearance': 0.1},
            '小屏': {'portability': 0.4, 'performance': 0.2, 'battery': 0.2, 'camera': 0.1, 'price': 0.05, 'appearance': 0.05},
            '便宜': {'price': 0.4, 'performance': 0.1, 'camera': 0.1, 'battery': 0.1, 'portability': 0.1, 'appearance': 0.2},
            '高端': {'appearance': 0.4, 'performance': 0.2, 'camera': 0.2, 'battery': 0.1, 'portability': 0.05, 'price': 0.05},
            '颜值': {'appearance': 0.5, 'portability': 0.2, 'camera': 0.1, 'performance': 0.1, 'battery': 0.05, 'price': 0.05},
            '品牌': {'appearance': 0.4, 'performance': 0.2, 'camera': 0.2, 'battery': 0.1, 'portability': 0.05, 'price': 0.05}
        }
        
        # 检查是否有优先级关键词
        has_priority = any(keyword in text for keyword in self.priority_keywords)
        
        if has_priority and preferences:
            # 有优先级时，使用偏好权重
            main_preference = preferences[0]
            if main_preference in preference_weights:
                return preference_weights[main_preference]
        
        # 无优先级时，根据偏好调整基础权重
        if preferences:
            adjusted_weights = base_weights.copy()
            for preference in preferences:
                if preference in preference_weights:
                    for key, value in preference_weights[preference].items():
                        adjusted_weights[key] = max(adjusted_weights[key], value)
            
            # 重新归一化权重
            total = sum(adjusted_weights.values())
            return {key: value / total for key, value in adjusted_weights.items()}
        
        return base_weights
    
    def parse_demand(self, text: str) -> UserDemand:
        """解析用户需求"""
        text = text.lower()
        
        # 提取预算
        budget_min, budget_max = self.extract_budget(text)
        
        # 提取偏好
        preferences = self.extract_preferences(text)
        
        # 计算权重
        weights = self.calculate_weights(preferences, text)
        
        return UserDemand(
            budget_min=budget_min,
            budget_max=budget_max,
            performance_weight=weights['performance'],
            camera_weight=weights['camera'],
            battery_weight=weights['battery'],
            portability_weight=weights['portability'],
            price_weight=weights['price'],
            appearance_weight=weights['appearance'],
            preferences=preferences
        )
    
    def demand_to_vector(self, demand: UserDemand) -> List[float]:
        """将需求转换为向量"""
        return [
            demand.performance_weight,
            demand.camera_weight,
            demand.battery_weight,
            demand.portability_weight,
            demand.price_weight,
            demand.appearance_weight
        ] 