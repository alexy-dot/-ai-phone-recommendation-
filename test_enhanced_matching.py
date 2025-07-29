#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版匹配引擎和雷达图功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.sample_data import sample_phones
from core.enhanced_matching_engine import EnhancedMatchingEngine
from core.enhanced_demand_parser import EnhancedDemandParser
from utils.dynamic_radar import DynamicRadarChartGenerator

def test_enhanced_matching():
    """测试增强版匹配引擎"""
    print("🧪 测试增强版匹配引擎")
    print("=" * 60)
    
    matching_engine = EnhancedMatchingEngine()
    demand_parser = EnhancedDemandParser()
    
    # 测试用例
    test_cases = [
        {
            'name': '明确存储需求',
            'input': '256G的手机',
            'expected_storage': 256
        },
        {
            'name': '复合需求',
            'input': '256G存储，8G内存，拍照好的手机',
            'expected_storage': 256,
            'expected_memory': 8
        },
        {
            'name': '价格+性能需求',
            'input': '3000元左右的手机，性能要好',
            'expected_price_range': (2400, 3600)
        },
        {
            'name': '范围需求',
            'input': '预算3000-4000元，128-256G存储',
            'expected_price_range': (3000, 4000),
            'expected_storage_range': (128, 256)
        },
        {
            'name': '比较需求',
            'input': '至少5000mAh电池，不超过3000元',
            'expected_min_battery': 5000,
            'expected_max_price': 3000
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}: {test_case['name']}")
        print(f"需求: {test_case['input']}")
        print("-" * 50)
        
        # 解析需求
        demand_analysis = demand_parser.parse_demand(test_case['input'])
        print(f"需求解析:")
        print(f"  摘要: {demand_analysis.demand_summary}")
        print(f"  具体需求: {len(demand_analysis.specific_requirements)} 个")
        for req in demand_analysis.specific_requirements:
            print(f"    {req.dimension}: {req.value}{req.unit} ({req.requirement_type})")
        
        # 执行匹配
        recommendations = matching_engine.match_phones(sample_phones, test_case['input'], top_n=3)
        
        print(f"\n推荐结果:")
        for j, rec in enumerate(recommendations, 1):
            phone = rec['phone']
            print(f"  {j}. {phone.name}")
            print(f"     价格: ¥{phone.price}")
            print(f"     存储: {phone.storage_gb}GB")
            print(f"     内存: {phone.ram_gb}GB")
            print(f"     电池: {phone.battery_mah}mAh")
            print(f"     匹配分数: {rec['match_score']:.3f}")
            print(f"     向量分数: {rec['vector_score']:.3f}")
            print(f"     精确分数: {rec['exact_score']:.3f}")
            print(f"     推荐理由: {rec['reasons']}")
        
        # 验证结果
        print(f"\n验证结果:")
        validation_passed = 0
        validation_total = 0
        
        # 验证存储需求
        if 'expected_storage' in test_case:
            validation_total += 1
            target_storage = test_case['expected_storage']
            storage_match_count = sum(1 for rec in recommendations if rec['phone'].storage_gb == target_storage)
            if storage_match_count > 0:
                print(f"  ✅ 存储需求: 推荐了 {storage_match_count} 款 {target_storage}GB 手机")
                validation_passed += 1
            else:
                print(f"  ❌ 存储需求: 未推荐 {target_storage}GB 手机")
        
        # 验证内存需求
        if 'expected_memory' in test_case:
            validation_total += 1
            target_memory = test_case['expected_memory']
            memory_match_count = sum(1 for rec in recommendations if rec['phone'].ram_gb == target_memory)
            if memory_match_count > 0:
                print(f"  ✅ 内存需求: 推荐了 {memory_match_count} 款 {target_memory}GB 内存手机")
                validation_passed += 1
            else:
                print(f"  ❌ 内存需求: 未推荐 {target_memory}GB 内存手机")
        
        # 验证价格范围
        if 'expected_price_range' in test_case:
            validation_total += 1
            min_price, max_price = test_case['expected_price_range']
            price_match_count = sum(1 for rec in recommendations if min_price <= rec['phone'].price <= max_price)
            if price_match_count > 0:
                print(f"  ✅ 价格需求: 推荐了 {price_match_count} 款 ¥{min_price}-{max_price} 手机")
                validation_passed += 1
            else:
                print(f"  ❌ 价格需求: 未推荐 ¥{min_price}-{max_price} 手机")
        
        print(f"  验证通过率: {validation_passed}/{validation_total}")
    
    print("\n" + "=" * 60)
    print("✅ 增强版匹配引擎测试完成！")

def test_radar_charts():
    """测试雷达图功能"""
    print("\n📊 测试雷达图功能")
    print("=" * 60)
    
    matching_engine = EnhancedMatchingEngine()
    radar_generator = DynamicRadarChartGenerator()
    
    # 测试用例
    test_cases = [
        {
            'name': '拍照优先需求',
            'input': '拍照好的手机，预算3000-5000元',
            'expected_dimensions': ['camera_quality', 'camera_features', 'price_value']
        },
        {
            'name': '性能优先需求',
            'input': '性能强劲的游戏手机，8G内存',
            'expected_dimensions': ['cpu_performance', 'gpu_performance', 'memory_capacity']
        },
        {
            'name': '续航优先需求',
            'input': '续航持久的手机，5000mAh以上电池',
            'expected_dimensions': ['battery_capacity', 'charging_speed']
        },
        {
            'name': '便携优先需求',
            'input': '轻薄便携的手机，重量要轻',
            'expected_dimensions': ['weight_portability', 'size_portability']
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📱 测试 {i}: {test_case['name']}")
        print(f"需求: {test_case['input']}")
        
        # 获取推荐结果
        recommendations = matching_engine.match_phones(sample_phones, test_case['input'], top_n=5)
        
        if not recommendations:
            print("❌ 无推荐结果")
            continue
        
        # 解析需求以获取关注维度
        demand_parser = EnhancedDemandParser()
        demand_analysis = demand_parser.parse_demand(test_case['input'])
        
        print(f"关注维度: {demand_analysis.focus_dimensions}")
        
        # 生成雷达图
        try:
            # 创建demand_vector对象用于雷达图
            demand_vector = matching_engine._create_demand_vector(demand_analysis)
            chart_paths = radar_generator.generate_all_charts(recommendations, demand_vector)
            
            print(f"✅ 雷达图生成成功:")
            for chart_type, path in chart_paths.items():
                print(f"  {chart_type}: {path}")
            
            # 验证维度
            if 'expected_dimensions' in test_case:
                expected_dims = set(test_case['expected_dimensions'])
                actual_dims = set(demand_analysis.focus_dimensions)
                overlap = expected_dims.intersection(actual_dims)
                
                if len(overlap) > 0:
                    print(f"✅ 维度匹配: {overlap}")
                else:
                    print(f"⚠️ 维度匹配: 期望 {expected_dims}, 实际 {actual_dims}")
        
        except Exception as e:
            print(f"❌ 雷达图生成失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 雷达图功能测试完成！")

def test_complex_scenarios():
    """测试复杂场景"""
    print("\n🎯 测试复杂场景")
    print("=" * 60)
    
    matching_engine = EnhancedMatchingEngine()
    
    complex_scenarios = [
        {
            'name': '多维度精确需求',
            'input': '256G存储，8G内存，6.1寸屏幕，5000mAh电池，3000元左右的手机',
            'description': '测试多个精确需求的组合'
        },
        {
            'name': '模糊+精确混合需求',
            'input': '拍照好的手机，至少8G内存，不超过4000元',
            'description': '测试模糊需求和精确需求的混合'
        },
        {
            'name': '范围+比较需求',
            'input': '预算3000-5000元，128-256G存储，至少5000mAh电池',
            'description': '测试范围需求和比较需求的组合'
        },
        {
            'name': '无明确需求',
            'input': '想要一个手机',
            'description': '测试无明确需求的情况'
        }
    ]
    
    for scenario in complex_scenarios:
        print(f"\n📋 {scenario['name']}")
        print(f"描述: {scenario['description']}")
        print(f"需求: {scenario['input']}")
        
        try:
            recommendations = matching_engine.match_phones(sample_phones, scenario['input'], top_n=3)
            
            print(f"推荐结果:")
            for i, rec in enumerate(recommendations, 1):
                phone = rec['phone']
                print(f"  {i}. {phone.name} - 匹配度: {rec['match_score']:.3f}")
                print(f"     理由: {rec['reasons']}")
            
            # 分析分数分布
            scores = [rec['match_score'] for rec in recommendations]
            print(f"分数分布: 最高 {max(scores):.3f}, 最低 {min(scores):.3f}, 平均 {sum(scores)/len(scores):.3f}")
        
        except Exception as e:
            print(f"❌ 处理失败: {e}")

if __name__ == "__main__":
    test_enhanced_matching()
    test_radar_charts()
    test_complex_scenarios() 