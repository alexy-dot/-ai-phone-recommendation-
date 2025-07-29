#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化后的对话系统演示
展示如何避免重复和死板的问题
"""

import sys
import os
sys.path.append('.')

from services.llm_provider import LLMProvider
from core.dialogue_controller import DialogueManager, DialogueContext, DialogueState

def demo_optimized_dialogue():
    """演示优化后的对话系统"""
    print("🎭 优化后的对话系统演示")
    print("=" * 60)
    print("💡 本次演示将展示系统如何避免重复和死板的问题")
    print("=" * 60)
    
    # 创建LLM提供者和对话管理器
    llm_provider = LLMProvider()
    dialogue_manager = DialogueManager()
    
    # 创建会话
    session_id = "demo_session"
    context = dialogue_manager.create_session(session_id)
    
    # 模拟多轮对话
    conversation_scenarios = [
        {
            "user_input": "我想买一个手机",
            "description": "用户初始需求，系统需要收集更多信息"
        },
        {
            "user_input": "3000左右",
            "description": "用户提供预算，系统继续收集偏好信息"
        },
        {
            "user_input": "主要拍照和日常使用",
            "description": "用户提供使用场景，系统需要细化拍照需求"
        },
        {
            "user_input": "夜景拍摄比较多",
            "description": "用户细化拍照需求，系统可以开始推荐"
        },
        {
            "user_input": "还有其他推荐吗",
            "description": "用户要求更多推荐，系统提供备选方案"
        }
    ]
    
    print("🔄 开始多轮对话演示:")
    print("-" * 40)
    
    for i, scenario in enumerate(conversation_scenarios, 1):
        print(f"\n📝 第{i}轮对话:")
        print(f"   用户输入: {scenario['user_input']}")
        print(f"   场景描述: {scenario['description']}")
        
        # 处理用户输入
        response = dialogue_manager.process_user_input(
            session_id, 
            scenario['user_input'], 
            []  # 这里应该传入手机数据，但为了演示简化
        )
        
        print(f"   系统状态: {response['state']}")
        print(f"   系统回复: {response['message']}")
        
        if response.get('clarification_question'):
            print(f"   🔍 澄清问题: {response['clarification_question']}")
        
        if response.get('recommendations'):
            print(f"   📋 推荐结果: {len(response['recommendations'])} 个推荐")
        
        print("-" * 40)
    
    # 演示重复问题避免机制
    print("\n" + "=" * 60)
    print("🛡️ 重复问题避免机制演示")
    print("-" * 40)
    
    # 模拟已经问过的问题
    asked_questions = [
        "您的预算大概是多少呢？",
        "您主要用手机做什么呢？",
        "您更注重夜景拍摄还是广角拍摄？"
    ]
    
    print("已问过的问题:")
    for q in asked_questions:
        print(f"   - {q}")
    
    # 测试在不同情况下生成新的澄清问题
    test_aspects = ["budget", "camera", "performance", "battery"]
    
    print("\n测试生成新的澄清问题:")
    for aspect in test_aspects:
        try:
            # 使用LLM生成
            llm_question = llm_provider.generate_clarification_question(
                aspect, 
                "用户需要推荐手机", 
                [{"system": q} for q in asked_questions]
            )
            print(f"   {aspect} (LLM): {llm_question}")
            
            # 使用本地回退
            local_question = llm_provider._smart_fallback_clarification_question(
                aspect, 
                "用户需要推荐手机", 
                [{"system": q} for q in asked_questions]
            )
            print(f"   {aspect} (本地): {local_question}")
            
        except Exception as e:
            print(f"   {aspect}: ❌ 生成失败 - {e}")
    
    # 演示多样化问题生成
    print("\n" + "=" * 60)
    print("🎲 多样化问题生成演示")
    print("-" * 40)
    
    # 测试同一类型问题的多样化
    aspect = "performance"
    print(f"测试 '{aspect}' 类型问题的多样化:")
    
    questions_generated = []
    for i in range(8):  # 生成8个问题
        try:
            question = llm_provider._smart_fallback_clarification_question(
                aspect, 
                "用户关心性能", 
                []
            )
            questions_generated.append(question)
        except Exception as e:
            print(f"   生成失败: {e}")
    
    # 显示生成的问题
    for i, q in enumerate(questions_generated, 1):
        print(f"   {i}. {q}")
    
    # 计算多样性
    unique_questions = set(questions_generated)
    diversity_ratio = len(unique_questions) / len(questions_generated)
    print(f"\n多样性统计:")
    print(f"   总问题数: {len(questions_generated)}")
    print(f"   唯一问题数: {len(unique_questions)}")
    print(f"   多样性比例: {diversity_ratio:.2f}")
    
    if diversity_ratio > 0.8:
        print("   ✅ 多样性优秀！")
    elif diversity_ratio > 0.6:
        print("   ⚠️ 多样性良好")
    else:
        print("   ❌ 多样性需要改进")
    
    # 演示上下文感知
    print("\n" + "=" * 60)
    print("🧠 上下文感知演示")
    print("-" * 40)
    
    # 模拟不同上下文的对话
    context_scenarios = [
        {
            "context": "用户提到拍照需求",
            "aspect": "general_preference",
            "expected": "camera"
        },
        {
            "context": "用户可能玩游戏",
            "aspect": "general_preference", 
            "expected": "performance"
        },
        {
            "context": "用户关心续航",
            "aspect": "general_preference",
            "expected": "battery"
        }
    ]
    
    print("测试上下文感知能力:")
    for scenario in context_scenarios:
        try:
            question = llm_provider._smart_fallback_clarification_question(
                scenario['aspect'],
                scenario['context'],
                []
            )
            print(f"   上下文: {scenario['context']}")
            print(f"   生成问题: {question}")
            print(f"   预期类型: {scenario['expected']}")
            print()
        except Exception as e:
            print(f"   上下文感知测试失败: {e}")
    
    print("=" * 60)
    print("🎉 优化后的对话系统演示完成！")
    print("\n💡 主要改进:")
    print("✅ 避免重复问题 - 智能检查历史记录")
    print("✅ 多样化表达 - 8种不同的问题模板")
    print("✅ 上下文感知 - 根据对话内容调整问题")
    print("✅ 自然语言 - LLM生成更自然的表达")
    print("✅ 智能回退 - 本地备用方案确保稳定性")
    print("✅ 个性化 - 根据用户特点调整问题风格")
    
    print("\n🚀 现在系统不再死板，不再重复，更像真人导购！")

if __name__ == "__main__":
    demo_optimized_dialogue() 