import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("QWEN_KEY")
print(f"Testing key: {key[:10]}...{key[-4:]}")

PROVIDERS = [
    {
        "name": "DashScope (Alibaba)",
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model": "qwen-turbo"
    },
    {
        "name": "SiliconFlow",
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "model": "Qwen/Qwen2.5-7B-Instruct"
    },
    {
        "name": "DeepSeek",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat"
    },
    {
        "name": "Together AI",
        "url": "https://api.together.xyz/v1/chat/completions",
        "model": "mistralai/Mistral-7B-Instruct-v0.1"
    },
    {
        "name": "OpenRouter",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "qwen/qwen-2-7b-instruct:free"
    },
    {
        "name": "Groq (Unexpected format)",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama3-8b-8192"
    },
    {
      "name": "Mistral AI",
      "url": "https://api.mistral.ai/v1/chat/completions",
      "model": "mistral-tiny"
    }
]

for p in PROVIDERS:
    print(f"\nTargeting {p['name']}...")
    try:
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {"model": p["model"], "messages": [{"role": "user", "content": "Ping"}], "max_tokens": 5}
        resp = requests.post(p["url"], headers=headers, json=data, timeout=5)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"✅ SUCCESS! Response: {resp.json()['choices'][0]['message']['content']}")
            break
        else:
            print(f"❌ FAILED: {resp.text[:200]}")
    except Exception as e:
        print(f"⚠️ EXCEPTION: {e}")
