# macOS平台输入控制实现
import time
from .control_unit import ControlUnit

class MacOSControl(ControlUnit):
    """macOS平台输入控制实现"""
    
    def __init__(self):
        """初始化macOS控制单元"""
        try:
            # 导入Quartz框架
            from Quartz import CGEventCreateMouseEvent, CGEventPost, kCGHIDEventTap, \
                kCGEventMouseMoved, kCGEventLeftMouseDown, kCGEventLeftMouseUp, \
                kCGEventRightMouseDown, kCGEventRightMouseUp, \
                kCGEventMiddleMouseDown, kCGEventMiddleMouseUp, \
                kCGEventScrollWheel, kCGEventKeyDown, kCGEventKeyUp, \
                CGEventCreateKeyboardEvent, CGEventSetIntegerValueField, \
                kCGKeyboardEventKeycode
            
            self.CGEventCreateMouseEvent = CGEventCreateMouseEvent
            self.CGEventPost = CGEventPost
            self.kCGHIDEventTap = kCGHIDEventTap
            self.kCGEventMouseMoved = kCGEventMouseMoved
            self.kCGEventLeftMouseDown = kCGEventLeftMouseDown
            self.kCGEventLeftMouseUp = kCGEventLeftMouseUp
            self.kCGEventRightMouseDown = kCGEventRightMouseDown
            self.kCGEventRightMouseUp = kCGEventRightMouseUp
            self.kCGEventMiddleMouseDown = kCGEventMiddleMouseDown
            self.kCGEventMiddleMouseUp = kCGEventMiddleMouseUp
            self.kCGEventScrollWheel = kCGEventScrollWheel
            self.kCGEventKeyDown = kCGEventKeyDown
            self.kCGEventKeyUp = kCGEventKeyUp
            self.CGEventCreateKeyboardEvent = CGEventCreateKeyboardEvent
            self.CGEventSetIntegerValueField = CGEventSetIntegerValueField
            self.kCGKeyboardEventKeycode = kCGKeyboardEventKeycode
            
            # 键盘按键映射
            self.key_map = {
                'enter': 36,
                'esc': 53,
                'tab': 48,
                'space': 49,
                'backspace': 51,
                'delete': 117,
                'up': 126,
                'down': 125,
                'left': 123,
                'right': 124,
                'ctrl': 59,
                'alt': 58,
                'shift': 56,
                'cmd': 55
            }
            
        except ImportError:
            print("警告: 无法导入Quartz框架，macOS控制功能不可用")
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
            
            # 这里简化处理，直接设置鼠标位置
            # 在实际实现中，应该获取当前位置并平滑移动
            event = self.CGEventCreateMouseEvent(
                None, self.kCGEventMouseMoved, (x, y), 0
            )
            self.CGEventPost(self.kCGHIDEventTap, event)
            time.sleep(duration)
            
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
                down_event = self.CGEventCreateMouseEvent(
                    None, self.kCGEventLeftMouseDown, (x, y), 0
                )
                up_event = self.CGEventCreateMouseEvent(
                    None, self.kCGEventLeftMouseUp, (x, y), 0
                )
            elif button == 'right':
                down_event = self.CGEventCreateMouseEvent(
                    None, self.kCGEventRightMouseDown, (x, y), 1
                )
                up_event = self.CGEventCreateMouseEvent(
                    None, self.kCGEventRightMouseUp, (x, y), 1
                )
            elif button == 'middle':
                down_event = self.CGEventCreateMouseEvent(
                    None, self.kCGEventMiddleMouseDown, (x, y), 2
                )
                up_event = self.CGEventCreateMouseEvent(
                    None, self.kCGEventMiddleMouseUp, (x, y), 2
                )
            else:
                return False
            
            # 发送鼠标事件
            self.CGEventPost(self.kCGHIDEventTap, down_event)
            time.sleep(0.05)
            self.CGEventPost(self.kCGHIDEventTap, up_event)
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
                    self._press_keycode(49)  # 空格键
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
            # 创建滚动事件
            event = self.CGEventCreateMouseEvent(
                None, self.kCGEventScrollWheel, (0, 0), 0
            )
            # 设置滚动量
            # 注意：macOS的滚动方向与Windows相反
            self.CGEventSetIntegerValueField(event, self.kCGKeyboardEventKeycode, -delta)
            self.CGEventPost(self.kCGHIDEventTap, event)
            
            return True
        except Exception as e:
            print(f"滚动鼠标失败: {e}")
            return False
    
    def _press_keycode(self, keycode: int) -> None:
        """按下并释放指定keycode的按键"""
        if not self.available:
            return
        
        try:
            # 创建按键按下事件
            down_event = self.CGEventCreateKeyboardEvent(None, keycode, True)
            self.CGEventPost(self.kCGHIDEventTap, down_event)
            
            time.sleep(0.05)
            
            # 创建按键释放事件
            up_event = self.CGEventCreateKeyboardEvent(None, keycode, False)
            self.CGEventPost(self.kCGHIDEventTap, up_event)
        except Exception as e:
            print(f"按下按键失败: {e}")
