# Windows平台输入控制实现
import ctypes
import time
from .control_unit import ControlUnit

class WindowsControl(ControlUnit):
    """Windows平台输入控制实现"""
    
    def __init__(self):
        """初始化Windows控制单元"""
        # 加载user32.dll
        self.user32 = ctypes.windll.user32
        
        # 鼠标事件常量
        self.MOUSEEVENTF_MOVE = 0x0001
        self.MOUSEEVENTF_LEFTDOWN = 0x0002
        self.MOUSEEVENTF_LEFTUP = 0x0004
        self.MOUSEEVENTF_RIGHTDOWN = 0x0008
        self.MOUSEEVENTF_RIGHTUP = 0x0010
        self.MOUSEEVENTF_MIDDLEDOWN = 0x0020
        self.MOUSEEVENTF_MIDDLEUP = 0x0040
        self.MOUSEEVENTF_WHEEL = 0x0800
        
        # 键盘事件常量
        self.KEYEVENTF_KEYDOWN = 0x0000
        self.KEYEVENTF_KEYUP = 0x0002
        
        # 窗口相关常量
        self.SW_SHOW = 5
        self.SW_RESTORE = 9
    
    def move_mouse(self, x: int, y: int, duration: float = 0.1) -> bool:
        """移动鼠标到指定坐标"""
        try:
            # 获取当前鼠标位置
            current_pos = self._get_mouse_pos()
            start_x, start_y = current_pos
            
            # 计算移动步长
            steps = 20
            step_duration = duration / steps
            
            # 平滑移动鼠标
            for i in range(steps + 1):
                t = i / steps
                current_x = int(start_x + (x - start_x) * t)
                current_y = int(start_y + (y - start_y) * t)
                
                # 设置鼠标位置
                self.user32.SetCursorPos(current_x, current_y)
                time.sleep(step_duration)
            
            return True
        except Exception as e:
            print(f"移动鼠标失败: {e}")
            return False
    
    def click(self, x: int, y: int, button: str = 'left', delay: float = 0.1) -> bool:
        """点击鼠标"""
        try:
            # 激活Edge窗口
            self.activate_edge_window()
            
            # 移动鼠标到指定位置
            self.move_mouse(x, y)
            
            # 根据按钮类型执行点击
            if button == 'left':
                self.user32.mouse_event(
                    self.MOUSEEVENTF_LEFTDOWN | self.MOUSEEVENTF_LEFTUP, 
                    x, y, 0, 0
                )
            elif button == 'right':
                self.user32.mouse_event(
                    self.MOUSEEVENTF_RIGHTDOWN | self.MOUSEEVENTF_RIGHTUP, 
                    x, y, 0, 0
                )
            elif button == 'middle':
                self.user32.mouse_event(
                    self.MOUSEEVENTF_MIDDLEDOWN | self.MOUSEEVENTF_MIDDLEUP, 
                    x, y, 0, 0
                )
            
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"点击鼠标失败: {e}")
            return False
    
    def type_text(self, text: str, delay: float = 0.05) -> bool:
        """输入文本"""
        try:
            # 激活Edge窗口
            self.activate_edge_window()
            
            for char in text:
                # 对于特殊字符，需要特殊处理
                if char == ' ':
                    self._press_virtual_key(0x20)  # 空格键
                elif char == '\n':
                    self._press_virtual_key(0x0D)  # 回车键
                else:
                    # 对于普通字符，使用keybd_event
                    self._type_char(char)
                time.sleep(delay)
            return True
        except Exception as e:
            print(f"输入文本失败: {e}")
            return False
    
    def press_key(self, key: str, delay: float = 0.1) -> bool:
        """按下按键"""
        try:
            # 激活Edge窗口
            self.activate_edge_window()
            
            # 按键映射
            key_map = {
                'enter': 0x0D,
                'esc': 0x1B,
                'tab': 0x09,
                'space': 0x20,
                'backspace': 0x08,
                'delete': 0x2E,
                'up': 0x26,
                'down': 0x28,
                'left': 0x25,
                'right': 0x27,
                'ctrl': 0x11,
                'alt': 0x12,
                'shift': 0x10,
                'win': 0x5B
            }
            
            if key in key_map:
                vk_code = key_map[key]
                self._press_virtual_key(vk_code)
            else:
                # 对于普通字符，直接输入
                self._type_char(key)
            
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"按下按键失败: {e}")
            return False
    
    def scroll(self, delta: int) -> bool:
        """滚动鼠标滚轮"""
        try:
            # 获取当前鼠标位置
            x, y = self._get_mouse_pos()
            
            # 执行滚动
            self.user32.mouse_event(
                self.MOUSEEVENTF_WHEEL, 
                x, y, delta * 120, 0
            )
            return True
        except Exception as e:
            print(f"滚动鼠标失败: {e}")
            return False
    
    def _get_mouse_pos(self) -> tuple:
        """获取当前鼠标位置"""
        class POINT(ctypes.Structure):
            _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]
        
        point = POINT()
        self.user32.GetCursorPos(ctypes.byref(point))
        return (point.x, point.y)
    
    def _press_virtual_key(self, vk_code: int) -> None:
        """按下并释放虚拟键"""
        self.user32.keybd_event(vk_code, 0, self.KEYEVENTF_KEYDOWN, 0)
        time.sleep(0.05)
        self.user32.keybd_event(vk_code, 0, self.KEYEVENTF_KEYUP, 0)
    
    def _type_char(self, char: str) -> None:
        """输入单个字符"""
        # 获取字符的虚拟键码
        vk_code = self.user32.VkKeyScanW(ord(char))
        
        # 提取键码和Shift状态
        key_code = vk_code & 0xFF
        shift_state = (vk_code >> 8) & 0xFF
        
        # 如果需要Shift键
        if shift_state & 1:
            self.user32.keybd_event(0x10, 0, self.KEYEVENTF_KEYDOWN, 0)
        
        # 按下并释放键
        self.user32.keybd_event(key_code, 0, self.KEYEVENTF_KEYDOWN, 0)
        time.sleep(0.05)
        self.user32.keybd_event(key_code, 0, self.KEYEVENTF_KEYUP, 0)
        
        # 释放Shift键
        if shift_state & 1:
            self.user32.keybd_event(0x10, 0, self.KEYEVENTF_KEYUP, 0)
    
    def activate_edge_window(self) -> bool:
        """激活Edge浏览器窗口"""
        try:
            # 定义窗口回调函数
            edge_windows = []
            
            def enum_windows_callback(hwnd, lParam):
                # 检查窗口是否可见
                if self.user32.IsWindowVisible(hwnd):
                    # 获取窗口标题
                    title = ctypes.create_unicode_buffer(256)
                    self.user32.GetWindowTextW(hwnd, title, 256)
                    window_title = title.value
                    # 检查标题是否包含Edge
                    if "Microsoft​ Edge" in window_title or "Edge" in window_title:
                        edge_windows.append(hwnd)
                return True
            
            # 枚举所有窗口
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            self.user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
            
            # 如果找到Edge窗口，激活它
            if edge_windows:
                # 激活第一个Edge窗口
                hwnd = edge_windows[0]
                # 检查窗口是否最小化
                if self.user32.IsIconic(hwnd):
                    self.user32.ShowWindow(hwnd, self.SW_RESTORE)
                else:
                    self.user32.ShowWindow(hwnd, self.SW_SHOW)
                # 激活窗口
                self.user32.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                return True
            return False
        except Exception as e:
            print(f"激活Edge窗口失败: {e}")
            return False
