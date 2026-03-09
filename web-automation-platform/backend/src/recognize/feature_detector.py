# 特征检测器
import cv2
import numpy as np
from .recognizer import Recognizer

class FeatureDetector(Recognizer):
    """特征检测器，用于识别复杂的UI元素"""
    
    def __init__(self):
        """初始化特征检测器"""
        super().__init__()
        # 初始化SIFT特征检测器
        self.sift = cv2.SIFT_create()
        # 初始化FLANN匹配器
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    def recognize(self, image: np.ndarray, template: np.ndarray = None, 
                 template_path: str = None, threshold: float = 0.7, 
                 region: dict = None) -> list:
        """执行特征检测
        
        Args:
            image: 输入图像
            template: 模板图像
            template_path: 模板图像路径
            threshold: 匹配阈值
            region: 搜索区域 {x, y, width, height}
            
        Returns:
            list: 匹配结果列表
        """
        results = []
        
        try:
            # 加载模板
            if template is None and template_path:
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
            
            if len(template.shape) == 3:
                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            else:
                template_gray = template
            
            # 检测特征点
            kp1, des1 = self.sift.detectAndCompute(template_gray, None)
            kp2, des2 = self.sift.detectAndCompute(image_gray, None)
            
            if des1 is None or des2 is None:
                return results
            
            # 匹配特征点
            matches = self.flann.knnMatch(des1, des2, k=2)
            
            # 过滤匹配点
            good_matches = []
            for m, n in matches:
                if m.distance < threshold * n.distance:
                    good_matches.append(m)
            
            # 如果匹配点足够多，计算变换矩阵
            if len(good_matches) > 10:
                # 获取匹配点的坐标
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                
                # 计算变换矩阵
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                
                if M is not None:
                    # 获取模板的边界框
                    h, w = template_gray.shape
                    pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
                    
                    # 计算变换后的边界框
                    dst = cv2.perspectiveTransform(pts, M)
                    
                    # 计算边界框的最小外接矩形
                    x_min = int(np.min(dst[:, :, 0]))
                    y_min = int(np.min(dst[:, :, 1]))
                    x_max = int(np.max(dst[:, :, 0]))
                    y_max = int(np.max(dst[:, :, 1]))
                    
                    width = x_max - x_min
                    height = y_max - y_min
                    
                    # 计算中心坐标
                    center_x = x_min + width // 2
                    center_y = y_min + height // 2
                    
                    # 如果指定了搜索区域，需要调整坐标
                    if region:
                        center_x += region['x']
                        center_y += region['y']
                    
                    # 计算匹配得分
                    score = len(good_matches) / len(matches) if matches else 0
                    
                    results.append({
                        'type': 'feature',
                        'x': center_x,
                        'y': center_y,
                        'width': width,
                        'height': height,
                        'score': score,
                        'matches': len(good_matches),
                        'rect': {'x': x_min, 'y': y_min, 'width': width, 'height': height}
                    })
            
        except Exception as e:
            print(f"特征检测失败: {e}")
        
        return results
    
    def detect_edges(self, image: np.ndarray, threshold1: int = 50, 
                    threshold2: int = 150) -> np.ndarray:
        """检测图像边缘
        
        Args:
            image: 输入图像
            threshold1: 边缘检测阈值1
            threshold2: 边缘检测阈值2
            
        Returns:
            np.ndarray: 边缘图像
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 边缘检测
            edges = cv2.Canny(gray, threshold1, threshold2)
            return edges
        except Exception as e:
            print(f"边缘检测失败: {e}")
            return image
    
    def find_contours(self, image: np.ndarray, min_area: int = 100) -> list:
        """查找图像轮廓
        
        Args:
            image: 输入图像
            min_area: 最小轮廓面积
            
        Returns:
            list: 轮廓列表
        """
        contours = []
        
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 二值化
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # 查找轮廓
            cnts, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 过滤小轮廓
            for cnt in cnts:
                area = cv2.contourArea(cnt)
                if area >= min_area:
                    # 计算轮廓的边界框
                    x, y, w, h = cv2.boundingRect(cnt)
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    contours.append({
                        'x': center_x,
                        'y': center_y,
                        'width': w,
                        'height': h,
                        'area': area,
                        'rect': {'x': x, 'y': y, 'width': w, 'height': h}
                    })
            
        except Exception as e:
            print(f"轮廓查找失败: {e}")
        
        return contours
