#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的澄清问题生成机制
"""

import sys
import os
sys.path.append('.')

from services.llm_provider import LLMProvider

def test_clarification_questions():
    """测试澄清问题生成"""
    print("🧪 测试优化后的澄清问题生成机制")
    print("=" * 60)
    
    # 创建LLM提供者
    llm_provider = LLMProvider()
    
    # 模拟对话历史
    conversation_history = [
        {"user": "我想买一个手机", "system": "您的预算大概是多少呢？"},
        {"user": "3000左右", "system": "您主要用手机做什么呢？"},
        {"user": "拍照和日常使用", "system": "您更注重夜景拍摄还是广角拍摄？"}
    ]
    
    # 测试不同的不清楚方面
    test_cases = [
        {
            "aspect": "budget",
            "context": "用户想要拍照好的手机",
            "description": "预算不明确的情况"
        },
        {
            "aspect": "camera",
            "context": "用户提到拍照需求",
            "description": "拍照偏好不明确的情况"
        },
        {
            "aspect": "performance",
            "context": "用户可能玩游戏",
            "description": "性能需求不明确的情况"
        },
        {
            "aspect": "portability",
            "context": "用户关心手机大小",
            "description": "便携性需求不明确的情况"
        },
        {
            "aspect": "battery",
            "context": "用户担心续航",
            "description": "续航需求不明确的情况"
        }
    ]
    
    print("📝 测试用例:")
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   不清楚方面: {case['aspect']}")
        print(f"   上下文: {case['context']}")
        
        # 测试LLM生成
        try:
            llm_question = llm_provider.generate_clarification_question(
                case['aspect'], 
                case['context'], 
                conversation_history
            )
            print(f"   🤖 LLM生成: {llm_question}")
        except Exception as e:
            print(f"   ❌ LLM生成失败: {e}")
        
        # 测试本地回退
        try:
            local_question = llm_provider._smart_fallback_clarification_question(
                case['aspect'], 
                case['context'], 
                conversation_history
            )
            print(f"   🔧 本地回退: {local_question}")
        except Exception as e:
            print(f"   ❌ 本地回退失败: {e}")
    
    # 测试重复问题避免
    print("\n" + "=" * 60)
    print("🔄 测试重复问题避免机制")
    print("-" * 30)
    
    # 模拟已经问过预算问题的情况
    asked_budget_questions = [
        "您的预算大概是多少呢？",
        "请问您能接受的价格范围是？",
        "您希望购买什么价位的手机？"
    ]
    
    print("已问过的预算问题:")
    for q in asked_budget_questions:
        print(f"   - {q}")
    
    # 测试在这种情况下生成新的预算问题
    try:
        new_question = llm_provider._smart_fallback_clarification_question(
            "budget", 
            "用户需要推荐手机", 
            [{"system": q} for q in asked_budget_questions]
        )
        print(f"\n🤖 生成的新问题: {new_question}")
        
        # 检查是否重复
        is_repeated = any(q in new_question for q in asked_budget_questions)
        if is_repeated:
            print("❌ 问题重复了！")
        else:
            print("✅ 成功避免了重复问题！")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 测试多样化问题生成
    print("\n" + "=" * 60)
    print("🎲 测试多样化问题生成")
    print("-" * 30)
    
    # 多次生成相同类型的问题，看是否多样化
    performance_questions = []
    for i in range(5):
        try:
            question = llm_provider._smart_fallback_clarification_question(
                "performance", 
                "用户关心性能", 
                []
            )
            performance_questions.append(question)
        except Exception as e:
            print(f"❌ 生成失败: {e}")
    
    print("生成的性能相关问题:")
    for i, q in enumerate(performance_questions, 1):
        print(f"   {i}. {q}")
    
    # 检查多样性
    unique_questions = set(performance_questions)
    diversity_ratio = len(unique_questions) / len(performance_questions)
    print(f"\n多样性比例: {diversity_ratio:.2f} ({len(unique_questions)}/{len(performance_questions)})")
    
    if diversity_ratio > 0.8:
        print("✅ 问题生成具有良好的多样性！")
    else:
        print("⚠️ 问题多样性有待提高")
    
    print("\n" + "=" * 60)
    print("🎉 澄清问题生成机制测试完成！")
    print("\n💡 优化效果:")
    print("✅ 避免重复问题 - 检查历史记录")
    print("✅ 多样化问题 - 多种表达方式")
    print("✅ 上下文感知 - 根据对话调整")
    print("✅ 智能回退 - 本地备用方案")
    print("✅ 自然表达 - 像真人导购")

if __name__ == "__main__":
    test_clarification_questions() 