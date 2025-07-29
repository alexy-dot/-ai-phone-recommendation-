#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户需求向量化引擎
将用户输入转换为标准化的需求向量
"""

import re
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class UserDemandVector:
    """用户需求向量"""
    # 与手机性能向量对应的需求权重（20个维度）
    cpu_performance: float = 0.0      # 用户对CPU性能的需求权重
    memory_capacity: float = 0.0      # 用户对内存的需求权重
    storage_speed: float = 0.0        # 用户对存储速度的需求权重
    gpu_performance: float = 0.0      # 用户对GPU性能的需求权重
    camera_quality: float = 0.0       # 用户对拍照质量的需求权重
    camera_features: float = 0.0      # 用户对拍照功能的需求权重
    battery_capacity: float = 0.0     # 用户对电池容量的需求权重
    charging_speed: float = 0.0       # 用户对充电速度的需求权重
    screen_quality: float = 0.0       # 用户对屏幕质量的需求权重
    screen_size: float = 0.0          # 用户对屏幕尺寸的需求权重
    weight_portability: float = 0.0   # 用户对重量便携性的需求权重
    size_portability: float = 0.0     # 用户对尺寸便携性的需求权重
    build_quality: float = 0.0        # 用户对做工质量的需求权重
    design_appeal: float = 0.0        # 用户对设计的需求权重
    price_value: float = 0.0          # 用户对价格价值的需求权重
    heat_control: float = 0.0         # 用户对散热控制的需求权重
    network_stability: float = 0.0    # 用户对网络稳定性的需求权重
    software_optimization: float = 0.0 # 用户对软件优化的需求权重
    durability: float = 0.0           # 用户对耐用性的需求权重
    
    # 用户关注的维度（用于雷达图）
    focus_dimensions: List[str] = None
    
    def __post_init__(self):
        if self.focus_dimensions is None:
            self.focus_dimensions = []
    
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


class DemandVectorizationEngine:
    """需求向量化引擎"""
    
    def __init__(self):
        # 关键词匹配规则
        self.keyword_mapping = {
            'cpu_performance': {
                'keywords': ['性能', '处理器', 'CPU', '游戏', '流畅', '快', '速度', '运行'],
                'weight_increment': 0.3
            },
            'memory_capacity': {
                'keywords': ['内存', 'RAM', '运行内存', '存储', '空间'],
                'weight_increment': 0.25
            },
            'storage_speed': {
                'keywords': ['存储', '空间', '容量', '速度', '快'],
                'weight_increment': 0.25
            },
            'gpu_performance': {
                'keywords': ['游戏', '显卡', 'GPU', '图形', '画质'],
                'weight_increment': 0.3
            },
            'camera_quality': {
                'keywords': ['拍照', '摄影', '相机', '像素', '清晰', '画质', '照片'],
                'weight_increment': 0.35
            },
            'camera_features': {
                'keywords': ['拍照', '摄影', '相机', '功能', '夜景', '人像', '广角'],
                'weight_increment': 0.3
            },
            'battery_capacity': {
                'keywords': ['续航', '电池', '持久', '充电', '电量', '待机'],
                'weight_increment': 0.35
            },
            'charging_speed': {
                'keywords': ['充电', '快充', '充电速度', '充电器', '无线充电'],
                'weight_increment': 0.3
            },
            'screen_quality': {
                'keywords': ['屏幕', '显示', '色彩', '分辨率', '画质', '清晰'],
                'weight_increment': 0.3
            },
            'screen_size': {
                'keywords': ['屏幕', '尺寸', '大小', '显示'],
                'weight_increment': 0.25
            },
            'weight_portability': {
                'keywords': ['轻薄', '便携', '重量', '携带', '轻', '重'],
                'weight_increment': 0.35
            },
            'size_portability': {
                'keywords': ['轻薄', '便携', '尺寸', '大小', '携带'],
                'weight_increment': 0.3
            },
            'build_quality': {
                'keywords': ['做工', '质量', '耐用', '坚固', '材质', '手感'],
                'weight_increment': 0.3
            },
            'design_appeal': {
                'keywords': ['外观', '设计', '颜值', '好看', '漂亮', '时尚'],
                'weight_increment': 0.3
            },
            'price_value': {
                'keywords': ['性价比', '便宜', '实惠', '预算', '价格', '贵', '便宜'],
                'weight_increment': 0.4
            },
            'heat_control': {
                'keywords': ['散热', '发热', '温度', '冷却'],
                'weight_increment': 0.25
            },
            'network_stability': {
                'keywords': ['网络', '信号', '稳定', '连接', '5G', '4G'],
                'weight_increment': 0.25
            },
            'software_optimization': {
                'keywords': ['系统', '软件', '优化', '流畅', '卡顿', '体验'],
                'weight_increment': 0.3
            },
            'durability': {
                'keywords': ['耐用', '质量', '坚固', '寿命', '长期'],
                'weight_increment': 0.25
            }
        }
        
        # 特殊需求模式
        self.special_patterns = {
            'gaming': {
                'keywords': ['游戏', '电竞', '王者', '吃鸡', '手游'],
                'dimensions': {
                    'cpu_performance': 0.8,
                    'gpu_performance': 0.8,
                    'memory_capacity': 0.6,
                    'heat_control': 0.7,
                    'battery_capacity': 0.6
                }
            },
            'photography': {
                'keywords': ['拍照', '摄影', '相机', '照片', '摄影'],
                'dimensions': {
                    'camera_quality': 0.9,
                    'camera_features': 0.9,
                    'screen_quality': 0.7,
                    'storage_speed': 0.6
                }
            },
            'business': {
                'keywords': ['商务', '办公', '工作', '会议', '邮件'],
                'dimensions': {
                    'battery_capacity': 0.8,
                    'network_stability': 0.8,
                    'software_optimization': 0.7,
                    'durability': 0.7
                }
            },
            'portable': {
                'keywords': ['轻薄', '便携', '携带', '轻便', '小巧'],
                'dimensions': {
                    'weight_portability': 0.9,
                    'size_portability': 0.9,
                    'battery_capacity': 0.6
                }
            },
            'budget': {
                'keywords': ['便宜', '实惠', '性价比', '预算', '经济'],
                'dimensions': {
                    'price_value': 0.9,
                    'battery_capacity': 0.6,
                    'durability': 0.6
                }
            }
        }
    
    def vectorize_demand(self, user_input: str) -> tuple[UserDemandVector, Dict]:
        """将用户输入转换为需求向量和预算信息"""
        vector = UserDemandVector()
        
        # 转换为小写进行匹配
        input_lower = user_input.lower()
        
        # 1. 关键词匹配
        self._apply_keyword_matching(vector, input_lower)
        
        # 2. 特殊需求模式匹配
        self._apply_special_patterns(vector, input_lower)
        
        # 3. 预算分析
        budget_info = self.extract_budget_info(user_input)
        budget_weight = self._analyze_budget(user_input)
        vector.price_value = max(vector.price_value, budget_weight)
        
        # 4. 确定关注的维度（权重>0.1的维度）
        vector.focus_dimensions = [
            dim for dim, weight in vector.to_dict().items() 
            if weight > 0.1
        ]
        
        # 5. 如果没有关注维度，设置默认维度
        if not vector.focus_dimensions:
            vector.focus_dimensions = ['cpu_performance', 'camera_quality', 
                                     'battery_capacity', 'price_value']
        
        return vector, budget_info
    
    def _apply_keyword_matching(self, vector: UserDemandVector, input_lower: str):
        """应用关键词匹配"""
        for dimension, config in self.keyword_mapping.items():
            weight = 0.0
            for keyword in config['keywords']:
                if keyword in input_lower:
                    weight += config['weight_increment']
            
            # 设置权重，但不超过1.0
            setattr(vector, dimension, min(weight, 1.0))
    
    def _apply_special_patterns(self, vector: UserDemandVector, input_lower: str):
        """应用特殊需求模式"""
        for pattern_name, pattern_config in self.special_patterns.items():
            # 检查是否匹配特殊模式
            pattern_matched = False
            for keyword in pattern_config['keywords']:
                if keyword in input_lower:
                    pattern_matched = True
                    break
            
            if pattern_matched:
                # 应用模式权重
                for dimension, weight in pattern_config['dimensions'].items():
                    current_weight = getattr(vector, dimension)
                    # 取最大值，避免覆盖已有的高权重
                    setattr(vector, dimension, max(current_weight, weight))
    
    def _analyze_budget(self, user_input: str) -> float:
        """分析预算对价格权重的影响"""
        # 预算提取模式
        budget_patterns = [
            r'预算.*?(\d+)[-~](\d+)',  # 预算3000-4000
            r'(\d+)[-~](\d+).*?预算',  # 3000-4000预算
            r'(\d+)[-~](\d+).*?元',    # 3000-4000元
            r'(\d+)[-~](\d+).*?块',    # 3000-4000块
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, user_input)
            if match:
                try:
                    min_budget = int(match.group(1))
                    max_budget = int(match.group(2))
                    avg_budget = (min_budget + max_budget) / 2
                    
                    # 预算越低，价格权重越高
                    if avg_budget < 2000:
                        return 0.9
                    elif avg_budget < 4000:
                        return 0.7
                    elif avg_budget < 6000:
                        return 0.5
                    elif avg_budget < 8000:
                        return 0.3
                    else:
                        return 0.2
                except (ValueError, IndexError):
                    continue
        
        # 如果没有明确预算，检查价格相关词汇
        price_keywords = ['便宜', '实惠', '性价比', '经济', '贵', '便宜']
        if any(keyword in user_input for keyword in price_keywords):
            return 0.6
        
        return 0.5  # 默认权重
    
    def extract_budget_info(self, user_input: str) -> Dict:
        """提取详细的预算信息"""
        budget_info = {
            'target_price': 0,
            'min_budget': 0,
            'max_budget': 0,
            'tolerance': 0.2,  # 默认20%容差
            'has_budget': False
        }
        
        # 1. 精确范围匹配：3000-4000元
        range_patterns = [
            r'(\d+)[-~](\d+).*?元',
            r'(\d+)[-~](\d+).*?块',
            r'预算.*?(\d+)[-~](\d+)',
            r'(\d+)[-~](\d+).*?预算'
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, user_input)
            if match:
                try:
                    min_val = int(match.group(1))
                    max_val = int(match.group(2))
                    budget_info.update({
                        'min_budget': min_val,
                        'max_budget': max_val,
                        'target_price': (min_val + max_val) / 2,
                        'tolerance': (max_val - min_val) / (min_val + max_val) * 2,  # 动态计算容差
                        'has_budget': True
                    })
                    return budget_info
                except (ValueError, IndexError):
                    continue
        
        # 2. 模糊表达匹配：大约3000元、3000元左右
        fuzzy_patterns = [
            r'大约.*?(\d+).*?元',
            r'(\d+).*?左右.*?元',
            r'(\d+).*?元.*?左右',
            r'大概.*?(\d+).*?元',
            r'(\d+).*?上下.*?元'
        ]
        
        for pattern in fuzzy_patterns:
            match = re.search(pattern, user_input)
            if match:
                try:
                    target_price = int(match.group(1))
                    # 根据价格范围设置不同的容差
                    if target_price < 2000:
                        tolerance = 0.15  # 15%容差
                    elif target_price < 5000:
                        tolerance = 0.2   # 20%容差
                    else:
                        tolerance = 0.25  # 25%容差
                    
                    budget_info.update({
                        'target_price': target_price,
                        'min_budget': int(target_price * (1 - tolerance)),
                        'max_budget': int(target_price * (1 + tolerance)),
                        'tolerance': tolerance,
                        'has_budget': True
                    })
                    return budget_info
                except (ValueError, IndexError):
                    continue
        
        # 3. 单一价格匹配：3000元
        single_patterns = [
            r'(\d+).*?元(?!.*?左右|.*?上下)',
            r'价格.*?(\d+)',
            r'(\d+).*?价格'
        ]
        
        for pattern in single_patterns:
            match = re.search(pattern, user_input)
            if match:
                try:
                    target_price = int(match.group(1))
                    tolerance = 0.1  # 单一价格用较小容差
                    
                    budget_info.update({
                        'target_price': target_price,
                        'min_budget': int(target_price * (1 - tolerance)),
                        'max_budget': int(target_price * (1 + tolerance)),
                        'tolerance': tolerance,
                        'has_budget': True
                    })
                    return budget_info
                except (ValueError, IndexError):
                    continue
        
        # 4. 关键词匹配（无具体数字）
        if any(keyword in user_input for keyword in ['便宜', '实惠', '性价比', '经济']):
            budget_info.update({
                'target_price': 3000,  # 默认经济型价格
                'min_budget': 1500,
                'max_budget': 4500,
                'tolerance': 0.5,
                'has_budget': True
            })
        elif any(keyword in user_input for keyword in ['高端', '旗舰', '顶级']):
            budget_info.update({
                'target_price': 8000,  # 默认高端价格
                'min_budget': 6000,
                'max_budget': 12000,
                'tolerance': 0.375,
                'has_budget': True
            })
        
        return budget_info
    
    def get_demand_summary(self, vector: UserDemandVector) -> str:
        """获取需求摘要"""
        focus_dimensions = vector.focus_dimensions
        if not focus_dimensions:
            return "通用需求"
        
        dimension_names = {
            'cpu_performance': '性能',
            'camera_quality': '拍照',
            'battery_capacity': '续航',
            'weight_portability': '便携',
            'price_value': '性价比',
            'screen_quality': '屏幕',
            'build_quality': '做工',
            'design_appeal': '外观',
            'gpu_performance': '游戏',
            'memory_capacity': '内存',
            'storage_speed': '存储',
            'camera_features': '拍照功能',
            'charging_speed': '充电',
            'screen_size': '屏幕尺寸',
            'size_portability': '尺寸便携',
            'heat_control': '散热',
            'network_stability': '网络',
            'software_optimization': '系统',
            'durability': '耐用性'
        }
        
        focus_names = [dimension_names.get(dim, dim) for dim in focus_dimensions]
        return f"重点关注: {', '.join(focus_names)}"
    
    def validate_demand(self, vector: UserDemandVector) -> bool:
        """验证需求向量是否有效"""
        # 检查是否有至少一个关注维度
        if not vector.focus_dimensions:
            return False
        
        # 检查权重是否在合理范围内
        for dimension, weight in vector.to_dict().items():
            if not (0.0 <= weight <= 1.0):
                return False
        
        return True 