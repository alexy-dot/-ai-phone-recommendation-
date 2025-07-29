#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连接测试脚本
"""

import json
import os
from openai import OpenAI

def test_api_connection():
    """测试API连接"""
    print("🧪 开始API连接测试...")
    
    # 1. 检查配置文件
    print("\n1️⃣ 检查配置文件...")
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 配置文件存在")
        print(f"🔑 API密钥: {config.get('ARK_API_KEY', '未找到')[:8]}...")
        print(f"🤖 模型: {config.get('LLM_MODEL_NAME', '未找到')}")
        print(f"🌐 地址: {config.get('LLM_BASE_URL', '未找到')}")
    else:
        print("❌ 配置文件不存在")
        return False
    
    # 2. 测试API连接
    print("\n2️⃣ 测试API连接...")
    try:
        client = OpenAI(
            base_url=config.get('LLM_BASE_URL'),
            api_key=config.get('ARK_API_KEY'),
        )
        
        response = client.chat.completions.create(
            model=config.get('LLM_MODEL_NAME'),
            messages=[
                {"role": "system", "content": "你是一个测试助手，请简单回复'连接成功'"},
                {"role": "user", "content": "测试连接"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API连接成功")
        print(f"🤖 回复: {result}")
        return True
        
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def test_system_components():
    """测试系统组件"""
    print("\n3️⃣ 测试系统组件...")
    
    try:
        # 测试数据库
        from database.database import DatabaseManager
        db = DatabaseManager()
        phones = db.get_all_phones()
        print(f"✅ 数据库连接成功，共{len(phones)}款手机")
        
        # 测试LLM服务
        from services.llm_provider import LLMProvider
        llm = LLMProvider()
        if llm.is_available():
            print("✅ LLM服务可用")
        else:
            print("❌ LLM服务不可用")
            
        # 测试推荐引擎
        from core.recommendation_engine import RecommendationEngine
        engine = RecommendationEngine()
        print("✅ 推荐引擎初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统组件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("🤖 大模型驱动智能推荐系统 - API测试")
    print("=" * 50)
    
    # 测试API连接
    api_ok = test_api_connection()
    
    # 测试系统组件
    system_ok = test_system_components()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"🔗 API连接: {'✅ 正常' if api_ok else '❌ 异常'}")
    print(f"🔧 系统组件: {'✅ 正常' if system_ok else '❌ 异常'}")
    
    if api_ok and system_ok:
        print("\n🎉 所有测试通过！系统可以正常使用")
        print("\n💡 下一步可以运行:")
        print("   python main_ai_driven.py test '你好'")
        print("   python main_ai_driven.py")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 