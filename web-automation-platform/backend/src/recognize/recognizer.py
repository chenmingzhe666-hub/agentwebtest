# 视觉识别基类
from abc import ABC, abstractmethod
import cv2
import numpy as np

class Recognizer(ABC):
    """视觉识别基类，定义统一的接口"""
    
    def __init__(self):
        """初始化识别器"""
        self.cache = {}
    
    @abstractmethod
    def recognize(self, image: np.ndarray, **kwargs) -> list:
        """执行识别
        
        Args:
            image: 输入图像
            **kwargs: 识别参数
            
        Returns:
            list: 识别结果列表
        """
        pass
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """预处理图像
        
        Args:
            image: 输入图像
            
        Returns:
            np.ndarray: 预处理后的图像
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 高斯模糊降噪
        image = cv2.GaussianBlur(image, (5, 5), 0)
        
        return image
    
    def get_screenshot(self) -> np.ndarray:
        """获取屏幕截图
        
        Returns:
            np.ndarray: 屏幕截图
        """
        import pyautogui
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def save_cache(self, key: str, value: any) -> None:
        """保存缓存
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        self.cache[key] = value
    
    def get_cache(self, key: str) -> any:
        """获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            any: 缓存值
        """
        return self.cache.get(key)
