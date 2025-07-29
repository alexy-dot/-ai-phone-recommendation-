#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ark API集成演示
"""

import sys
import os
sys.path.append('.')

from services.llm_provider import LLMProvider

def demo_ark_integration():
    """演示Ark API集成"""
    print("🚀 Ark API集成演示")
    print("=" * 60)
    
    # 创建LLM提供者
    llm_provider = LLMProvider()
    
    print(f"📡 API类型: {llm_provider.config.api_type}")
    print(f"🤖 模型: {llm_provider.config.model_name}")
    print(f"✅ LLM服务可用: {llm_provider.is_available()}")
    
    # 演示1：意图理解
    print("\n" + "=" * 60)
    print("🎯 演示1：意图理解")
    print("-" * 30)
    
    user_inputs = [
        "预算3000-4000，拍照优先",
        "想要轻薄便携的手机",
        "需要性能强劲的游戏手机",
        "续航持久的商务手机"
    ]
    
    for i, user_input in enumerate(user_inputs, 1):
        print(f"\n{i}. 用户输入: {user_input}")
        try:
            intent_result = llm_provider.understand_intent(user_input)
            print(f"   📊 意图分析结果:")
            print(f"   - 意图: {intent_result.get('intent', 'N/A')}")
            print(f"   - 预算: {intent_result.get('budget_min', 'N/A')} - {intent_result.get('budget_max', 'N/A')}")
            print(f"   - 偏好: {intent_result.get('preferences', [])}")
            print(f"   - 优先级: {intent_result.get('priority', 'N/A')}")
            print(f"   - 置信度: {intent_result.get('confidence', 'N/A')}")
        except Exception as e:
            print(f"   ❌ 分析失败: {e}")
    
    # 演示2：推荐解释生成
    print("\n" + "=" * 60)
    print("💬 演示2：推荐解释生成")
    print("-" * 30)
    
    phones = [
        {
            "name": "iPhone 15",
            "reasons": ["性能强劲", "拍照优秀", "系统流畅"],
            "demand": "预算3000-4000，拍照优先"
        },
        {
            "name": "华为P60",
            "reasons": ["拍照出色", "续航持久", "设计精美"],
            "demand": "想要轻薄便携的手机"
        }
    ]
    
    for i, phone in enumerate(phones, 1):
        print(f"\n{i}. 推荐手机: {phone['name']}")
        print(f"   推荐理由: {', '.join(phone['reasons'])}")
        print(f"   用户需求: {phone['demand']}")
        
        try:
            explanation = llm_provider.generate_recommendation_explanation(
                phone['name'], phone['reasons'], phone['demand']
            )
            print(f"   💬 AI推荐解释:")
            print(f"   {explanation}")
        except Exception as e:
            print(f"   ❌ 生成失败: {e}")
    
    # 演示3：澄清问题生成
    print("\n" + "=" * 60)
    print("❓ 演示3：澄清问题生成")
    print("-" * 30)
    
    unclear_aspects = ["budget", "performance", "camera", "battery", "portability"]
    
    for aspect in unclear_aspects:
        try:
            question = llm_provider.generate_clarification_question(aspect)
            print(f"   {aspect}: {question}")
        except Exception as e:
            print(f"   {aspect}: ❌ 生成失败 - {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Ark API集成演示完成！")
    print("\n💡 主要特点:")
    print("✅ 智能意图理解 - 准确解析用户需求")
    print("✅ 自然语言解释 - 生成详细的推荐理由")
    print("✅ 智能澄清问题 - 主动收集缺失信息")
    print("✅ 本地回退机制 - 确保系统稳定运行")

if __name__ == "__main__":
    demo_ark_integration() 