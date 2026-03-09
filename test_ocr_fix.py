import requests
import json

# 测试修复后的OCR识别功能
url = "http://localhost:8000/api/test/edge"

# 发送测试请求
response = requests.post(url, json={
    "page_url": "https://letcode.in/home"
})

print("状态码:", response.status_code)

if response.status_code == 200:
    result = response.json()
    print("\n测试结果:")
    print(f"成功: {result.get('success')}")
    print(f"消息: {result.get('message')}")
    print(f"OCR识别结果数量: {len(result.get('ocr_results', []))}")
    print(f"执行的测试步骤数量: {len(result.get('test_steps', []))}")
    
    # 显示OCR识别结果
    if result.get('ocr_results'):
        print("\nOCR识别结果:")
        for idx, ocr_result in enumerate(result['ocr_results'][:10]):  # 只显示前10个
            print(f"{idx + 1}. 文本: {ocr_result['text']}, 位置: {ocr_result['position']}")
    
    # 显示测试步骤
    if result.get('test_steps'):
        print("\n执行的测试步骤:")
        for idx, step in enumerate(result['test_steps'][:10]):  # 只显示前10个
            print(f"{idx + 1}. {step['action']} - {step.get('text', 'N/A')}, 坐标: ({step.get('x', 0)}, {step.get('y', 0)})")
    
    # 检查AI是否生成了测试计划
    print(f"\nAI测试计划: {'成功' if len(result.get('test_steps', [])) > 1 else '失败，回退到传统方法'}")
else:
    print("测试失败:", response.text)
