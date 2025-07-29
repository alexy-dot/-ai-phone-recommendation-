import os
import time
from openai import OpenAI

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key="168084fd-f4fd-463d-ac60-66d28a824fb5",
    timeout=120.0  # 增加超时时间到120秒
)

try:
    print("🔍 开始测试Ark API连接...")
    print(f"🌐 基础URL: {client.base_url}")
    print(f"🔑 API密钥: {client.api_key[:10]}...{client.api_key[-10:]}")
    
    start_time = time.time()
    
    completion = client.chat.completions.create(
        # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        model="doubao-1-5-pro-32k-250115",
        messages=[
            {"role": "system", "content": "你是人工智能助手"},
            {"role": "user", "content": "你好"},
        ],
    )
    
    end_time = time.time()
    print(f"⏱️ 请求耗时: {end_time - start_time:.2f}秒")
    print(f"✅ API请求成功！")
    print(f"💬 AI回复: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ API请求失败: {e}")
    print(f"🔧 错误类型: {type(e).__name__}")
    
    # 提供具体的错误处理建议
    if "timeout" in str(e).lower():
        print("💡 建议: 网络连接超时，请检查网络连接或尝试使用VPN")
    elif "connection" in str(e).lower():
        print("💡 建议: 网络连接失败，请检查网络设置")
    elif "authentication" in str(e).lower() or "401" in str(e):
        print("💡 建议: API密钥无效，请检查API密钥是否正确")
    else:
        print("💡 建议: 请检查API配置和网络连接")