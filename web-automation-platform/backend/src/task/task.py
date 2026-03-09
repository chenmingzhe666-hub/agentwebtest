# 任务类
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import time
import uuid
from .task_step import TaskStep

class Task(BaseModel):
    """任务类"""
    # 任务基本信息
    task_id: str = str(uuid.uuid4())
    name: str
    description: Optional[str] = None
    
    # 任务步骤
    steps: List[TaskStep]
    
    # 任务状态
    status: str = "created"  # created, running, completed, failed, paused
    current_step: int = 0
    total_steps: int = 0
    progress: int = 0
    
    # 任务结果
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # 任务时间
    created_at: float = time.time()
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # 任务日志
    logs: List[str] = []
    
    def __init__(self, **data):
        """初始化任务"""
        super().__init__(**data)
        self.total_steps = len(self.steps)
    
    def start(self) -> None:
        """开始任务"""
        self.status = "running"
        self.started_at = time.time()
        self.logs.append(f"Task {self.task_id} started")
    
    def pause(self) -> None:
        """暂停任务"""
        self.status = "paused"
        self.logs.append(f"Task {self.task_id} paused")
    
    def resume(self) -> None:
        """恢复任务"""
        self.status = "running"
        self.logs.append(f"Task {self.task_id} resumed")
    
    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        """完成任务"""
        self.status = "completed"
        self.completed_at = time.time()
        self.progress = 100
        self.result = result
        self.logs.append(f"Task {self.task_id} completed")
    
    def fail(self, error: str) -> None:
        """任务失败"""
        self.status = "failed"
        self.completed_at = time.time()
        self.error = error
        self.logs.append(f"Task {self.task_id} failed: {error}")
    
    def next_step(self) -> Optional[TaskStep]:
        """获取下一个步骤"""
        if self.current_step < self.total_steps:
            step = self.steps[self.current_step]
            self.current_step += 1
            self.progress = int((self.current_step / self.total_steps) * 100)
            return step
        return None
    
    def add_log(self, message: str) -> None:
        """添加日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取任务状态"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "progress": self.progress,
            "logs": self.logs[-10:],  # 只返回最近10条日志
            "error": self.error
        }
    
    class Config:
        """配置类"""
        json_schema_extra = {
            "example": {
                "name": "登录测试",
                "description": "测试登录功能",
                "steps": [
                    {
                        "type": "click",
                        "target": {
                            "type": "template",
                            "template_name": "login_button"
                        },
                        "description": "点击登录按钮"
                    },
                    {
                        "type": "type",
                        "text": "username",
                        "target": {
                            "type": "ocr",
                            "keyword": "用户名"
                        },
                        "description": "输入用户名"
                    }
                ]
            }
        }
