#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Ark API测试
"""

import requests
import json
import time

def test_ark_api_simple():
    """简单的Ark API测试"""
    print("🔍 开始简单Ark API测试...")
    
    # API配置
    base_url = "https://ark.cn-beijing.volces.com/api/v3"
    api_key = "168084fd-f4fd-463d-ac60-66d28a824fb5"
    model = "doubao-1-5-pro-32k-250115"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "你好，请简单回复'测试成功'"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        print(f"🌐 发送请求到: {base_url}/chat/completions")
        print(f"🤖 使用模型: {model}")
        
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        end_time = time.time()
        print(f"⏱️ 请求耗时: {end_time - start_time:.2f}秒")
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API请求成功！")
            print(f"📄 响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if 'choices' in result and result['choices']:
                content = result['choices'][0]['message']['content']
                print(f"💬 AI回复: {content}")
                return True
            else:
                print("❌ 响应格式异常")
                return False
        else:
            print(f"❌ API请求失败")
            print(f"📄 错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

if __name__ == "__main__":
    success = test_ark_api_simple()
    if success:
        print("\n�� 测试成功！")
    else:
        print("\n❌ 测试失败")
