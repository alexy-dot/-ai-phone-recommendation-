#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版需求解析器
能够处理所有类型的明确需求，包括数字提取和精确匹配
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SpecificRequirement:
    """具体需求"""
    dimension: str          # 需求维度
    value: float           # 具体数值
    unit: str              # 单位
    tolerance: float       # 容差
    requirement_type: str  # 需求类型：exact(精确), range(范围), minimum(最低), maximum(最高)


@dataclass
class EnhancedDemandAnalysis:
    """增强版需求分析结果"""
    # 向量化权重
    vector_weights: Dict[str, float]
    
    # 具体需求列表
    specific_requirements: List[SpecificRequirement]
    
    # 预算信息
    budget_info: Dict
    
    # 关注维度
    focus_dimensions: List[str]
    
    # 需求摘要
    demand_summary: str


class EnhancedDemandParser:
    """增强版需求解析器"""
    
    def __init__(self):
        # 数字提取模式
        self.number_patterns = {
            'storage': {
                'patterns': [
                    r'(\d+)\s*[Gg][Bb]?\s*存储',
                    r'(\d+)\s*[Gg][Bb]?\s*空间',
                    r'(\d+)\s*[Gg][Bb]?\s*容量',
                    r'存储\s*(\d+)\s*[Gg][Bb]?',
                    r'(\d+)\s*[Gg][Bb]?\s*的手机',
                    r'(\d+)\s*[Gg][Bb]?\s*存储空间'
                ],
                'dimension': 'storage_speed',
                'unit': 'GB',
                'tolerance': 0.0  # 精确匹配
            },
            'memory': {
                'patterns': [
                    r'(\d+)\s*[Gg]\s*内存',
                    r'(\d+)\s*[Gg]\s*RAM',
                    r'(\d+)\s*[Gg]\s*运行内存',
                    r'内存\s*(\d+)\s*[Gg]',
                    r'(\d+)\s*[Gg]\s*内存的手机'
                ],
                'dimension': 'memory_capacity',
                'unit': 'GB',
                'tolerance': 0.0
            },
            'screen_size': {
                'patterns': [
                    r'(\d+\.?\d*)\s*寸\s*屏幕',
                    r'(\d+\.?\d*)\s*英寸\s*屏幕',
                    r'屏幕\s*(\d+\.?\d*)\s*寸',
                    r'(\d+\.?\d*)\s*寸\s*的手机',
                    r'(\d+\.?\d*)\s*英寸\s*的手机'
                ],
                'dimension': 'screen_size',
                'unit': 'inch',
                'tolerance': 0.1  # 0.1寸容差
            },
            'battery': {
                'patterns': [
                    r'(\d+)\s*[Mm][Aa][Hh]\s*电池',
                    r'(\d+)\s*毫安\s*电池',
                    r'电池\s*(\d+)\s*[Mm][Aa][Hh]',
                    r'(\d+)\s*[Mm][Aa][Hh]\s*的手机',
                    r'(\d+)\s*毫安\s*的手机'
                ],
                'dimension': 'battery_capacity',
                'unit': 'mAh',
                'tolerance': 0.05  # 5%容差
            },
            'camera': {
                'patterns': [
                    r'(\d+)\s*[Mm][Pp]\s*摄像头',
                    r'(\d+)\s*[Mm][Pp]\s*相机',
                    r'(\d+)\s*百万像素',
                    r'摄像头\s*(\d+)\s*[Mm][Pp]',
                    r'(\d+)\s*[Mm][Pp]\s*的手机',
                    r'(\d+)\s*[Mm][Pp]\s*拍照'
                ],
                'dimension': 'camera_quality',
                'unit': 'MP',
                'tolerance': 0.1  # 10%容差
            },
            'price': {
                'patterns': [
                    r'(\d+)\s*元\s*左右',
                    r'大约\s*(\d+)\s*元',
                    r'(\d+)\s*元\s*上下',
                    r'价格\s*(\d+)\s*元',
                    r'(\d+)\s*元\s*的手机',
                    r'(\d+)\s*块\s*左右',
                    r'大约\s*(\d+)\s*块'
                ],
                'dimension': 'price_value',
                'unit': 'yuan',
                'tolerance': 0.2  # 20%容差
            }
        }
        
        # 范围提取模式
        self.range_patterns = {
            'price_range': {
                'patterns': [
                    r'(\d+)[-~](\d+)\s*元',
                    r'(\d+)[-~](\d+)\s*块',
                    r'预算\s*(\d+)[-~](\d+)',
                    r'(\d+)[-~](\d+)\s*预算'
                ],
                'dimension': 'price_value',
                'unit': 'yuan'
            },
            'storage_range': {
                'patterns': [
                    r'(\d+)[-~](\d+)\s*[Gg][Bb]?\s*存储',
                    r'存储\s*(\d+)[-~](\d+)\s*[Gg][Bb]?'
                ],
                'dimension': 'storage_speed',
                'unit': 'GB'
            }
        }
        
        # 比较词模式
        self.comparison_patterns = {
            'minimum': {
                'keywords': ['至少', '最少', '最低', '不小于', '大于等于', '>=', '≥'],
                'tolerance': 0.1
            },
            'maximum': {
                'keywords': ['最多', '最高', '不超过', '不大于', '小于等于', '<=', '≤'],
                'tolerance': 0.1
            }
        }
    
    def parse_demand(self, user_input: str) -> EnhancedDemandAnalysis:
        """解析用户需求"""
        # 1. 提取具体数值需求
        specific_requirements = self._extract_specific_requirements(user_input)
        
        # 2. 提取预算信息
        budget_info = self._extract_budget_info(user_input)
        
        # 3. 生成向量权重
        vector_weights = self._generate_vector_weights(user_input, specific_requirements, budget_info)
        
        # 4. 确定关注维度
        focus_dimensions = self._determine_focus_dimensions(vector_weights, specific_requirements)
        
        # 5. 生成需求摘要
        demand_summary = self._generate_demand_summary(specific_requirements, focus_dimensions)
        
        return EnhancedDemandAnalysis(
            vector_weights=vector_weights,
            specific_requirements=specific_requirements,
            budget_info=budget_info,
            focus_dimensions=focus_dimensions,
            demand_summary=demand_summary
        )
    
    def _extract_specific_requirements(self, user_input: str) -> List[SpecificRequirement]:
        """提取具体数值需求"""
        requirements = []
        
        # 1. 提取精确数值
        for category, config in self.number_patterns.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, user_input, re.IGNORECASE)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        requirement = SpecificRequirement(
                            dimension=config['dimension'],
                            value=value,
                            unit=config['unit'],
                            tolerance=config['tolerance'],
                            requirement_type='exact'
                        )
                        requirements.append(requirement)
                        break  # 只取第一个匹配
                    except (ValueError, IndexError):
                        continue
        
        # 2. 提取范围数值
        for category, config in self.range_patterns.items():
            for pattern in config['patterns']:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    try:
                        min_val = float(match.group(1))
                        max_val = float(match.group(2))
                        avg_val = (min_val + max_val) / 2
                        tolerance = (max_val - min_val) / avg_val
                        
                        requirement = SpecificRequirement(
                            dimension=config['dimension'],
                            value=avg_val,
                            unit=config['unit'],
                            tolerance=tolerance,
                            requirement_type='range'
                        )
                        requirements.append(requirement)
                        break
                    except (ValueError, IndexError):
                        continue
        
        # 3. 检查比较词
        for comparison_type, config in self.comparison_patterns.items():
            for keyword in config['keywords']:
                if keyword in user_input:
                    # 查找比较词附近的数字
                    number_match = re.search(rf'{keyword}.*?(\d+)', user_input)
                    if number_match:
                        try:
                            value = float(number_match.group(1))
                            # 根据比较词类型确定需求类型
                            req_type = 'minimum' if comparison_type == 'minimum' else 'maximum'
                            
                            requirement = SpecificRequirement(
                                dimension='price_value',  # 默认价格，可以根据上下文调整
                                value=value,
                                unit='yuan',
                                tolerance=config['tolerance'],
                                requirement_type=req_type
                            )
                            requirements.append(requirement)
                            break
                        except (ValueError, IndexError):
                            continue
        
        return requirements
    
    def _extract_budget_info(self, user_input: str) -> Dict:
        """提取预算信息（复用原有逻辑）"""
        # 这里可以复用原有的预算提取逻辑
        budget_info = {
            'target_price': 0,
            'min_budget': 0,
            'max_budget': 0,
            'tolerance': 0.2,
            'has_budget': False
        }
        
        # 精确范围匹配
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
                        'tolerance': (max_val - min_val) / (min_val + max_val) * 2,
                        'has_budget': True
                    })
                    return budget_info
                except (ValueError, IndexError):
                    continue
        
        # 模糊表达匹配
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
                    tolerance = 0.2 if target_price < 5000 else 0.25
                    
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
        
        return budget_info
    
    def _generate_vector_weights(self, user_input: str, 
                               specific_requirements: List[SpecificRequirement],
                               budget_info: Dict) -> Dict[str, float]:
        """生成向量权重"""
        weights = {
            'cpu_performance': 0.0,
            'memory_capacity': 0.0,
            'storage_speed': 0.0,
            'gpu_performance': 0.0,
            'camera_quality': 0.0,
            'camera_features': 0.0,
            'battery_capacity': 0.0,
            'charging_speed': 0.0,
            'screen_quality': 0.0,
            'screen_size': 0.0,
            'weight_portability': 0.0,
            'size_portability': 0.0,
            'build_quality': 0.0,
            'design_appeal': 0.0,
            'price_value': 0.0,
            'heat_control': 0.0,
            'network_stability': 0.0,
            'software_optimization': 0.0,
            'durability': 0.0
        }
        
        # 1. 根据具体需求设置权重
        for req in specific_requirements:
            if req.dimension in weights:
                weights[req.dimension] = 0.8  # 明确需求给予高权重
        
        # 2. 根据预算信息设置价格权重
        if budget_info.get('has_budget'):
            weights['price_value'] = max(weights['price_value'], 0.7)
        
        # 3. 关键词匹配（作为补充）
        input_lower = user_input.lower()
        
        # 性能相关
        if any(word in input_lower for word in ['性能', '处理器', 'CPU', '游戏', '流畅']):
            weights['cpu_performance'] = max(weights['cpu_performance'], 0.6)
            weights['gpu_performance'] = max(weights['gpu_performance'], 0.5)
        
        # 拍照相关
        if any(word in input_lower for word in ['拍照', '摄影', '相机', '照片']):
            weights['camera_quality'] = max(weights['camera_quality'], 0.7)
            weights['camera_features'] = max(weights['camera_features'], 0.6)
        
        # 续航相关
        if any(word in input_lower for word in ['续航', '电池', '持久', '充电']):
            weights['battery_capacity'] = max(weights['battery_capacity'], 0.7)
            weights['charging_speed'] = max(weights['charging_speed'], 0.5)
        
        # 便携相关
        if any(word in input_lower for word in ['轻薄', '便携', '重量', '携带']):
            weights['weight_portability'] = max(weights['weight_portability'], 0.7)
            weights['size_portability'] = max(weights['size_portability'], 0.6)
        
        return weights
    
    def _determine_focus_dimensions(self, vector_weights: Dict[str, float],
                                  specific_requirements: List[SpecificRequirement]) -> List[str]:
        """确定关注维度"""
        focus_dimensions = []
        
        # 1. 添加有具体需求的维度
        for req in specific_requirements:
            if req.dimension not in focus_dimensions:
                focus_dimensions.append(req.dimension)
        
        # 2. 添加权重较高的维度
        for dimension, weight in vector_weights.items():
            if weight > 0.3 and dimension not in focus_dimensions:
                focus_dimensions.append(dimension)
        
        # 3. 如果没有关注维度，设置默认维度
        if not focus_dimensions:
            focus_dimensions = ['cpu_performance', 'camera_quality', 'battery_capacity', 'price_value']
        
        return focus_dimensions
    
    def _generate_demand_summary(self, specific_requirements: List[SpecificRequirement],
                               focus_dimensions: List[str]) -> str:
        """生成需求摘要"""
        summaries = []
        
        # 添加具体需求摘要
        for req in specific_requirements:
            if req.requirement_type == 'exact':
                summaries.append(f"{req.value}{req.unit}")
            elif req.requirement_type == 'range':
                summaries.append(f"{req.value}{req.unit}左右")
            elif req.requirement_type == 'minimum':
                summaries.append(f"至少{req.value}{req.unit}")
            elif req.requirement_type == 'maximum':
                summaries.append(f"最多{req.value}{req.unit}")
        
        # 添加关注维度摘要
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
        
        focus_names = [dimension_names.get(dim, dim) for dim in focus_dimensions if dim not in [req.dimension for req in specific_requirements]]
        
        if focus_names:
            summaries.append(f"重点关注: {', '.join(focus_names)}")
        
        return "，".join(summaries) if summaries else "通用需求"
    
    def validate_requirements(self, requirements: List[SpecificRequirement]) -> bool:
        """验证需求是否合理"""
        for req in requirements:
            # 检查数值范围
            if req.value <= 0:
                return False
            
            # 检查容差
            if req.tolerance < 0 or req.tolerance > 1:
                return False
        
        return True 