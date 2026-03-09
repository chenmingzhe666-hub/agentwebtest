import requests
import json

# 测试新的纯视觉AI测试流程
url = "http://localhost:8000/api/test/edge"

# 发送测试请求
response = requests.post(url, json={
    "page_url": "https://letcode.in/home"
})

print("状态码:", response.status_code)

if response.status_code == 200:
    result = response.json()
    print("\n=== 测试结果 ===")
    print(f"成功: {result.get('success')}")
    print(f"消息: {result.get('message')}")
    print(f"页面标题: {result.get('page_info', {}).get('title', 'N/A')}")
    print(f"OCR识别结果数量: {len(result.get('ocr_results', []))}")
    print(f"执行的测试步骤数量: {len(result.get('test_steps', []))}")
    print(f"所有页面截图数量: {len(result.get('all_screenshots', []))}")
    
    # 显示OCR识别结果（现在只是可选的）
    if result.get('ocr_results'):
        print(f"\n=== OCR识别结果（仅用于显示）===")
        for idx, ocr_result in enumerate(result['ocr_results'][:5]):  # 只显示前5个
            print(f"{idx + 1}. 文本: {ocr_result['text']}, 位置: {ocr_result['position']}")
    
    # 显示测试步骤
    if result.get('test_steps'):
        print(f"\n=== AI生成的测试步骤 ===")
        for idx, step in enumerate(result['test_steps'][:15]):  # 显示前15个
            print(f"{idx + 1}. {step['action']} - {step.get('text', 'N/A')}, 坐标: ({step.get('x', 0)}, {step.get('y', 0)})")
            if step.get('description'):
                print(f"   描述: {step['description']}")
    
    # 显示测试记忆
    if result.get('test_memory'):
        print(f"\n=== 测试记忆 ===")
        memory = result['test_memory']
        print(f"访问过的页面数量: {len(memory.get('visited_pages', []))}")
        print(f"完成的测试步骤数量: {len(memory.get('completed_steps', []))}")
        print(f"测试历史记录数量: {len(memory.get('test_history', []))}")
    
    # 检查AI是否生成了测试计划
    test_steps_count = len(result.get('test_steps', []))
    print(f"\n=== 总结 ===")
    if test_steps_count > 1:
        print(f"✓ AI测试计划生成成功！生成了 {test_steps_count} 个智能测试步骤")
        print("✓ 系统现在直接使用Qwen3-VL模型分析截图，不依赖OCR")
    else:
        print("✗ AI测试计划生成失败，使用了默认测试步骤")
else:
    print("测试失败:", response.text)
