import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class NormalizedPhoneVector:
    """归一化后的手机参数向量"""
    name: str
    # 性能维度 (0-1)
    performance_score: float  # CPU + RAM + 存储的综合评分
    # 影像维度 (0-1) 
    camera_score: float       # 摄像头像素评分
    # 续航维度 (0-1)
    battery_score: float      # 电池容量评分
    # 便携维度 (0-1)
    portability_score: float  # 重量和屏幕尺寸的综合评分
    # 价格维度 (0-1, 越小越便宜)
    price_score: float        # 价格归一化(0-1)
    # 外观维度 (0-1)
    appearance_score: float   # 评分和销量的综合
    # 原始数据
    original_data: dict

class PhoneNormalizer:
    """手机参数归一化处理器"""
    
    def __init__(self):
        # 定义各参数的取值范围(用于归一化)
        self.param_ranges = {
            'ram_gb': (4, 16),      # 内存范围
            'storage_gb': (64, 1024), # 存储范围
            'screen_size_inch': (5.0, 7.0), # 屏幕尺寸范围
            'camera_mp': (8, 200),   # 摄像头像素范围
            'battery_mah': (2000, 6000), # 电池容量范围
            'weight_g': (120, 250),  # 重量范围
            'price': (1000, 15000),  # 价格范围
            'rating': (3.0, 5.0),    # 评分范围
            'sales': (1000, 50000)   # 销量范围
        }
        
        # CPU性能评分映射
        self.cpu_scores = {
            '骁龙8 Gen2': 0.95, '骁龙8+ Gen1': 0.90, '骁龙8 Gen1': 0.85,
            '骁龙7+ Gen2': 0.80, '骁龙7 Gen1': 0.75, '骁龙6 Gen1': 0.70,
            'A16': 0.98, 'A15': 0.95, 'A14': 0.90, 'A13': 0.85,
            '天玑9200': 0.93, '天玑9000': 0.88, '天玑8200': 0.83,
            '麒麟9000': 0.87, '麒麟990': 0.82
        }
    
    def normalize_value(self, value: float, param_name: str) -> float:
        """归一化单个数值到0-1区间"""
        min_val, max_val = self.param_ranges[param_name]
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)
    
    def get_cpu_score(self, cpu_name: str) -> float:
        """获取CPU性能评分"""
        return self.cpu_scores.get(cpu_name, 0.7)  # 默认0.7
    
    def calculate_performance_score(self, phone) -> float:
        """计算综合性能评分"""
        cpu_score = self.get_cpu_score(phone.cpu)
        ram_score = self.normalize_value(phone.ram_gb, 'ram_gb')
        storage_score = self.normalize_value(phone.storage_gb, 'storage_gb')
        
        # 权重分配: CPU 50%, RAM 30%, 存储 20%
        return cpu_score * 0.5 + ram_score * 0.3 + storage_score * 0.2
    
    def calculate_camera_score(self, phone) -> float:
        """计算摄像头评分"""
        return self.normalize_value(phone.camera_mp, 'camera_mp')
    
    def calculate_battery_score(self, phone) -> float:
        """计算电池续航评分"""
        return self.normalize_value(phone.battery_mah, 'battery_mah')
    
    def calculate_portability_score(self, phone) -> float:
        """计算便携性评分(重量轻、屏幕适中为优)"""
        # 重量越小越好，屏幕尺寸适中最好
        weight_score = 1 - self.normalize_value(phone.weight_g, 'weight_g')  # 重量越小越好
        screen_score = 1 - abs(self.normalize_value(phone.screen_size_inch, 'screen_size_inch') - 0.5)  # 屏幕适中最好
        
        return (weight_score * 0.6 + screen_score * 0.4)
    
    def calculate_price_score(self, phone) -> float:
        """计算价格评分(价格越低越好)"""
        return 1 - self.normalize_value(phone.price, 'price')  # 价格越低越好
    
    def calculate_appearance_score(self, phone) -> float:
        """计算外观/品牌评分"""
        rating_score = self.normalize_value(phone.rating, 'rating')
        sales_score = self.normalize_value(phone.sales, 'sales')
        
        return (rating_score * 0.7 + sales_score * 0.3)
    
    def normalize_phone(self, phone) -> NormalizedPhoneVector:
        """将手机参数归一化为向量"""
        return NormalizedPhoneVector(
            name=phone.name,
            performance_score=self.calculate_performance_score(phone),
            camera_score=self.calculate_camera_score(phone),
            battery_score=self.calculate_battery_score(phone),
            portability_score=self.calculate_portability_score(phone),
            price_score=self.calculate_price_score(phone),
            appearance_score=self.calculate_appearance_score(phone),
            original_data={
                'cpu': phone.cpu,
                'ram_gb': phone.ram_gb,
                'storage_gb': phone.storage_gb,
                'screen_size_inch': phone.screen_size_inch,
                'camera_mp': phone.camera_mp,
                'battery_mah': phone.battery_mah,
                'weight_g': phone.weight_g,
                'price': phone.price,
                'rating': phone.rating,
                'sales': phone.sales,
                'highlights': phone.highlights
            }
        )
    
    def get_vector(self, normalized_phone: NormalizedPhoneVector) -> List[float]:
        """获取归一化向量"""
        return [
            normalized_phone.performance_score,
            normalized_phone.camera_score,
            normalized_phone.battery_score,
            normalized_phone.portability_score,
            normalized_phone.price_score,
            normalized_phone.appearance_score
        ] 