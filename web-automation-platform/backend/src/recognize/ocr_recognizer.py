# OCR识别器
import cv2
import numpy as np
from .recognizer import Recognizer

class OCRRecognizer(Recognizer):
    """OCR识别器，用于识别文本内容"""
    
    def __init__(self):
        """初始化OCR识别器"""
        super().__init__()
        try:
            # 导入PaddleOCR
            from paddleocr import PaddleOCR
            # 初始化OCR，使用中英文模型
            self.ocr = PaddleOCR(use_textline_orientation=True, lang='ch')
            self.available = True
        except ImportError:
            print("警告: 无法导入PaddleOCR，OCR功能不可用")
            self.available = False
    
    def recognize(self, image: np.ndarray, region: dict = None, 
                 keywords: list = None, min_confidence: float = 0.5) -> list:
        """执行OCR识别
        
        Args:
            image: 输入图像
            region: 识别区域 {x, y, width, height}
            keywords: 关键词过滤列表
            min_confidence: 最小置信度
            
        Returns:
            list: 识别结果列表
        """
        results = []
        
        if not self.available:
            return results
        
        try:
            # 裁剪识别区域
            if region:
                x, y, w, h = region['x'], region['y'], region['width'], region['height']
                image = image[y:y+h, x:x+w]
            
            # 执行OCR识别
            ocr_results = self.ocr.ocr(image)
            
            if ocr_results:
                for line in ocr_results:
                    for word_info in line:
                        # 获取文本和位置
                        text = word_info[1][0]
                        confidence = word_info[1][1]
                        bbox = word_info[0]
                        
                        # 过滤低置信度结果
                        if confidence < min_confidence:
                            continue
                        
                        # 过滤关键词
                        if keywords and text not in keywords:
                            continue
                        
                        # 计算边界框
                        x1, y1 = int(bbox[0][0]), int(bbox[0][1])
                        x2, y2 = int(bbox[2][0]), int(bbox[2][1])
                        width = x2 - x1
                        height = y2 - y1
                        
                        # 计算中心坐标
                        center_x = x1 + width // 2
                        center_y = y1 + height // 2
                        
                        # 如果指定了识别区域，需要调整坐标
                        if region:
                            center_x += region['x']
                            center_y += region['y']
                        
                        results.append({
                            'type': 'ocr',
                            'text': text,
                            'x': center_x,
                            'y': center_y,
                            'width': width,
                            'height': height,
                            'score': confidence,
                            'rect': {'x': x1, 'y': y1, 'width': width, 'height': height}
                        })
            
        except Exception as e:
            print(f"OCR识别失败: {e}")
        
        return results
    
    def recognize_text(self, image: np.ndarray) -> str:
        """识别图像中的所有文本
        
        Args:
            image: 输入图像
            
        Returns:
            str: 识别的文本
        """
        if not self.available:
            return ""
        
        try:
            # 执行OCR识别
            ocr_results = self.ocr.ocr(image)
            
            text = ""
            if ocr_results:
                for line in ocr_results:
                    for word_info in line:
                        text += word_info[1][0] + " "
            
            return text.strip()
        except Exception as e:
            print(f"文本识别失败: {e}")
            return ""
    
    def find_text(self, image: np.ndarray, text: str, 
                 region: dict = None, min_confidence: float = 0.5) -> dict:
        """查找指定文本
        
        Args:
            image: 输入图像
            text: 要查找的文本
            region: 搜索区域 {x, y, width, height}
            min_confidence: 最小置信度
            
        Returns:
            dict: 查找结果
        """
        results = self.recognize(image, region=region, min_confidence=min_confidence)
        
        for result in results:
            if text in result['text']:
                return result
        
        return None
