#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Token分析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.sample_data import sample_phones
from analysis.token_limit_analysis import TokenLimitAnalyzer

def test_token_analysis():
    """测试Token分析功能"""
    print("🔍 测试Token限制分析")
    print("=" * 60)
    
    analyzer = TokenLimitAnalyzer()
    
    # 1. 测试系统提示分析
    print("\n📝 1. 系统提示分析")
    system_prompt = """
    你是一个专业的手机推荐助手。你需要根据用户的需求，从提供的手机数据中选择最合适的手机进行推荐。
    
    你的任务包括：
    1. 理解用户的需求和偏好
    2. 分析手机的各项参数和性能
    3. 根据用户需求进行匹配和推荐
    4. 提供详细的推荐理由和对比分析
    
    请确保推荐的手机符合用户的主要需求，并提供充分的理由说明为什么这些手机是最佳选择。
    """
    
    system_analysis = analyzer.analyze_system_prompt(system_prompt)
    print(f"Token使用量: {system_analysis.total_tokens}")
    print(f"风险等级: {system_analysis.risk_level}")
    print(f"风险因素: {system_analysis.risk_factors}")
    print(f"建议: {system_analysis.recommendations}")
    print(f"成本估算: ${system_analysis.cost_estimate:.4f}")
    
    # 2. 测试用户输入分析
    print("\n👤 2. 用户输入分析")
    user_input = "我想要一个拍照好的手机，预算在3000-5000元之间，最好是256G存储，8G内存，电池容量要大一些，续航要持久。"
    
    user_analysis = analyzer.analyze_user_input(user_input)
    print(f"Token使用量: {user_analysis.total_tokens}")
    print(f"风险等级: {user_analysis.risk_level}")
    print(f"风险因素: {user_analysis.risk_factors}")
    print(f"建议: {user_analysis.recommendations}")
    
    # 3. 测试手机数据分析
    print("\n📱 3. 手机数据分析")
    # 转换手机数据为字典格式
    phones_data = []
    for phone in sample_phones:
        phone_dict = {
            'name': phone.name,
            'cpu': phone.cpu,
            'ram_gb': phone.ram_gb,
            'storage_gb': phone.storage_gb,
            'screen_size_inch': phone.screen_size_inch,
            'camera_mp': phone.camera_mp,
            'battery_mah': phone.battery_mah,
            'weight_g': phone.weight_g,
            'price': phone.price,
            'highlights': phone.highlights,
            'rating': phone.rating,
            'sales': phone.sales,
            'heat_control_score': phone.heat_control_score,
            'network_stability_score': phone.network_stability_score
        }
        phones_data.append(phone_dict)
    
    phone_analysis = analyzer.analyze_phone_data(phones_data)
    print(f"Token使用量: {phone_analysis.total_tokens}")
    print(f"风险等级: {phone_analysis.risk_level}")
    print(f"风险因素: {phone_analysis.risk_factors}")
    print(f"建议: {phone_analysis.recommendations}")
    print(f"成本估算: ${phone_analysis.cost_estimate:.4f}")
    
    # 4. 测试完整请求分析
    print("\n🔄 4. 完整请求分析")
    complete_analysis = analyzer.analyze_complete_request(
        system_prompt, user_input, "", phones_data
    )
    print(f"总Token使用量: {complete_analysis.total_tokens}")
    print(f"风险等级: {complete_analysis.risk_level}")
    print(f"风险因素: {complete_analysis.risk_factors}")
    print(f"建议: {complete_analysis.recommendations}")
    print(f"成本估算: ${complete_analysis.cost_estimate:.4f}")
    
    # 5. 显示优化策略
    print("\n💡 5. 优化策略")
    strategies = analyzer.get_optimization_strategies()
    for category, strategy_list in strategies.items():
        print(f"\n{category}:")
        for strategy in strategy_list:
            print(f"  - {strategy}")
    
    # 6. 测试不同模型
    print("\n🤖 6. 不同模型对比")
    models = ['gpt-4', 'gpt-3.5-turbo']
    
    for model in models:
        print(f"\n{model}:")
        model_analysis = analyzer.analyze_complete_request(
            system_prompt, user_input, "", phones_data, model
        )
        print(f"  Token使用量: {model_analysis.total_tokens}")
        print(f"  风险等级: {model_analysis.risk_level}")
        print(f"  成本估算: ${model_analysis.cost_estimate:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ Token分析测试完成！")

