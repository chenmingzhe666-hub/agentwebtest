# 输入控制基类
from abc import ABC, abstractmethod
import time

class ControlUnit(ABC):
    """输入控制基类，定义统一的接口"""
    
    @abstractmethod
    def move_mouse(self, x: int, y: int, duration: float = 0.1) -> bool:
        """移动鼠标到指定坐标
        
        Args:
            x: 目标x坐标
            y: 目标y坐标
            duration: 移动持续时间（秒）
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def click(self, x: int, y: int, button: str = 'left', delay: float = 0.1) -> bool:
        """点击鼠标
        
        Args:
            x: 点击x坐标
            y: 点击y坐标
            button: 按钮类型 ('left', 'right', 'middle')
            delay: 点击后延迟（秒）
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def type_text(self, text: str, delay: float = 0.05) -> bool:
        """输入文本
        
        Args:
            text: 要输入的文本
            delay: 每个字符输入延迟（秒）
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def press_key(self, key: str, delay: float = 0.1) -> bool:
        """按下按键
        
        Args:
            key: 按键名称
            delay: 按下后延迟（秒）
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def scroll(self, delta: int) -> bool:
        """滚动鼠标滚轮
        
        Args:
            delta: 滚动量（正数向上，负数向下）
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    def wait(self, seconds: float) -> None:
        """等待指定时间
        
        Args:
            seconds: 等待时间（秒）
        """
        time.sleep(seconds)
