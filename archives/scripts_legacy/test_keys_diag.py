import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_bothub(key, model="qwen-2.5-72b-instruct"):
    print(f"\n--- Testing Bothub with model {model} ---")
    url = "https://bothub.chat/api/v2/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    data = {"model": model, "messages": [{"role": "user", "content": "Ping"}], "max_tokens": 10}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Success: {resp.json()['choices'][0]['message']['content']}")
            return True
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
    return False

def test_dashscope(key, model="qwen-plus"):
    print(f"\n--- Testing DashScope (Alibaba) with model {model} ---")
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    data = {"model": model, "messages": [{"role": "user", "content": "Ping"}], "max_tokens": 10}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Success: {resp.json()['choices'][0]['message']['content']}")
            return True
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
    return False

def test_openrouter(key, model="qwen/qwen-2.5-72b-instruct"):
    print(f"\n--- Testing OpenRouter with model {model} ---")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    data = {"model": model, "messages": [{"role": "user", "content": "Ping"}], "max_tokens": 10}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Success: {resp.json()['choices'][0]['message']['content']}")
            return True
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
    return False

def test_siliconflow(key, model="Qwen/Qwen2.5-7b-Instruct"):
    print(f"\n--- Testing SiliconFlow with model {model} ---")
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    data = {"model": model, "messages": [{"role": "user", "content": "Ping"}], "max_tokens": 10}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Success: {resp.json()['choices'][0]['message']['content']}")
            return True
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
    return False

# 1. Test current QWEN_KEY (L33 override)
qwen_key_current = os.getenv("QWEN_KEY")
print(f"Current QWEN_KEY from .env: {qwen_key_current}")
test_bothub(qwen_key_current)
test_dashscope(qwen_key_current)
test_siliconflow(qwen_key_current)
test_openrouter(qwen_key_current)

# 2. Test the specific sk_ key from L26
with open('.env', 'r') as f:
    lines = f.readlines()
    l26_key = next((l.split('=')[1].strip() for l in lines if 'sk_u7zL' in l), None)

if l26_key:
    print(f"\nTesting specific sk_ key from L26: {l26_key[:10]}...")
    test_dashscope(l26_key)
    test_bothub(l26_key)
    test_siliconflow(l26_key)

# 3. Test OpenRouter Qwen Key
or_key = os.getenv("OPEN_ROUTER_QWEN_KEY")
if or_key:
    test_openrouter(or_key)
