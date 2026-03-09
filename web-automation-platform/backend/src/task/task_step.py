# 任务步骤类
from typing import Dict, Any, Optional
from pydantic import BaseModel

class TaskStep(BaseModel):
    """任务步骤类"""
    # 步骤类型
    type: str  # click, type, wait, validate, recognize
    
    # 目标信息
    target: Optional[Dict[str, Any]] = None
    
    # 操作参数
    text: Optional[str] = None  # 输入文本
    delay: float = 0.1  # 操作延迟
    duration: float = 0.1  # 操作持续时间
    
    # 验证参数
    expected: Optional[str] = None  # 预期结果
    timeout: int = 30  # 验证超时时间
    
    # 重试参数
    retry_count: int = 3  # 重试次数
    retry_interval: float = 2  # 重试间隔
    
    # 识别参数
    template_name: Optional[str] = None  # 模板名称
    keywords: Optional[list] = None  # OCR关键词
    threshold: float = 0.8  # 识别阈值
    
    # 区域参数
    region: Optional[Dict[str, int]] = None  # 操作区域 {x, y, width, height}
    
    # 步骤描述
    description: Optional[str] = None  # 步骤描述
    
    class Config:
        """配置类"""
        json_schema_extra = {
            "example": {
                "type": "click",
                "target": {
                    "type": "template",
                    "template_name": "login_button"
                },
                "delay": 0.5,
                "retry_count": 3,
                "retry_interval": 2,
                "description": "点击登录按钮"
            }
        }
