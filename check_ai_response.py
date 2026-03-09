import requests
import json

# 构建Ollama API请求
url = "http://localhost:11434/api/generate"
headers = {"Content-Type": "application/json"}

# 不使用图像，直接测试文本响应
prompt = "你是一个Web自动化测试专家。请生成一个测试登录页面的测试步骤。请严格按照以下JSON格式输出测试步骤，不要添加任何其他文本：{\"test_steps\": [{\"action\": \"click\", \"x\": 50, \"y\": 50, \"text\": \"登录按钮\", \"description\": \"点击登录按钮\"}]}"

data = {
    "model": "qwen3-vl:8b",
    "prompt": prompt,
    "stream": False,
    "format": "json"
}

print("测试Ollama API...")
try:
    response = requests.post(url, headers=headers, json=data, timeout=60)
    response.raise_for_status()
    print(f"响应状态码: {response.status_code}")
    result = response.json()
    
    # 检查thinking字段
    if "thinking" in result:
        ai_response = result["thinking"]
        print(f"AI思考内容长度: {len(ai_response)} 字符")
        print(f"AI思考内容: {ai_response}")
        
        # 尝试提取JSON部分
        try:
            # 查找JSON的开始和结束位置
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                print(f"提取的JSON: {json_str}")
                
                ai_result = json.loads(json_str)
                if "test_steps" in ai_result:
                    print(f"AI生成了 {len(ai_result['test_steps'])} 个测试步骤")
                    for step in ai_result['test_steps']:
                        print(f"步骤: {step}")
        except Exception as e:
            print(f"解析JSON失败: {e}")
    else:
        print("响应中没有thinking字段")
        print(f"完整响应: {result}")
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()