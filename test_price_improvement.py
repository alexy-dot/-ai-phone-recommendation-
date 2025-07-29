#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试价格评分改进效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.sample_data import sample_phones
from core.new_recommendation_engine import NewRecommendationEngine
from core.vectorization_engine import VectorizationEngine
from core.demand_vectorization import DemandVectorizationEngine

def test_price_scoring_improvement():
    """测试价格评分改进效果"""
    print("🧪 测试价格评分改进效果")
    print("=" * 60)
    
    # 初始化引擎
    vectorization_engine = VectorizationEngine()
    demand_engine = DemandVectorizationEngine()
    recommendation_engine = NewRecommendationEngine()
    
    # 测试用例
    test_cases = [
        {
            'name': '精确预算范围',
            'input': '预算3000-4000元，拍照优先',
            'expected_budget': {'min_budget': 3000, 'max_budget': 4000}
        },
        {
            'name': '模糊表达',
            'input': '大约3000元左右的手机',
            'expected_budget': {'target_price': 3000, 'tolerance': 0.2}
        },
        {
            'name': '单一价格',
            'input': '3000元的手机',
            'expected_budget': {'target_price': 3000, 'tolerance': 0.1}
        },
        {
            'name': '经济型需求',
            'input': '便宜实惠的手机',
            'expected_budget': {'target_price': 3000, 'min_budget': 1500, 'max_budget': 4500}
        },
        {
            'name': '高端需求',
            'input': '高端旗舰手机',
            'expected_budget': {'target_price': 8000, 'min_budget': 6000, 'max_budget': 12000}
        }
    ]
    
    # 测试预算提取
    print("\n📊 测试预算提取功能:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   输入: {test_case['input']}")
        
        # 提取预算信息
        demand_vector, budget_info = demand_engine.vectorize_demand(test_case['input'])
        
        print(f"   提取结果:")
        print(f"     有预算信息: {budget_info.get('has_budget', False)}")
        if budget_info.get('has_budget'):
            if budget_info.get('target_price'):
                print(f"     目标价格: ¥{budget_info['target_price']}")
                print(f"     容差: {budget_info['tolerance']:.1%}")
            if budget_info.get('min_budget') and budget_info.get('max_budget'):
                print(f"     预算范围: ¥{budget_info['min_budget']} - ¥{budget_info['max_budget']}")
        
        # 验证结果
        expected = test_case['expected_budget']
        if budget_info.get('has_budget'):
            if 'target_price' in expected and budget_info.get('target_price') == expected['target_price']:
                print(f"   ✅ 目标价格匹配")
            elif 'min_budget' in expected and budget_info.get('min_budget') == expected['min_budget']:
                print(f"   ✅ 预算范围匹配")
            else:
                print(f"   ⚠️ 结果与预期不完全匹配")
        else:
            print(f"   ❌ 未提取到预算信息")
    
    # 测试价格评分
    print("\n\n💰 测试价格评分效果:")
    
    # 选择几款不同价格的手机进行测试
    test_phones = sample_phones[:5]  # 取前5款手机
    
    for test_case in test_cases[:3]:  # 测试前3个用例
        print(f"\n📱 测试用例: {test_case['name']}")
        print(f"用户需求: {test_case['input']}")
        
        # 获取预算信息
        _, budget_info = demand_engine.vectorize_demand(test_case['input'])
        
        print(f"\n手机价格评分对比:")
        print(f"{'手机名称':<20} {'价格':<10} {'传统评分':<10} {'新评分':<10} {'改进':<10}")
        print("-" * 70)
        
        for phone in test_phones:
            # 传统评分（无预算信息）
            traditional_score = vectorization_engine._calculate_traditional_price_score(phone)
            
            # 新评分（有预算信息）
            new_score = vectorization_engine._calculate_price_value_score(phone, budget_info)
            
            # 计算改进程度
            improvement = new_score - traditional_score
            
            print(f"{phone.name:<20} ¥{phone.price:<9} {traditional_score:<10.3f} {new_score:<10.3f} {improvement:+.3f}")
    
    # 测试完整推荐流程
    print("\n\n🚀 测试完整推荐流程:")
    
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
                print(f"     价格: ¥{phone.price}")
                print(f"     匹配分数: {rec['match_score']:.3f}")
                print(f"     推荐理由: {rec['reasons']}")
            
            # 显示预算信息
            budget_info = result['demand_analysis'].get('budget_info', {})
            if budget_info.get('has_budget'):
                print(f"\n预算匹配分析:")
                if budget_info.get('target_price'):
                    print(f"  目标价格: ¥{budget_info['target_price']}")
                    print(f"  容差范围: {budget_info['tolerance']:.1%}")
                if budget_info.get('min_budget') and budget_info.get('max_budget'):
                    print(f"  预算范围: ¥{budget_info['min_budget']} - ¥{budget_info['max_budget']}")
            
        except Exception as e:
            print(f"❌ 推荐失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 价格评分改进测试完成！")

def test_specific_scenarios():
    """测试特定场景"""
    print("\n🎯 测试特定场景")
    print("=" * 40)
    
    recommendation_engine = NewRecommendationEngine()
    
    # 场景1: 用户说"3000元左右的手机"
    print("\n场景1: 用户说'3000元左右的手机'")
    result1 = recommendation_engine.recommend(sample_phones, "3000元左右的手机", top_n=3)
    
    print("推荐结果:")
    for i, rec in enumerate(result1['recommendations'], 1):
        phone = rec['phone']
        print(f"  {i}. {phone.name} (¥{phone.price}) - 匹配度: {rec['match_score']:.3f}")
    
    # 场景2: 用户说"预算3000-4000，拍照优先"
    print("\n场景2: 用户说'预算3000-4000，拍照优先'")
    result2 = recommendation_engine.recommend(sample_phones, "预算3000-4000，拍照优先", top_n=3)
    
    print("推荐结果:")
    for i, rec in enumerate(result2['recommendations'], 1):
        phone = rec['phone']
        print(f"  {i}. {phone.name} (¥{phone.price}) - 匹配度: {rec['match_score']:.3f}")
    
    # 场景3: 用户说"便宜实惠的手机"
    print("\n场景3: 用户说'便宜实惠的手机'")
    result3 = recommendation_engine.recommend(sample_phones, "便宜实惠的手机", top_n=3)
    
    print("推荐结果:")
    for i, rec in enumerate(result3['recommendations'], 1):
        phone = rec['phone']
        print(f"  {i}. {phone.name} (¥{phone.price}) - 匹配度: {rec['match_score']:.3f}")

if __name__ == "__main__":
    test_price_scoring_improvement()
    test_specific_scenarios() 