import requests
import json

# 测试修复后的TestMemory功能
url = "http://localhost:8000/api/test/edge"

# 发送测试请求
response = requests.post(url, json={
    "page_url": "https://letcode.in/home"
})

print("状态码:", response.status_code)
print("响应头:", response.headers)

if response.status_code == 200:
    result = response.json()
    print("\n测试结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 检查test_memory结构
    if "test_memory" in result:
        print("\n✓ test_memory字段存在")
        test_memory = result["test_memory"]
        
        # 检查memory字段
        if "memory" in test_memory:
            print("✓ memory字段存在")
            memory = test_memory["memory"]
            
            # 检查各个子字段
            if "visited_pages" in memory:
                print(f"✓ visited_pages字段存在，数量: {len(memory['visited_pages'])}")
            else:
                print("✗ visited_pages字段不存在")
                
            if "completed_steps" in memory:
                print(f"✓ completed_steps字段存在，数量: {len(memory['completed_steps'])}")
            else:
                print("✗ completed_steps字段不存在")
                
            if "test_history" in memory:
                print(f"✓ test_history字段存在，数量: {len(memory['test_history'])}")
            else:
                print("✗ test_history字段不存在")
        else:
            print("✗ memory字段不存在")
    else:
        print("✗ test_memory字段不存在")
else:
    print("测试失败:", response.text)
