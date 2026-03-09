# -*- coding: utf-8 -*-
# Edge页面自动化测试工具后端主应用
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uvicorn
import requests
import base64
import json
import os
import time
from PIL import ImageGrab
# 不再使用cv2和numpy，直接使用PIL处理截图
# import cv2
# import numpy as np

# 导入模块
from src.task import TaskManager
# 不再使用OCR识别器，直接使用AI模型分析截图
# from src.recognize import OCRRecognizer

# 创建FastAPI应用
app = FastAPI(
    title="Edge页面自动化测试工具",
    description="用于测试当前打开的Edge页面的自动化工具",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化任务管理器
task_manager = TaskManager()

# 不再使用OCR识别器，直接使用AI模型分析截图
# ocr_recognizer = OCRRecognizer()

# 测试记忆系统
class TestMemory:
    """测试记忆系统，记录测试过的页面和操作"""
    
    def __init__(self):
        self.memory = {
            "visited_pages": [],  # 访问过的页面
            "completed_steps": [],  # 完成的测试步骤
            "current_page": None,  # 当前页面信息
            "test_history": []  # 测试历史
        }
    
    def add_visited_page(self, page_info):
        """添加访问过的页面"""
        self.memory["visited_pages"].append(page_info)
        self.memory["current_page"] = page_info
    
    def add_completed_step(self, step):
        """添加完成的测试步骤"""
        self.memory["completed_steps"].append(step)
    
    def add_test_history(self, test_info):
        """添加测试历史"""
        self.memory["test_history"].append(test_info)
    
    def get_memory(self):
        """获取记忆"""
        return self.memory
    
    def clear(self):
        """清空记忆"""
        self.memory = {
            "visited_pages": [],
            "completed_steps": [],
            "current_page": None,
            "test_history": []
        }

# 创建测试记忆实例
test_memory = TestMemory()

# 辅助函数：将百分比坐标转换为实际屏幕坐标
def convert_percent_coords_to_screen(percent_x, percent_y, screen_width, screen_height):
    """将百分比坐标转换为实际屏幕坐标"""
    try:
        # 确保百分比值在0-100之间
        percent_x = max(0, min(100, percent_x))
        percent_y = max(0, min(100, percent_y))
        
        # 转换为实际屏幕坐标
        screen_x = int((percent_x / 100) * screen_width)
        screen_y = int((percent_y / 100) * screen_height)
        
        return screen_x, screen_y
    except Exception as e:
        print(f"坐标转换失败: {e}")
        # 回退到屏幕中心
        return screen_width // 2, screen_height // 2

# Qwen3-VL模型接口
def get_ai_test_plan(screenshot_path):
    """使用Qwen3-VL模型生成智能测试计划"""
    try:
        # 读取截图文件并转换为base64
        with open(screenshot_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # 构建Ollama API请求
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        
        # 构建提示词
        prompt = '你是一个Web自动化测试专家。请直接分析截图，生成详细的测试步骤。\n\n请生成一个完整的测试流程，包括：\n1. 分析当前页面的功能和结构\n2. 识别页面中的所有可交互元素，特别是页面中的三个"CLICK ME"按钮\n3. 对于每个按钮元素，精确定位其中心点位置\n4. 生成测试步骤，依次点击每个"CLICK ME"按钮\n5. 对于每个按钮点击后可能弹出的对话框，生成关闭对话框的测试步骤\n6. 确保测试步骤覆盖所有按钮元素\n7. 确保生成的坐标能够精确点击到按钮的中心点\n\n请严格按照以下JSON格式输出测试步骤，不要添加任何其他文本：\n{\n  "test_steps": [\n    {\n      "action": "click",\n      "x": 50,\n      "y": 50,\n      "text": "登录按钮",\n      "description": "点击登录按钮"\n    }\n  ]\n}\n\n支持的操作类型：click, type, scroll, tab, clear, get_attribute, is_enabled, is_readonly\n\n请确保输出的坐标是相对于截图的百分比坐标，其中x和y的范围都是0-100，分别表示从截图左边缘和上边缘到目标元素中心点的百分比距离。例如，截图中心的坐标应该是(50, 50)。这样可以确保坐标在不同屏幕分辨率下都能正确映射。\n\n特别注意：\n1. 请生成至少3个测试步骤，每个步骤点击一个不同的"CLICK ME"按钮\n2. 请确保生成的坐标能够准确点击到每个"CLICK ME"按钮的中心点\n3. 请为每个按钮点击后可能弹出的对话框生成关闭步骤'  
        
        data = {
            "model": "qwen3-vl:8b",
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "format": "json"
        }
        
        print("正在调用Qwen3-VL模型生成测试计划...")
        
        # 发送请求，设置合理的超时时间以确保模型有足够时间处理图像
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 从thinking字段获取AI生成的内容
        ai_response = result.get("thinking", "")
        print(f"AI思考内容长度: {len(ai_response)} 字符")
        
        # 尝试提取JSON部分
        try:
            # 查找JSON的开始和结束位置
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                print(f"提取的JSON: {json_str[:500]}...")
                
                ai_result = json.loads(json_str)
                if "test_steps" in ai_result:
                    print(f"AI生成了 {len(ai_result['test_steps'])} 个测试步骤")
                    return ai_result["test_steps"]
        except Exception as e:
            print(f"解析AI响应失败: {e}")
        
        print("AI测试计划生成失败，回退到传统方法...")
        return []
    except requests.exceptions.Timeout:
        print("Qwen3-VL模型调用超时，回退到传统方法...")
        return []
    except Exception as e:
        print(f"调用Qwen3-VL模型失败: {e}")
        return []

# 数据模型
class TestEdgeRequest(BaseModel):
    """测试Edge页面请求模型"""
    page_url: Optional[str] = None

# 根路径
@app.get("/")
def root():
    """根路径"""
    return {
        "message": "Edge页面自动化测试工具",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}

# 提供截图文件访问
@app.get("/api/screenshots/{filename}")
def get_screenshot(filename: str):
    """获取测试页面截图"""
    import os
    from fastapi.responses import FileResponse
    
    # 获取项目根目录
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    # 截图存储目录
    test_results_dir = os.path.join(project_root, "test_results")
    screenshot_path = os.path.join(test_results_dir, filename)
    
    if os.path.exists(screenshot_path):
        return FileResponse(screenshot_path)
    else:
        raise HTTPException(status_code=404, detail="Screenshot not found")

# 直接测试Edge页面的API
@app.post("/api/test/edge")
def test_edge_page(request: TestEdgeRequest):
    """直接测试当前打开的Edge页面"""
    try:
        page_url = request.page_url
        print("开始测试Edge页面...")
        print(f"测试页面URL: {page_url}")
        
        # 1. 激活Edge窗口
        print("获取控制单元...")
        control_unit = TaskManager()._get_control_unit()
        
        # 2. 如果提供了URL，先导航到目标页面
        if page_url:
            print(f"导航到目标页面: {page_url}")
            # 激活Edge浏览器（假设Edge是默认浏览器）
            import subprocess
            subprocess.run(["start", "microsoft-edge:" + page_url], shell=True)
            time.sleep(3)  # 等待页面加载
        
        # 3. 抓取当前屏幕（现在应该是目标页面）
        print("抓取屏幕截图...")
        screenshot = ImageGrab.grab()
        
        # 获取当前鼠标位置
        import ctypes
        user32 = ctypes.windll.user32
        class POINT(ctypes.Structure):
            _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]
        point = POINT()
        user32.GetCursorPos(ctypes.byref(point))
        mouse_x, mouse_y = point.x, point.y
        print(f"当前鼠标位置: ({mouse_x}, {mouse_y})")
        
        # 在截图上绘制鼠标指针
        from PIL import ImageDraw
        draw = ImageDraw.Draw(screenshot)
        # 绘制鼠标指针（红色圆圈）
        radius = 10
        draw.ellipse([(mouse_x - radius, mouse_y - radius), (mouse_x + radius, mouse_y + radius)], outline="red", width=2)
        # 绘制鼠标指针的十字线
        cross_length = 15
        draw.line([(mouse_x - cross_length, mouse_y), (mouse_x + cross_length, mouse_y)], fill="red", width=2)
        draw.line([(mouse_x, mouse_y - cross_length), (mouse_x, mouse_y + cross_length)], fill="red", width=2)
        
        # 4. 保存截图用于分析
        # 获取项目根目录
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        # 创建测试结果目录
        test_results_dir = os.path.join(project_root, "test_results")
        if not os.path.exists(test_results_dir):
            os.makedirs(test_results_dir)
        
        # 生成截图文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"edge_screenshot_{timestamp}.png"
        screenshot_path = os.path.join(test_results_dir, screenshot_filename)
        
        # 直接使用PIL保存截图
        screenshot.save(screenshot_path)
        print(f"截图已成功保存到: {screenshot_path}")
        print(f"截图文件大小: {os.path.getsize(screenshot_path)} 字节")
        print(f"鼠标位置已标记在截图上: ({mouse_x}, {mouse_y})")
        
        # 5. 跳过OCR识别，直接使用AI模型分析截图
        print("跳过OCR识别，直接使用AI模型分析截图...")
        ocr_results = []
        formatted_ocr_results = []
        
        # 6. 直接使用AI模型分析页面内容，规划测试步骤
        print("使用AI模型分析页面内容，规划测试步骤...")
        test_steps = []
        
        # 使用Qwen3-VL模型生成智能测试计划（不依赖OCR）
        ai_test_steps = get_ai_test_plan(screenshot_path)
        
        if len(ai_test_steps) > 0:
            # 使用AI生成的测试步骤
            test_steps = ai_test_steps
            for step in test_steps:
                print(f"AI添加测试步骤: {step['action']} - {step['text']}，坐标: ({step['x']}, {step['y']})")
        else:
            # 回退到简单的默认测试步骤
            print("AI测试计划生成失败，使用默认测试步骤...")
            # 使用默认的测试步骤，点击页面中心
            screen_width, screen_height = screenshot.size
            center_x = screen_width // 2
            center_y = screen_height // 2
            test_steps.append({"action": "click", "x": center_x, "y": center_y, "text": "页面中心", "description": "点击页面中心"})
            print(f"添加默认测试步骤: 点击页面中心，坐标: ({center_x}, {center_y})")
        
        # 7. 执行测试步骤
        print("执行测试步骤...")
        execution_results = []
        all_screenshots = []  # 存储所有页面的截图
        
        # 获取截图大小
        screenshot_width, screenshot_height = screenshot.size
        print(f"截图大小: {screenshot_width}x{screenshot_height}")
        
        # 获取实际屏幕分辨率
        import ctypes
        user32 = ctypes.windll.user32
        actual_screen_width = user32.GetSystemMetrics(0)
        actual_screen_height = user32.GetSystemMetrics(1)
        print(f"实际屏幕分辨率: {actual_screen_width}x{actual_screen_height}")
        
        # 使用实际屏幕分辨率进行坐标转换
        screen_width, screen_height = actual_screen_width, actual_screen_height
        
        # 分析截图中的鼠标指针标记位置
        def detect_mouse_pointer(image, mouse_pos):
            """检测截图中的鼠标指针标记位置"""
            try:
                # 这里可以使用更复杂的图像处理方法来检测鼠标指针标记
                # 目前我们使用之前获取的鼠标位置
                return mouse_pos
            except Exception as e:
                print(f"检测鼠标指针失败: {e}")
                return None
        
        # 初始鼠标指针位置
        mouse_pointer_pos = detect_mouse_pointer(screenshot, (mouse_x, mouse_y))
        if mouse_pointer_pos:
            print(f"初始鼠标指针位置: ({mouse_pointer_pos[0]}, {mouse_pointer_pos[1]})")
        
        for step in test_steps:
            action = step.get("action", "click").lower()  # 转换为小写以支持大小写不敏感
            x = step.get("x", 50)  # 默认值设为50（屏幕中心）
            y = step.get("y", 50)  # 默认值设为50（屏幕中心）
            text = step.get("text", "未知目标")
            
            # 检查坐标范围，如果已经是实际屏幕坐标（大于100），则直接使用
            if x > 100 or y > 100:
                print(f"使用原始坐标: ({x}, {y})")
                screen_x, screen_y = x, y
            else:
                # 转换百分比坐标为实际屏幕坐标
                screen_x, screen_y = convert_percent_coords_to_screen(x, y, screen_width, screen_height)
                print(f"坐标转换: ({x}, {y}) -> ({screen_x}, {screen_y})")
            
            # 不使用鼠标指针位置进行校准，以确保每个测试步骤使用独立的坐标
            # 这样可以避免所有测试步骤都使用相同的坐标
            
            # 更新步骤中的坐标为实际屏幕坐标
            step['x'] = screen_x
            step['y'] = screen_y
            x, y = screen_x, screen_y
            
            if action == "click":
                print(f"执行点击操作: {text}，坐标: ({x}, {y})")
                success = control_unit.click(x, y)
                execution_results.append({"step": step, "success": success})
                time.sleep(2)  # 等待页面响应，增加等待时间以确保页面切换完成
                
                # 检查是否弹出了对话框（如Congratulations!）
                print("检查是否弹出了对话框...")
                # 尝试点击对话框的关闭按钮
                # 对话框关闭按钮通常在右上角，坐标大约在屏幕中心偏上
                close_button_x = screen_width // 2
                close_button_y = screen_height // 4
                print(f"尝试点击对话框关闭按钮，坐标: ({close_button_x}, {close_button_y})")
                control_unit.click(close_button_x, close_button_y)
                time.sleep(1)  # 等待对话框关闭
                
                # 页面可能已切换，重新截图
                print("页面可能已切换，重新截图...")
                new_screenshot = ImageGrab.grab()
                
                # 获取当前鼠标位置
                user32 = ctypes.windll.user32
                point = POINT()
                user32.GetCursorPos(ctypes.byref(point))
                mouse_x, mouse_y = point.x, point.y
                print(f"当前鼠标位置: ({mouse_x}, {mouse_y})")
                
                # 在截图上绘制鼠标指针
                draw = ImageDraw.Draw(new_screenshot)
                # 绘制鼠标指针（红色圆圈）
                radius = 10
                draw.ellipse([(mouse_x - radius, mouse_y - radius), (mouse_x + radius, mouse_y + radius)], outline="red", width=2)
                # 绘制鼠标指针的十字线
                cross_length = 15
                draw.line([(mouse_x - cross_length, mouse_y), (mouse_x + cross_length, mouse_y)], fill="red", width=2)
                draw.line([(mouse_x, mouse_y - cross_length), (mouse_x, mouse_y + cross_length)], fill="red", width=2)
                
                new_timestamp = time.strftime("%Y%m%d_%H%M%S")
                new_screenshot_filename = f"edge_screenshot_{new_timestamp}.png"
                new_screenshot_path = os.path.join(test_results_dir, new_screenshot_filename)
                new_screenshot.save(new_screenshot_path)
                all_screenshots.append({
                    "filename": new_screenshot_filename,
                    "path": new_screenshot_path,
                    "timestamp": new_timestamp,
                    "mouse_position": (mouse_x, mouse_y)
                })
                print(f"新页面截图已保存到: {new_screenshot_path}")
                print(f"鼠标位置已标记在截图上: ({mouse_x}, {mouse_y})")
            elif action == "type" or action == "input" or action == "send_keys" or action == "sendKeys":
                print(f"执行输入操作: {text}，坐标: ({x}, {y})")
                # 先点击输入框
                control_unit.click(x, y)
                time.sleep(0.5)
                # 然后输入文本
                input_text = "test"
                if "content" in step:
                    input_text = step["content"]
                elif "value" in step:
                    input_text = step["value"]
                elif "text" in step:
                    # 直接使用text字段作为输入内容
                    input_text = step["text"]
                print(f"输入内容: {input_text}")
                success = control_unit.type_text(input_text)
                execution_results.append({"step": step, "success": success})
                time.sleep(1)
            elif action == "scroll":
                print(f"执行滚动操作: {text}")
                # 滚动鼠标滚轮
                success = control_unit.scroll(100)  # 向上滚动
                execution_results.append({"step": step, "success": success})
                time.sleep(1)
            elif action == "tab" or action == "key":
                print(f"执行按键操作: {text}")
                # 模拟按键
                if action == "tab":
                    success = control_unit.press_key("tab")
                elif "key" in step:
                    success = control_unit.press_key(step["key"])
                else:
                    success = control_unit.press_key("tab")
                execution_results.append({"step": step, "success": success})
                time.sleep(1)
            elif action == "clear":
                print(f"执行清除操作: {text}，坐标: ({x}, {y})")
                # 先点击输入框
                control_unit.click(x, y)
                time.sleep(0.5)
                # 全选文本
                control_unit.press_key("ctrl+a")
                time.sleep(0.3)
                # 删除文本
                control_unit.press_key("delete")
                execution_results.append({"step": step, "success": True})
                time.sleep(1)
            elif action == "get_attribute" or action == "getAttribute" or action == "is_enabled" or action == "isEnabled" or action == "is_readonly" or action == "isReadonly":
                print(f"执行验证操作: {text}，坐标: ({x}, {y})")
                # 点击元素以获取焦点
                control_unit.click(x, y)
                time.sleep(0.5)
                # 验证操作（这里只是模拟验证）
                execution_results.append({"step": step, "success": True})
                time.sleep(1)
            else:
                print(f"未知操作类型: {action}，回退到点击操作")
                # 回退到点击操作
                success = control_unit.click(x, y)
                execution_results.append({"step": step, "success": success})
                time.sleep(1)
            
            # 添加完成的步骤到记忆系统
            test_memory.add_completed_step(step)
        
        # 8. 保留截图文件供前端访问
        print(f"截图文件已保存并保留: {screenshot_path}")
        
        print("Edge页面测试完成")
        
        # 获取页面信息
        import ctypes
        user32 = ctypes.windll.user32
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(user32.GetForegroundWindow(), buf, 256)
        window_title = buf.value
        
        page_info = {
            "title": window_title,
            "url": page_url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "screenshot_taken": True,
            "screenshot_path": screenshot_filename,
            "screenshot_full_path": screenshot_path
        }
        
        # 添加页面信息到记忆系统
        test_memory.add_visited_page(page_info)
        
        # 添加测试历史到记忆系统
        test_history = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "page_info": page_info,
            "test_steps": test_steps,
            "execution_results": execution_results,
            "screenshots": all_screenshots
        }
        test_memory.add_test_history(test_history)
        
        return {
            "success": True,
            "message": "Edge页面测试完成",
            "page_info": page_info,
            "ocr_results": formatted_ocr_results,
            "test_steps": test_steps,
            "execution_results": execution_results,
            "all_screenshots": all_screenshots,
            "test_memory": test_memory.get_memory()
        }
    except Exception as e:
        print(f"测试Edge页面失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )