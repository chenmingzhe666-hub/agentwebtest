import requests
import json
import time

# 测试API的Python脚本
url = "http://localhost:8000/api/test/edge"
headers = {"Content-Type": "application/json"}
data = {
    "page_url": "https://webdriveruniversity.com/Click-Buttons/index.html"
}

try:
    print("开始测试API...")
    print(f"发送请求到: {url}")
    print(f"请求数据: {json.dumps(data, indent=2)}")
    
    start_time = time.time()
    response = requests.post(url, headers=headers, json=data, timeout=120)  # 增加超时时间到120秒
    end_time = time.time()
    
    print(f"请求耗时: {end_time - start_time:.2f} 秒")
    print(f"响应状态码: {response.status_code}")
    
    response.raise_for_status()
    result = response.json()
    
    print("\n测试成功！")
    print(f"测试状态: {'成功' if result['success'] else '失败'}")
    print(f"测试消息: {result['message']}")
    print(f"执行的测试步骤数量: {len(result['test_steps'])}")
    print("\n执行的测试步骤:")
    for step in result['test_steps']:
        print(f"- {step['action']} - {step.get('text', '未知目标')} - 坐标: ({step.get('x', 'N/A')}, {step.get('y', 'N/A')})")
    print("\n测试记忆:")
    print(f"访问过的页面数量: {len(result['test_memory']['visited_pages'])}")
    print(f"完成的测试步骤数量: {len(result['test_memory']['completed_steps'])}")
    
    # 打印页面信息
    if 'page_info' in result:
        print("\n页面信息:")
        print(f"页面标题: {result['page_info'].get('title', '未知')}")
        print(f"页面URL: {result['page_info'].get('url', '未知')}")
        print(f"截图文件名: {result['page_info'].get('screenshot_path', '未知')}")
        print(f"截图时间: {result['page_info'].get('timestamp', '未知')}")
    
    # 打印所有截图信息
    if 'all_screenshots' in result and len(result['all_screenshots']) > 0:
        print("\n所有截图:")
        for i, screenshot in enumerate(result['all_screenshots']):
            print(f"截图 {i+1}: {screenshot['filename']} - {screenshot['timestamp']}")
            if 'mouse_position' in screenshot:
                print(f"  鼠标位置: ({screenshot['mouse_position'][0]}, {screenshot['mouse_position'][1]})")
except Exception as e:
    print(f"\n测试失败: {e}")
    import traceback
    traceback.print_exc()