def test_optimization_scenarios():
    """测试优化场景"""
    print("\n🎯 测试优化场景")
    print("=" * 60)
    
    analyzer = TokenLimitAnalyzer()
    
    # 场景1: 大量手机数据
    print("\n📊 场景1: 大量手机数据")
    large_phones_data = []
    for i in range(100):  # 100款手机
        phone_dict = {
            'name': f'Phone_{i}',
            'cpu': f'CPU_{i}',
            'ram_gb': 8 + (i % 8),
            'storage_gb': 128 + (i % 4) * 128,
            'screen_size_inch': 6.0 + (i % 10) * 0.1,
            'camera_mp': 48 + (i % 5) * 12,
            'battery_mah': 4000 + (i % 10) * 200,
            'weight_g': 180 + (i % 20),
            'price': 2000 + (i % 30) * 100,
            'highlights': [f'feature_{j}' for j in range(5)],
            'rating': 4.0 + (i % 10) * 0.1,
            'sales': 1000 + (i % 50) * 100,
            'heat_control_score': 0.7 + (i % 10) * 0.03,
            'network_stability_score': 0.8 + (i % 10) * 0.02
        }
        large_phones_data.append(phone_dict)
    
    large_analysis = analyzer.analyze_phone_data(large_phones_data)
    print(f"Token使用量: {large_analysis.total_tokens}")
    print(f"风险等级: {large_analysis.risk_level}")
    print(f"风险因素: {large_analysis.risk_factors}")
    print(f"建议: {large_analysis.recommendations}")
    
    # 场景2: 复杂用户需求
    print("\n📝 场景2: 复杂用户需求")
    complex_user_input = """
    我需要一个手机，具体要求如下：
    1. 拍照功能要非常强大，最好是徕卡镜头或者蔡司镜头
    2. 处理器要高端，最好是骁龙8 Gen 2或者天玑9200+
    3. 内存至少12GB，存储至少256GB
    4. 屏幕要6.7寸以上，分辨率要高，支持120Hz刷新率
    5. 电池容量要5000mAh以上，支持快充
    6. 价格在4000-8000元之间
    7. 品牌最好是华为、小米、OPPO、vivo、一加等知名品牌
    8. 要有良好的散热系统
    9. 网络要支持5G
    10. 系统要流畅，最好是原生Android或者MIUI、EMUI等成熟系统
    11. 外观要时尚，最好是玻璃机身
    12. 要有NFC功能
    13. 支持无线充电
    14. 要有IP68防水
    15. 要有立体声扬声器
    """
    
    complex_analysis = analyzer.analyze_user_input(complex_user_input)
    print(f"Token使用量: {complex_analysis.total_tokens}")
    print(f"风险等级: {complex_analysis.risk_level}")
    print(f"风险因素: {complex_analysis.risk_factors}")
    print(f"建议: {complex_analysis.recommendations}")
    
    # 场景3: 长系统提示
    print("\n⚙️ 场景3: 长系统提示")
    long_system_prompt = """
    你是一个专业的智能手机推荐助手，具有以下能力和职责：
    
    1. 专业知识：
       - 深入了解各种手机品牌、型号和规格
       - 掌握手机性能评估和对比方法
       - 熟悉不同用户群体的需求和偏好
       - 了解手机市场趋势和最新技术
    
    2. 需求分析：
       - 准确理解用户的需求和偏好
       - 识别用户的核心需求和次要需求
       - 分析用户的预算限制和使用场景
       - 考虑用户的品牌偏好和特殊要求
    
    3. 数据评估：
       - 全面分析手机的各项参数和性能
       - 评估手机在不同场景下的表现
       - 对比不同手机的优缺点
       - 考虑性价比和长期使用价值
    
    4. 推荐策略：
       - 根据用户需求进行精准匹配
       - 提供多个推荐选项供用户选择
       - 详细说明推荐理由和优势
       - 提供对比分析和购买建议
    
    5. 沟通技巧：
       - 使用清晰易懂的语言
       - 提供专业而友好的建议
       - 耐心回答用户的问题
       - 主动澄清模糊的需求
    
    6. 持续改进：
       - 收集用户反馈
       - 更新产品知识
       - 优化推荐算法
       - 提升服务质量
    
    请确保你的推荐准确、专业、有用，并始终以用户的最佳利益为出发点。
    """
    
    long_system_analysis = analyzer.analyze_system_prompt(long_system_prompt)
    print(f"Token使用量: {long_system_analysis.total_tokens}")
    print(f"风险等级: {long_system_analysis.risk_level}")
    print(f"风险因素: {long_system_analysis.risk_factors}")
    print(f"建议: {long_system_analysis.recommendations}")

if __name__ == "__main__":
    test_token_analysis()
    test_optimization_scenarios() 