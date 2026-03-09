import cv2
import numpy as np
from paddleocr import PaddleOCR
import os

# 初始化OCR
ocr = PaddleOCR(use_textline_orientation=True, lang='ch')

# 读取最新的截图
test_results_dir = r"E:\agent自动测试web\test_results"
screenshots = [f for f in os.listdir(test_results_dir) if f.endswith('.png')]
latest_screenshot = sorted(screenshots)[-1]
screenshot_path = os.path.join(test_results_dir, latest_screenshot)

print(f"测试截图: {latest_screenshot}")
print(f"完整路径: {screenshot_path}")

# 使用PIL读取图像
from PIL import Image
try:
    pil_image = Image.open(screenshot_path)
    image = np.array(pil_image)
    print(f"截图尺寸: {image.shape}")
    
    # 执行OCR识别
    print("开始OCR识别...")
    ocr_results = ocr.ocr(image, cls=True)
    
    if ocr_results:
        print(f"识别到 {len(ocr_results)} 行文本")
        for line_idx, line in enumerate(ocr_results):
            print(f"\n第 {line_idx + 1} 行:")
            for word_info in line:
                text = word_info[1][0]
                confidence = word_info[1][1]
                bbox = word_info[0]
                print(f"  文本: {text}")
                print(f"  置信度: {confidence}")
    else:
        print("OCR识别结果为空")
except Exception as e:
    print(f"OCR识别失败: {e}")
    import traceback
    traceback.print_exc()
