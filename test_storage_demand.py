#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试存储容量等明确需求的处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.sample_data import sample_phones
from core.new_recommendation_engine import NewRecommendationEngine
from core.demand_vectorization import DemandVectorizationEngine

def test_storage_demand():
    """测试存储容量需求的处理"""
    print("🧪 测试存储容量等明确需求的处理")
    print("=" * 60)
    
    demand_engine = DemandVectorizationEngine()
    recommendation_engine = NewRecommendationEngine()
    
    # 测试用例
    test_cases = [
        {
            'name': '明确存储需求',
            'input': '256G的手机',
            'expected_storage': 256
        },
        {
            'name': '存储容量需求',
            'input': '要128G存储空间的手机',
            'expected_storage': 128
        },
        {
            'name': '大容量需求',
            'input': '512G大容量手机',
            'expected_storage': 512
        },
        {
            'name': '存储+其他需求',
            'input': '256G存储，拍照好的手机',
            'expected_storage': 256
        }
    ]
    
    print("\n📊 测试需求向量化:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   输入: {test_case['input']}")
        
        # 向量化需求
        demand_vector, budget_info = demand_engine.vectorize_demand(test_case['input'])
        
        print(f"   向量化结果:")
        print(f"     storage_speed权重: {demand_vector.storage_speed:.3f}")
        print(f"     memory_capacity权重: {demand_vector.memory_capacity:.3f}")
        print(f"     关注维度: {demand_vector.focus_dimensions}")
        
        # 检查是否识别到存储需求
        if demand_vector.storage_speed > 0.1:
            print(f"   ✅ 识别到存储需求")
        else:
            print(f"   ❌ 未识别到存储需求")
    
    print("\n\n🚀 测试推荐效果:")
    
    for test_case in test_cases[:2]:  # 测试前2个用例
        print(f"\n📋 测试: {test_case['name']}")
        print(f"需求: {test_case['input']}")
        
        try:
            # 运行推荐
            result = recommendation_engine.recommend(sample_phones, test_case['input'], top_n=3)
            
            print(f"\n推荐结果:")
            for i, rec in enumerate(result['recommendations'], 1):
                phone = rec['phone']
                print(f"  {i}. {phone.name}")
                print(f"     存储: {phone.storage_gb}GB")
                print(f"     匹配分数: {rec['match_score']:.3f}")
                print(f"     推荐理由: {rec['reasons']}")
            
            # 检查推荐结果是否符合存储需求
            target_storage = test_case['expected_storage']
            storage_match_count = 0
            for rec in result['recommendations']:
                if rec['phone'].storage_gb == target_storage:
                    storage_match_count += 1
            
            if storage_match_count > 0:
                print(f"   ✅ 推荐了 {storage_match_count} 款符合存储需求的手机")
            else:
                print(f"   ⚠️ 未推荐符合存储需求的手机")
            
        except Exception as e:
            print(f"❌ 推荐失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 存储需求处理测试完成！")

def test_other_specific_demands():
    """测试其他明确需求"""
    print("\n🎯 测试其他明确需求")
    print("=" * 40)
    
    demand_engine = DemandVectorizationEngine()
    
    specific_demands = [
        {
            'name': '明确内存需求',
            'input': '8G内存的手机',
            'dimension': 'memory_capacity'
        },
        {
            'name': '明确屏幕尺寸',
            'input': '6.1寸屏幕的手机',
            'dimension': 'screen_size'
        },
        {
            'name': '明确电池容量',
            'input': '5000mAh电池的手机',
            'dimension': 'battery_capacity'
        },
        {
            'name': '明确摄像头像素',
            'input': '48MP摄像头的手机',
            'dimension': 'camera_quality'
        }
    ]
    
    for demand in specific_demands:
        print(f"\n📱 {demand['name']}")
        print(f"输入: {demand['input']}")
        
        # 向量化需求
        demand_vector, _ = demand_engine.vectorize_demand(demand['input'])
        
        # 获取对应维度的权重
        dimension_weight = getattr(demand_vector, demand['dimension'])
        print(f"权重: {dimension_weight:.3f}")
        
        if dimension_weight > 0.1:
            print(f"✅ 正确识别到{demand['name']}")
        else:
            print(f"❌ 未识别到{demand['name']}")

if __name__ == "__main__":
    test_storage_demand()
    test_other_specific_demands() 