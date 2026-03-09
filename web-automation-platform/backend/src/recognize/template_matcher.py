# 模板匹配器
import cv2
import numpy as np
import os
from .recognizer import Recognizer

class TemplateMatcher(Recognizer):
    """模板匹配器，用于识别固定的UI元素"""
    
    def __init__(self, template_dir: str = 'templates'):
        """初始化模板匹配器
        
        Args:
            template_dir: 模板文件目录
        """
        super().__init__()
        self.template_dir = template_dir
        # 创建模板目录
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
    
    def recognize(self, image: np.ndarray, template_name: str = None, 
                 template: np.ndarray = None, threshold: float = 0.8, 
                 region: dict = None) -> list:
        """执行模板匹配
        
        Args:
            image: 输入图像
            template_name: 模板名称
            template: 模板图像（如果不使用模板名称）
            threshold: 匹配阈值
            region: 搜索区域 {x, y, width, height}
            
        Returns:
            list: 匹配结果列表
        """
        results = []
        
        try:
            # 加载模板
            if template is None and template_name:
                template_path = os.path.join(self.template_dir, f'{template_name}.png')
                if not os.path.exists(template_path):
                    return results
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
            
            if template is None:
                return results
            
            # 裁剪搜索区域
            if region:
                x, y, w, h = region['x'], region['y'], region['width'], region['height']
                image = image[y:y+h, x:x+w]
            
            # 转换为灰度图
            if len(image.shape) == 3:
                image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                image_gray = image
            
            # 模板匹配
            result = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
            
            # 查找匹配位置
            locations = np.where(result >= threshold)
            
            # 处理匹配结果
            for pt in zip(*locations[::-1]):
                x, y = pt
                w, h = template.shape[1], template.shape[0]
                
                # 计算匹配中心坐标
                center_x = x + w // 2
                center_y = y + h // 2
                
                # 如果指定了搜索区域，需要调整坐标
                if region:
                    center_x += region['x']
                    center_y += region['y']
                
                # 计算匹配得分
                score = float(result[y, x])
                
                results.append({
                    'type': 'template',
                    'name': template_name,
                    'x': center_x,
                    'y': center_y,
                    'width': w,
                    'height': h,
                    'score': score,
                    'rect': {'x': x, 'y': y, 'width': w, 'height': h}
                })
            
            # 去重处理
            results = self._remove_duplicates(results)
            
        except Exception as e:
            print(f"模板匹配失败: {e}")
        
        return results
    
    def _remove_duplicates(self, results: list, threshold: int = 10) -> list:
        """去除重复的匹配结果
        
        Args:
            results: 匹配结果列表
            threshold: 距离阈值
            
        Returns:
            list: 去重后的结果列表
        """
        if not results:
            return results
        
        # 按得分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        unique_results = []
        for result in results:
            # 检查是否与已添加的结果重复
            is_duplicate = False
            for unique in unique_results:
                distance = np.sqrt(
                    (result['x'] - unique['x']) ** 2 + 
                    (result['y'] - unique['y']) ** 2
                )
                if distance < threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_results.append(result)
        
        return unique_results
    
    def save_template(self, template_name: str, image: np.ndarray, 
                     region: dict = None) -> bool:
        """保存模板
        
        Args:
            template_name: 模板名称
            image: 源图像
            region: 模板区域 {x, y, width, height}
            
        Returns:
            bool: 保存是否成功
        """
        try:
            if region:
                x, y, w, h = region['x'], region['y'], region['width'], region['height']
                template = image[y:y+h, x:x+w]
            else:
                template = image
            
            template_path = os.path.join(self.template_dir, f'{template_name}.png')
            cv2.imwrite(template_path, template)
            return True
        except Exception as e:
            print(f"保存模板失败: {e}")
            return False
    
    def list_templates(self) -> list:
        """列出所有模板
        
        Returns:
            list: 模板名称列表
        """
        templates = []
        for file in os.listdir(self.template_dir):
            if file.endswith('.png'):
                templates.append(os.path.splitext(file)[0])
        return templates
