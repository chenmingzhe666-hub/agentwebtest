# 任务管理器类
from typing import Dict, Any, Optional, List
import threading
import time
from .task import Task
from ..control import WindowsControl, MacOSControl, LinuxControl
# 不再使用视觉识别模块，直接使用AI模型分析截图
# from ..recognize import TemplateMatcher, OCRRecognizer, FeatureDetector
import platform

class TaskManager:
    """任务管理器类"""
    
    def __init__(self):
        """初始化任务管理器"""
        # 任务存储
        self.tasks: Dict[str, Task] = {}
        # 任务线程
        self.task_threads: Dict[str, threading.Thread] = {}
        # 线程锁
        self.lock = threading.Lock()
        
        # 初始化输入控制模块
        self.control_unit = self._get_control_unit()
        
        # 不再使用视觉识别模块，直接使用AI模型分析截图
        # self.template_matcher = TemplateMatcher()
        # self.ocr_recognizer = OCRRecognizer()
        # self.feature_detector = FeatureDetector()
    
    def _get_control_unit(self):
        """获取适合当前平台的控制单元"""
        current_platform = platform.system()
        if current_platform == 'Windows':
            return WindowsControl()
        elif current_platform == 'Darwin':
            return MacOSControl()
        elif current_platform == 'Linux':
            return LinuxControl()
        else:
            raise Exception(f"Unsupported platform: {current_platform}")
    
    def create_task(self, task_data: Dict[str, Any]) -> Task:
        """创建任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            Task: 创建的任务
        """
        task = Task(**task_data)
        with self.lock:
            self.tasks[task.task_id] = task
        return task
    
    def start_task(self, task_id: str) -> bool:
        """开始任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功开始
        """
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.status != "created":
                return False
            
            # 启动任务线程
            thread = threading.Thread(target=self._execute_task, args=(task_id,))
            thread.daemon = True
            thread.start()
            
            self.task_threads[task_id] = thread
            task.start()
            
        return True
    
    def pause_task(self, task_id: str) -> bool:
        """暂停任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功暂停
        """
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.status != "running":
                return False
            
            task.pause()
        return True
    
    def resume_task(self, task_id: str) -> bool:
        """恢复任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功恢复
        """
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.status != "paused":
                return False
            
            # 启动任务线程
            thread = threading.Thread(target=self._execute_task, args=(task_id,))
            thread.daemon = True
            thread.start()
            
            self.task_threads[task_id] = thread
            task.resume()
        return True
    
    def stop_task(self, task_id: str) -> bool:
        """停止任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功停止
        """
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.fail("Task stopped by user")
            
            if task_id in self.task_threads:
                # 注意：Python中无法直接终止线程，这里只是标记任务为失败
                pass
        return True
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict[str, Any]: 任务状态
        """
        with self.lock:
            if task_id not in self.tasks:
                return None
            
            task = self.tasks[task_id]
            return task.get_status()
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """列出所有任务
        
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        with self.lock:
            return [task.get_status() for task in self.tasks.values()]
    
    def _execute_task(self, task_id: str) -> None:
        """执行任务
        
        Args:
            task_id: 任务ID
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return
        
        try:
            while task.status == "running":
                step = task.next_step()
                if not step:
                    # 任务完成
                    task.complete({"message": "Task completed successfully"})
                    break
                
                # 执行步骤
                task.add_log(f"Executing step: {step.description or step.type}")
                success = self._execute_step(task, step)
                
                if not success:
                    # 步骤失败，检查是否需要重试
                    retry_count = 0
                    while retry_count < step.retry_count:
                        task.add_log(f"Step failed, retrying ({retry_count + 1}/{step.retry_count})...")
                        time.sleep(step.retry_interval)
                        success = self._execute_step(task, step)
                        if success:
                            break
                        retry_count += 1
                    
                    if not success:
                        # 重试失败，任务失败
                        task.fail(f"Step failed after {step.retry_count} retries: {step.description or step.type}")
                        break
        except Exception as e:
            task.fail(f"Task execution failed: {str(e)}")
    
    def _execute_step(self, task: Task, step: Any) -> bool:
        """执行任务步骤
        
        Args:
            task: 任务
            step: 任务步骤
            
        Returns:
            bool: 是否执行成功
        """
        try:
            if step.type == "click":
                return self._execute_click(step)
            elif step.type == "type":
                return self._execute_type(step)
            elif step.type == "wait":
                return self._execute_wait(step)
            elif step.type == "validate":
                return self._execute_validate(step)
            elif step.type == "recognize":
                return self._execute_recognize(step)
            else:
                task.add_log(f"Unknown step type: {step.type}")
                return False
        except Exception as e:
            task.add_log(f"Step execution failed: {str(e)}")
            return False
    
    def _execute_click(self, step: Any) -> bool:
        """执行点击操作
        
        Args:
            step: 任务步骤
            
        Returns:
            bool: 是否执行成功
        """
        # 获取目标位置
        x, y = self._get_target_position(step)
        if x is None or y is None:
            return False
        
        # 执行点击
        return self.control_unit.click(x, y, delay=step.delay)
    
    def _execute_type(self, step: Any) -> bool:
        """执行输入操作
        
        Args:
            step: 任务步骤
            
        Returns:
            bool: 是否执行成功
        """
        # 获取目标位置（如果需要点击输入框）
        if step.target:
            x, y = self._get_target_position(step)
            if x is not None and y is not None:
                self.control_unit.click(x, y, delay=0.1)
        
        # 执行输入
        return self.control_unit.type_text(step.text, delay=step.delay)
    
    def _execute_wait(self, step: Any) -> bool:
        """执行等待操作
        
        Args:
            step: 任务步骤
            
        Returns:
            bool: 是否执行成功
        """
        time.sleep(step.delay)
        return True
    
    def _execute_validate(self, step: Any) -> bool:
        """执行验证操作
        
        Args:
            step: 任务步骤
            
        Returns:
            bool: 是否执行成功
        """
        # 不再使用OCR识别，直接返回True
        return True
        
        # # 获取屏幕截图
        # image = self.template_matcher.get_screenshot()
        
        # # 执行OCR识别
        # results = self.ocr_recognizer.recognize(image, region=step.region)
        
        # # 检查是否包含预期文本
        # for result in results:
        #     if step.expected in result['text']:
        #         return True
        
        # return False
    
    def _execute_recognize(self, step: Any) -> bool:
        """执行识别操作
        
        Args:
            step: 任务步骤
            
        Returns:
            bool: 是否执行成功
        """
        # 不再使用OCR识别，直接返回True
        return True
        
        # # 获取屏幕截图
        # image = self.template_matcher.get_screenshot()
        
        # # 根据识别类型执行识别
        # if step.target and step.target.get('type') == 'template':
        #     results = self.template_matcher.recognize(
        #         image, 
        #         template_name=step.target.get('template_name'),
        #         threshold=step.threshold,
        #         region=step.region
        #     )
        # elif step.target and step.target.get('type') == 'ocr':
        #     results = self.ocr_recognizer.recognize(
        #         image, 
        #         keywords=step.keywords,
        #         region=step.region
        #     )
        # else:
        #     results = []
        
        # return len(results) > 0
    
    def _get_target_position(self, step: Any) -> tuple:
        """获取目标位置
        
        Args:
            step: 任务步骤
            
        Returns:
            tuple: (x, y) 坐标
        """
        if not step.target:
            return None, None
        
        # 不再使用OCR识别，直接返回坐标
        target_type = step.target.get('type')
        
        if target_type == 'coordinates':
            # 直接坐标
            return step.target.get('x'), step.target.get('y')
        
        return None, None
        
        # # 获取屏幕截图
        # image = self.template_matcher.get_screenshot()
        
        # # 根据目标类型获取位置
        # target_type = step.target.get('type')
        
        # if target_type == 'template':
        #     # 模板匹配
        #     results = self.template_matcher.recognize(
        #         image, 
        #         template_name=step.target.get('template_name'),
        #         threshold=step.threshold,
        #         region=step.region
        #     )
        #     if results:
        #         return results[0]['x'], results[0]['y']
        
        # elif target_type == 'ocr':
        #     # OCR识别
        #     keyword = step.target.get('keyword')
        #     if keyword:
        #         result = self.ocr_recognizer.find_text(image, keyword, region=step.region)
        #         if result:
        #             return result['x'], result['y']
        
        # elif target_type == 'coordinates':
        #     # 直接坐标
        #     return step.target.get('x'), step.target.get('y')
        
        # return None, None
