import cv2
import numpy as np
from paddleocr import PaddleOCR

# 初始化OCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# 读取最新的截图
screenshot_path = r"E:\agent自动测试web\test_results\edge_screenshot_20260308_224059.png"
image = cv2.imread(screenshot_path)

if image is None:
    print("无法读取截图文件")
else:
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
                print(f"  位置: {bbox}")
    else:
        print("OCR识别结果为空")
