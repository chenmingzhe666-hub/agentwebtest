# Linux平台输入控制实现
import time
from .control_unit import ControlUnit

class LinuxControl(ControlUnit):
    """Linux平台输入控制实现"""
    
    def __init__(self):
        """初始化Linux控制单元"""
        try:
            # 导入Xlib库
            from Xlib import X, display
            from Xlib.ext import xtest
            
            self.display = display.Display()
            self.screen = self.display.screen()
            self.root = self.screen.root
            self.xtest = xtest
            
            # 键盘按键映射
            self.key_map = {
                'enter': 36,
                'esc': 9,
                'tab': 23,
                'space': 65,
                'backspace': 22,
                'delete': 119,
                'up': 111,
                'down': 116,
                'left': 113,
                'right': 114,
                'ctrl': 37,
                'alt': 64,
                'shift': 50,
                'super': 133
            }
            
        except ImportError:
            print("警告: 无法导入Xlib库，Linux控制功能不可用")
            self.available = False
        else:
            self.available = True
    
    def move_mouse(self, x: int, y: int, duration: float = 0.1) -> bool:
        """移动鼠标到指定坐标"""
        if not self.available:
            return False
        
        try:
            # 平滑移动鼠标
            steps = 20
            step_duration = duration / steps
            
            # 获取当前鼠标位置
            current_pos = self._get_mouse_pos()
            start_x, start_y = current_pos
            
            for i in range(steps + 1):
                t = i / steps
                current_x = int(start_x + (x - start_x) * t)
                current_y = int(start_y + (y - start_y) * t)
                
                # 设置鼠标位置
                self.root.warp_pointer(current_x, current_y)
                self.display.sync()
                time.sleep(step_duration)
            
            return True
        except Exception as e:
            print(f"移动鼠标失败: {e}")
            return False
    
    def click(self, x: int, y: int, button: str = 'left', delay: float = 0.1) -> bool:
        """点击鼠标"""
        if not self.available:
            return False
        
        try:
            # 移动鼠标到指定位置
            self.move_mouse(x, y)
            
            # 根据按钮类型执行点击
            if button == 'left':
                button_code = 1
            elif button == 'right':
                button_code = 3
            elif button == 'middle':
                button_code = 2
            else:
                return False
            
            # 执行点击
            self.xtest.fake_input(self.display, X.ButtonPress, button_code)
            self.display.sync()
            time.sleep(0.05)
            self.xtest.fake_input(self.display, X.ButtonRelease, button_code)
            self.display.sync()
            time.sleep(delay)
            
            return True
        except Exception as e:
            print(f"点击鼠标失败: {e}")
            return False
    
    def type_text(self, text: str, delay: float = 0.05) -> bool:
        """输入文本"""
        if not self.available:
            return False
        
        try:
            for char in text:
                # 对于特殊字符，需要特殊处理
                if char == ' ':
                    self._press_keycode(65)  # 空格键
                elif char == '\n':
                    self._press_keycode(36)  # 回车键
                else:
                    # 对于普通字符，需要映射到对应的keycode
                    # 这里简化处理，实际实现需要更复杂的映射
                    pass
                time.sleep(delay)
            return True
        except Exception as e:
            print(f"输入文本失败: {e}")
            return False
    
    def press_key(self, key: str, delay: float = 0.1) -> bool:
        """按下按键"""
        if not self.available:
            return False
        
        try:
            if key in self.key_map:
                keycode = self.key_map[key]
                self._press_keycode(keycode)
            else:
                # 对于普通字符，需要映射到对应的keycode
                pass
            
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"按下按键失败: {e}")
            return False
    
    def scroll(self, delta: int) -> bool:
        """滚动鼠标滚轮"""
        if not self.available:
            return False
        
        try:
            # 滚轮事件
            # 注意：Linux的滚动方向与Windows相同
            scroll_amount = delta * 120
            
            if scroll_amount > 0:
                # 向上滚动
                for _ in range(abs(delta)):
                    self.xtest.fake_input(self.display, X.ButtonPress, 4)
                    self.display.sync()
                    time.sleep(0.05)
                    self.xtest.fake_input(self.display, X.ButtonRelease, 4)
                    self.display.sync()
            else:
                # 向下滚动
                for _ in range(abs(delta)):
                    self.xtest.fake_input(self.display, X.ButtonPress, 5)
                    self.display.sync()
                    time.sleep(0.05)
                    self.xtest.fake_input(self.display, X.ButtonRelease, 5)
                    self.display.sync()
            
            return True
        except Exception as e:
            print(f"滚动鼠标失败: {e}")
            return False
    
    def _get_mouse_pos(self) -> tuple:
        """获取当前鼠标位置"""
        if not self.available:
            return (0, 0)
        
        try:
            # 获取鼠标位置
            coord = self.root.query_pointer()
            return (coord.root_x, coord.root_y)
        except Exception as e:
            print(f"获取鼠标位置失败: {e}")
            return (0, 0)
    
    def _press_keycode(self, keycode: int) -> None:
        """按下并释放指定keycode的按键"""
        if not self.available:
            return
        
        try:
            # 按下按键
            self.xtest.fake_input(self.display, X.KeyPress, keycode)
            self.display.sync()
            time.sleep(0.05)
            
            # 释放按键
            self.xtest.fake_input(self.display, X.KeyRelease, keycode)
            self.display.sync()
        except Exception as e:
            print(f"按下按键失败: {e}")
