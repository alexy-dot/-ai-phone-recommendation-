#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试脚本
验证Ark API在项目中的工作
"""

import sys
import os
sys.path.append('.')

from services.llm_provider import LLMProvider, LLMConfig

def test_llm_integration():
    """测试LLM集成"""
    print("🔍 测试LLM集成...")
    
    # 创建LLM提供者
    llm_provider = LLMProvider()
    
    # 检查配置
    print(f"📡 API类型: {llm_provider.config.api_type}")
    print(f"🤖 模型: {llm_provider.config.model_name}")
    print(f"🌐 基础URL: {llm_provider.config.base_url}")
    
    # 检查可用性
    is_available = llm_provider.is_available()
    print(f"✅ LLM服务可用: {is_available}")
    
    if not is_available:
        print("❌ LLM服务不可用")
        return False
    
    # 测试意图理解
    print("\n🔍 测试意图理解...")
    user_input = "预算3000-4000，拍照优先"
    
    try:
        intent_result = llm_provider.understand_intent(user_input)
        print(f"✅ 意图理解成功")
        print(f"📊 结果: {intent_result}")
        
        # 检查关键字段
        if 'budget_min' in intent_result and 'budget_max' in intent_result:
            print(f"💰 预算范围: {intent_result['budget_min']} - {intent_result['budget_max']}")
        
        if 'preferences' in intent_result:
            print(f"🎯 偏好: {intent_result['preferences']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 意图理解失败: {e}")
        return False

def test_recommendation_explanation():
    """测试推荐解释生成"""
    print("\n🔍 测试推荐解释生成...")
    
    llm_provider = LLMProvider()
    
    try:
        explanation = llm_provider.generate_recommendation_explanation(
            phone_name="iPhone 15",
            reasons=["性能强劲", "拍照优秀", "系统流畅"],
            user_demand="预算3000-4000，拍照优先"
        )
        
        print(f"✅ 推荐解释生成成功")
        print(f"💬 解释: {explanation}")
        return True
        
    except Exception as e:
        print(f"❌ 推荐解释生成失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Ark API集成测试")
    print("=" * 50)
    
    # 测试LLM集成
    integration_success = test_llm_integration()
    
    # 测试推荐解释
    explanation_success = test_recommendation_explanation()
    
    print("\n" + "=" * 50)
    if integration_success and explanation_success:
        print("🎉 所有测试通过！Ark API集成成功！")
        print("\n💡 现在您可以运行主程序进行完整测试：")
        print("   python main_enhanced.py")
    else:
        print("❌ 部分测试失败，需要进一步检查。")

if __name__ == "__main__":
    main() 