#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手机性能向量化引擎
将手机硬件参数转换为标准化的性能向量
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from database.sample_data import PhoneSpec


@dataclass
class PhonePerformanceVector:
    """手机性能向量"""
    # 基础性能维度（20个固定维度）
    cpu_performance: float = 0.0      # CPU性能
    memory_capacity: float = 0.0      # 内存容量
    storage_speed: float = 0.0        # 存储速度
    gpu_performance: float = 0.0      # GPU性能
    camera_quality: float = 0.0       # 拍照质量
    camera_features: float = 0.0      # 拍照功能
    battery_capacity: float = 0.0     # 电池容量
    charging_speed: float = 0.0       # 充电速度
    screen_quality: float = 0.0       # 屏幕质量
    screen_size: float = 0.0          # 屏幕尺寸
    weight_portability: float = 0.0   # 重量便携性
    size_portability: float = 0.0     # 尺寸便携性
    build_quality: float = 0.0        # 做工质量
    design_appeal: float = 0.0        # 设计吸引力
    price_value: float = 0.0          # 价格价值
    heat_control: float = 0.0         # 散热控制
    network_stability: float = 0.0    # 网络稳定性
    software_optimization: float = 0.0 # 软件优化
    durability: float = 0.0           # 耐用性
    
    def to_dict(self) -> Dict[str, float]:
        """转换为字典格式"""
        return {
            'cpu_performance': self.cpu_performance,
            'memory_capacity': self.memory_capacity,
            'storage_speed': self.storage_speed,
            'gpu_performance': self.gpu_performance,
            'camera_quality': self.camera_quality,
            'camera_features': self.camera_features,
            'battery_capacity': self.battery_capacity,
            'charging_speed': self.charging_speed,
            'screen_quality': self.screen_quality,
            'screen_size': self.screen_size,
            'weight_portability': self.weight_portability,
            'size_portability': self.size_portability,
            'build_quality': self.build_quality,
            'design_appeal': self.design_appeal,
            'price_value': self.price_value,
            'heat_control': self.heat_control,
            'network_stability': self.network_stability,
            'software_optimization': self.software_optimization,
            'durability': self.durability
        }


