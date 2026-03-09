import requests
import json

# 测试Ollama API
url = "http://localhost:11434/api/generate"
headers = {"Content-Type": "application/json"}
data = {
    "model": "qwen3-vl:8b",
    "prompt": "Hello",
    "stream": False
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")
