#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版需求解析器
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.enhanced_demand_parser import EnhancedDemandParser

def test_enhanced_demand_parser():
    """测试增强版需求解析器"""
    print("🧪 测试增强版需求解析器")
    print("=" * 60)
    
    parser = EnhancedDemandParser()
    
    # 测试用例
    test_cases = [
        {
            'name': '明确存储需求',
            'input': '256G的手机',
            'expected': {
                'storage_speed': 256,
                'storage_speed_weight': 0.8
            }
        },
        {
            'name': '明确内存需求',
            'input': '8G内存的手机',
            'expected': {
                'memory_capacity': 8,
                'memory_capacity_weight': 0.8
            }
        },
        {
            'name': '明确屏幕尺寸',
            'input': '6.1寸屏幕的手机',
            'expected': {
                'screen_size': 6.1,
                'screen_size_weight': 0.8
            }
        },
        {
            'name': '明确电池容量',
            'input': '5000mAh电池的手机',
            'expected': {
                'battery_capacity': 5000,
                'battery_capacity_weight': 0.8
            }
        },
        {
            'name': '明确摄像头像素',
            'input': '48MP摄像头的手机',
            'expected': {
                'camera_quality': 48,
                'camera_quality_weight': 0.8
            }
        },
        {
            'name': '明确价格需求',
            'input': '3000元左右的手机',
            'expected': {
                'price_value': 3000,
                'price_value_weight': 0.8,
                'has_budget': True
            }
        },
        {
            'name': '复合需求',
            'input': '256G存储，8G内存，拍照好的手机',
            'expected': {
                'storage_speed': 256,
                'memory_capacity': 8,
                'camera_quality_weight': 0.7
            }
        },
        {
            'name': '范围需求',
            'input': '预算3000-4000元，128-256G存储',
            'expected': {
                'price_value': 3500,
                'storage_speed': 192,
                'has_budget': True
            }
        },
        {
            'name': '比较需求',
            'input': '至少5000mAh电池，不超过3000元',
            'expected': {
                'battery_capacity': 5000,
                'price_value': 3000
            }
        }
    ]
    
    print("\n📊 测试需求解析:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   输入: {test_case['input']}")
        
        # 解析需求
        analysis = parser.parse_demand(test_case['input'])
        
        print(f"   解析结果:")
        print(f"     需求摘要: {analysis.demand_summary}")
        print(f"     关注维度: {analysis.focus_dimensions}")
        
        # 显示具体需求
        if analysis.specific_requirements:
            print(f"     具体需求:")
            for req in analysis.specific_requirements:
                print(f"       {req.dimension}: {req.value}{req.unit} ({req.requirement_type})")
        
        # 显示向量权重
        print(f"     向量权重:")
        for dimension, weight in analysis.vector_weights.items():
            if weight > 0.1:
                print(f"       {dimension}: {weight:.3f}")
        
        # 显示预算信息
        if analysis.budget_info.get('has_budget'):
            print(f"     预算信息:")
            if analysis.budget_info.get('target_price'):
                print(f"       目标价格: ¥{analysis.budget_info['target_price']}")
                print(f"       容差: {analysis.budget_info['tolerance']:.1%}")
            if analysis.budget_info.get('min_budget') and analysis.budget_info.get('max_budget'):
                print(f"       预算范围: ¥{analysis.budget_info['min_budget']} - ¥{analysis.budget_info['max_budget']}")
        
        # 验证结果
        expected = test_case['expected']
        validation_results = []
        
        for req in analysis.specific_requirements:
            if req.dimension in expected:
                expected_value = expected[req.dimension]
                if abs(req.value - expected_value) < 1:  # 允许1的误差
                    validation_results.append(f"✅ {req.dimension}: {req.value} ≈ {expected_value}")
                else:
                    validation_results.append(f"❌ {req.dimension}: {req.value} ≠ {expected_value}")
        
        # 验证权重
        for dimension, expected_weight in expected.items():
            if dimension.endswith('_weight'):
                actual_dimension = dimension.replace('_weight', '')
                actual_weight = analysis.vector_weights.get(actual_dimension, 0)
                if abs(actual_weight - expected_weight) < 0.1:
                    validation_results.append(f"✅ {actual_dimension}权重: {actual_weight:.3f} ≈ {expected_weight}")
                else:
                    validation_results.append(f"❌ {actual_dimension}权重: {actual_weight:.3f} ≠ {expected_weight}")
        
        # 验证预算
        if 'has_budget' in expected:
            actual_has_budget = analysis.budget_info.get('has_budget', False)
            if actual_has_budget == expected['has_budget']:
                validation_results.append(f"✅ 预算识别: {actual_has_budget}")
            else:
                validation_results.append(f"❌ 预算识别: {actual_has_budget} ≠ {expected['has_budget']}")
        
        if validation_results:
            print(f"   验证结果:")
            for result in validation_results:
                print(f"     {result}")
        
        print()
    
    print("=" * 60)
    print("✅ 增强版需求解析器测试完成！")

def test_edge_cases():
    """测试边界情况"""
    print("\n🎯 测试边界情况")
    print("=" * 40)
    
    parser = EnhancedDemandParser()
    
    edge_cases = [
        {
            'name': '无明确需求',
            'input': '想要一个手机',
            'expected_focus': ['cpu_performance', 'camera_quality', 'battery_capacity', 'price_value']
        },
        {
            'name': '多个相同类型需求',
            'input': '256G存储，512G存储',
            'expected': '应该只取第一个匹配'
        },
        {
            'name': '复杂表达',
            'input': '要一个至少8G内存，不超过3000元，拍照好的手机',
            'expected_requirements': 3
        },
        {
            'name': '单位变体',
            'input': '256GB存储，8G内存，6.1英寸屏幕',
            'expected_requirements': 3
        }
    ]
    
    for case in edge_cases:
        print(f"\n📱 {case['name']}")
        print(f"输入: {case['input']}")
        
        analysis = parser.parse_demand(case['input'])
        
        print(f"解析结果:")
        print(f"  需求摘要: {analysis.demand_summary}")
        print(f"  具体需求数量: {len(analysis.specific_requirements)}")
        print(f"  关注维度: {analysis.focus_dimensions}")
        
        if analysis.specific_requirements:
            print(f"  具体需求:")
            for req in analysis.specific_requirements:
                print(f"    {req.dimension}: {req.value}{req.unit} ({req.requirement_type})")

if __name__ == "__main__":
    test_enhanced_demand_parser()
    test_edge_cases() 