class VectorizationEngine:
    """向量化引擎"""
    
    def __init__(self):
        # CPU性能评分规则
        self.cpu_scores = {
            # Apple A系列
            'A17 Pro': 95, 'A16': 90, 'A15': 85, 'A14': 80, 'A13': 75,
            # 高通骁龙系列
            'Snapdragon 8 Gen 3': 92, 'Snapdragon 8 Gen 2': 88, 'Snapdragon 8 Gen 1': 85,
            'Snapdragon 7+ Gen 2': 80, 'Snapdragon 7 Gen 2': 75, 'Snapdragon 6 Gen 1': 70,
            # 联发科天玑系列
            'Dimensity 9300': 90, 'Dimensity 9200': 85, 'Dimensity 8200': 80,
            'Dimensity 7200': 75, 'Dimensity 6100': 70,
            # 其他
            'Kirin 9000': 85, 'Kirin 820': 75, 'Exynos 2200': 85, 'Exynos 2100': 80
        }
        
        # 内存评分规则
        self.memory_scores = {
            4: 60, 6: 70, 8: 80, 12: 90, 16: 95
        }
        
        # 存储评分规则
        self.storage_scores = {
            64: 50, 128: 70, 256: 85, 512: 95, 1024: 100
        }
        
        # 屏幕尺寸评分规则（便携性角度）
        self.screen_size_scores = {
            5.0: 95, 5.5: 90, 6.0: 85, 6.1: 80, 6.3: 75, 6.5: 70, 6.7: 65, 6.8: 60
        }
        
        # 重量评分规则（便携性角度）
        self.weight_scores = {
            150: 95, 160: 90, 170: 85, 180: 80, 190: 75, 200: 70, 210: 65, 220: 60
        }
        
        # 电池容量评分规则
        self.battery_scores = {
            3000: 60, 3500: 70, 4000: 80, 4500: 85, 5000: 90, 5500: 95, 6000: 100
        }
        
        # 摄像头像素评分规则
        self.camera_scores = {
            12: 70, 16: 75, 20: 80, 24: 85, 32: 90, 48: 95, 50: 95, 64: 100, 108: 100
        }
    
    def vectorize_phone(self, phone: PhoneSpec, user_budget: Optional[Dict] = None) -> PhonePerformanceVector:
        """将手机规格转换为性能向量"""
        vector = PhonePerformanceVector()
        
        # CPU性能计算
        vector.cpu_performance = self._calculate_cpu_score(phone.cpu)
        
        # 内存容量计算
        vector.memory_capacity = self._calculate_memory_score(phone.ram_gb)
        
        # 存储速度计算（基于存储容量）
        vector.storage_speed = self._calculate_storage_score(phone.storage_gb)
        
        # GPU性能（通常与CPU相关）
        vector.gpu_performance = vector.cpu_performance * 0.9
        
        # 拍照质量计算
        vector.camera_quality = self._calculate_camera_score(phone.camera_mp)
        
        # 拍照功能（基于摄像头像素和品牌）
        vector.camera_features = self._calculate_camera_features_score(phone)
        
        # 电池容量计算
        vector.battery_capacity = self._calculate_battery_score(phone.battery_mah)
        
        # 充电速度（基于电池容量和品牌）
        vector.charging_speed = self._calculate_charging_speed_score(phone)
        
        # 屏幕质量（基于尺寸和品牌）
        vector.screen_quality = self._calculate_screen_quality_score(phone)
        
        # 屏幕尺寸评分（便携性角度）
        vector.screen_size = self._calculate_screen_size_score(phone.screen_size_inch)
        
        # 重量便携性计算
        vector.weight_portability = self._calculate_weight_score(phone.weight_g)
        
        # 尺寸便携性计算
        vector.size_portability = self._calculate_size_score(phone.screen_size_inch)
        
        # 做工质量（基于品牌和价格）
        vector.build_quality = self._calculate_build_quality_score(phone)
        
        # 设计吸引力（基于品牌和价格）
        vector.design_appeal = self._calculate_design_appeal_score(phone)
        
        # 价格价值计算（传入用户预算信息）
        vector.price_value = self._calculate_price_value_score(phone, user_budget)
        
        # 散热控制（基于CPU和品牌）
        vector.heat_control = self._calculate_heat_control_score(phone)
        
        # 网络稳定性（基于品牌）
        vector.network_stability = self._calculate_network_stability_score(phone)
        
        # 软件优化（基于品牌）
        vector.software_optimization = self._calculate_software_optimization_score(phone)
        
        # 耐用性（基于品牌和做工）
        vector.durability = self._calculate_durability_score(phone)
        
        return vector
    
    def _calculate_cpu_score(self, cpu: str) -> float:
        """CPU性能评分"""
        # 查找精确匹配
        if cpu in self.cpu_scores:
            return self.cpu_scores[cpu] / 100.0
        
        # 模糊匹配
        cpu_lower = cpu.lower()
        for cpu_name, score in self.cpu_scores.items():
            if cpu_name.lower() in cpu_lower or cpu_lower in cpu_name.lower():
                return score / 100.0
        
        # 默认评分
        return 0.7
    
    def _calculate_memory_score(self, ram_gb: int) -> float:
        """内存容量评分"""
        if ram_gb in self.memory_scores:
            return self.memory_scores[ram_gb] / 100.0
        elif ram_gb > 16:
            return 0.95
        elif ram_gb < 4:
            return 0.6
        else:
            return 0.7
    
    def _calculate_storage_score(self, storage_gb: int) -> float:
        """存储速度评分"""
        if storage_gb in self.storage_scores:
            return self.storage_scores[storage_gb] / 100.0
        elif storage_gb > 1024:
            return 1.0
        elif storage_gb < 64:
            return 0.5
        else:
            return 0.7
    
    def _calculate_camera_score(self, camera_mp: int) -> float:
        """摄像头像素评分"""
        if camera_mp in self.camera_scores:
            return self.camera_scores[camera_mp] / 100.0
        elif camera_mp > 108:
            return 1.0
        elif camera_mp < 12:
            return 0.7
        else:
            return 0.8
    
    def _calculate_camera_features_score(self, phone: PhoneSpec) -> float:
        """拍照功能评分"""
        base_score = self._calculate_camera_score(phone.camera_mp)
        
        # 品牌加成
        brand_bonus = 0.0
        if 'iPhone' in phone.name or 'Apple' in phone.name:
            brand_bonus = 0.1
        elif 'Samsung' in phone.name:
            brand_bonus = 0.08
        elif 'Huawei' in phone.name:
            brand_bonus = 0.08
        
        return min(base_score + brand_bonus, 1.0)
    
    def _calculate_battery_score(self, battery_mah: int) -> float:
        """电池容量评分"""
        if battery_mah in self.battery_scores:
            return self.battery_scores[battery_mah] / 100.0
        elif battery_mah > 6000:
            return 1.0
        elif battery_mah < 3000:
            return 0.6
        else:
            return 0.8
    
    def _calculate_charging_speed_score(self, phone: PhoneSpec) -> float:
        """充电速度评分"""
        base_score = 0.7
        
        # 品牌加成
        if 'iPhone' in phone.name:
            base_score = 0.6  # iPhone充电较慢
        elif 'Huawei' in phone.name:
            base_score = 0.85  # 华为快充
        elif 'Xiaomi' in phone.name or 'Redmi' in phone.name:
            base_score = 0.9   # 小米快充
        elif 'OPPO' in phone.name or 'OnePlus' in phone.name:
            base_score = 0.9   # OPPO快充
        
        return base_score
    
    def _calculate_screen_quality_score(self, phone: PhoneSpec) -> float:
        """屏幕质量评分"""
        base_score = 0.8
        
        # 品牌加成
        if 'iPhone' in phone.name:
            base_score = 0.9
        elif 'Samsung' in phone.name:
            base_score = 0.95
        elif 'Huawei' in phone.name:
            base_score = 0.85
        
        return base_score
    
    def _calculate_screen_size_score(self, screen_size: float) -> float:
        """屏幕尺寸评分（便携性角度）"""
        if screen_size in self.screen_size_scores:
            return self.screen_size_scores[screen_size] / 100.0
        elif screen_size > 6.8:
            return 0.6
        elif screen_size < 5.0:
            return 0.95
        else:
            return 0.8
    
    def _calculate_weight_score(self, weight_g: int) -> float:
        """重量便携性评分"""
        if weight_g in self.weight_scores:
            return self.weight_scores[weight_g] / 100.0
        elif weight_g > 220:
            return 0.6
        elif weight_g < 150:
            return 0.95
        else:
            return 0.8
    
    def _calculate_size_score(self, screen_size: float) -> float:
        """尺寸便携性评分"""
        return self._calculate_screen_size_score(screen_size)
    
    def _calculate_build_quality_score(self, phone: PhoneSpec) -> float:
        """做工质量评分"""
        base_score = 0.8
        
        # 品牌加成
        if 'iPhone' in phone.name:
            base_score = 0.95
        elif 'Samsung' in phone.name:
            base_score = 0.9
        elif 'Huawei' in phone.name:
            base_score = 0.85
        
        # 价格加成
        if phone.price > 8000:
            base_score += 0.1
        elif phone.price < 2000:
            base_score -= 0.1
        
        return min(max(base_score, 0.0), 1.0)
    
    def _calculate_design_appeal_score(self, phone: PhoneSpec) -> float:
        """设计吸引力评分"""
        base_score = 0.8
        
        # 品牌加成
        if 'iPhone' in phone.name:
            base_score = 0.9
        elif 'Samsung' in phone.name:
            base_score = 0.85
        elif 'Huawei' in phone.name:
            base_score = 0.8
        
        # 价格加成
        if phone.price > 6000:
            base_score += 0.1
        
        return min(max(base_score, 0.0), 1.0)
    
    def _calculate_price_value_score(self, phone: PhoneSpec, user_budget: Optional[Dict] = None) -> float:
        """价格价值评分 - 基于用户预算的线性匹配"""
        if phone.price <= 0:
            return 0.5
        
        # 如果没有用户预算信息，使用传统的性价比计算
        if not user_budget:
            return self._calculate_traditional_price_score(phone)
        
        # 基于用户预算的线性匹配
        target_price = user_budget.get('target_price', 0)
        min_budget = user_budget.get('min_budget', 0)
        max_budget = user_budget.get('max_budget', 0)
        tolerance = user_budget.get('tolerance', 0.2)  # 默认20%的容差
        
        if target_price > 0:
            # 计算价格匹配度（基于目标价格）
            price_diff = abs(phone.price - target_price)
            price_ratio = price_diff / target_price
            
            if price_ratio <= tolerance:
                # 在容差范围内，匹配度很高
                return 1.0 - (price_ratio / tolerance) * 0.3  # 最高0.7的匹配度
            else:
                # 超出容差范围，匹配度降低
                return max(0.0, 0.7 - (price_ratio - tolerance) * 0.5)
        
        elif min_budget > 0 and max_budget > 0:
            # 基于预算范围的匹配
            if min_budget <= phone.price <= max_budget:
                # 在预算范围内，计算最佳匹配
                budget_center = (min_budget + max_budget) / 2
                price_diff = abs(phone.price - budget_center)
                budget_range = max_budget - min_budget
                
                if budget_range > 0:
                    # 越接近预算中心，匹配度越高
                    match_ratio = 1.0 - (price_diff / (budget_range / 2))
                    return max(0.0, min(1.0, match_ratio))
                else:
                    return 1.0  # 预算范围很小，精确匹配
            else:
                # 超出预算范围
                if phone.price < min_budget:
                    # 价格过低，可能质量不够
                    return max(0.0, 0.5 - (min_budget - phone.price) / min_budget * 0.3)
                else:
                    # 价格过高，超出预算
                    return max(0.0, 0.5 - (phone.price - max_budget) / max_budget * 0.5)
        
        else:
            # 回退到传统计算
            return self._calculate_traditional_price_score(phone)
    
    def _calculate_traditional_price_score(self, phone: PhoneSpec) -> float:
        """传统的性价比评分（作为回退方案）"""
        # 计算综合性能分数
        performance_score = (
            self._calculate_cpu_score(phone.cpu) * 0.3 +
            self._calculate_memory_score(phone.ram_gb) * 0.2 +
            self._calculate_camera_score(phone.camera_mp) * 0.2 +
            self._calculate_battery_score(phone.battery_mah) * 0.15 +
            self._calculate_storage_score(phone.storage_gb) * 0.15
        )
        
        # 性价比 = 性能分数 / 价格（归一化）
        price_normalized = phone.price / 10000  # 假设10000为最高价格
        value_score = performance_score / price_normalized
        
        # 归一化到0-1范围
        return min(max(value_score, 0.0), 1.0)
    
    def _calculate_heat_control_score(self, phone: PhoneSpec) -> float:
        """散热控制评分"""
        base_score = 0.7
        
        # 基于CPU性能调整
        cpu_score = self._calculate_cpu_score(phone.cpu)
        if cpu_score > 0.9:
            base_score -= 0.1  # 高性能CPU散热压力大
        elif cpu_score < 0.7:
            base_score += 0.1  # 低性能CPU散热压力小
        
        # 品牌加成
        if 'iPhone' in phone.name:
            base_score += 0.1  # iPhone散热较好
        elif 'Samsung' in phone.name:
            base_score += 0.05
        
        return min(max(base_score, 0.0), 1.0)
    
    def _calculate_network_stability_score(self, phone: PhoneSpec) -> float:
        """网络稳定性评分"""
        base_score = 0.8
        
        # 品牌加成
        if 'iPhone' in phone.name:
            base_score = 0.9
        elif 'Huawei' in phone.name:
            base_score = 0.85
        elif 'Samsung' in phone.name:
            base_score = 0.8
        
        return base_score
    
    def _calculate_software_optimization_score(self, phone: PhoneSpec) -> float:
        """软件优化评分"""
        base_score = 0.8
        
        # 品牌加成
        if 'iPhone' in phone.name:
            base_score = 0.95  # iOS优化最好
        elif 'Huawei' in phone.name:
            base_score = 0.85
        elif 'Samsung' in phone.name:
            base_score = 0.8
        
        return base_score
    
    def _calculate_durability_score(self, phone: PhoneSpec) -> float:
        """耐用性评分"""
        base_score = 0.8
        
        # 品牌加成
        if 'iPhone' in phone.name:
            base_score = 0.9
        elif 'Samsung' in phone.name:
            base_score = 0.85
        elif 'Huawei' in phone.name:
            base_score = 0.8
        
        # 价格加成
        if phone.price > 6000:
            base_score += 0.1
        
        return min(max(base_score, 0.0), 1.0) 