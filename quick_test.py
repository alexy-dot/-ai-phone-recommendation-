#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证修改效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.llm_orchestrator import LLMOrchestrator

def test_llm_orchestrator():
    """测试LLM编排器"""
    print("🧪 测试LLM编排器...")
    
    try:
        # 初始化编排器
        orchestrator = LLMOrchestrator()
        print("✅ LLM编排器初始化成功")
        
        # 测试简单处理
        session_id = "test_session"
        user_input = "你好"
        
        print(f"📝 测试输入: {user_input}")
        
        # 调用处理函数
        response = orchestrator.process_user_input(user_input, session_id)
        
        print(f"✅ 处理成功")
        print(f"🤖 回复: {response.message}")
        
        if response.clarification_question:
            print(f"❓ 澄清问题: {response.clarification_question}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🚀 快速测试 - 验证修改效果")
    print("=" * 50)
    
    success = test_llm_orchestrator()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试通过！修改成功")
        print("💡 现在可以正常使用 main_ai_driven.py")
    else:
        print("❌ 测试失败，需要进一步调试")
    print("=" * 50)

if __name__ == "__main__":
    main() 