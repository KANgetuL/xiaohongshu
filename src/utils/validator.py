"""
数据验证工具模块
提供各种数据验证功能
"""

import re
from typing import Dict, List, Tuple, Any
from pathlib import Path

from config.settings import FILTER_RULES
from config.constants import IMAGE_EXTENSIONS, QUALITY_CHECKS


class DataValidator:
    """数据验证器类"""
    
    def __init__(self):
        self.min_text_length = FILTER_RULES["min_text_length"]
        self.min_image_width = FILTER_RULES["min_image_width"]
        self.min_image_height = FILTER_RULES["min_image_height"]
        self.allowed_formats = FILTER_RULES["allowed_image_formats"]
    
    def validate_text_length(self, text: str) -> Tuple[bool, str]:
        """
        验证文本长度是否符合要求
        
        Args:
            text: 待验证的文本
            
        Returns:
            (是否通过, 错误信息)
        """
        if not text or not isinstance(text, str):
            return False, "文本为空或不是字符串"
        
        # 计算中文字符数量
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        total_length = len(chinese_chars)
        
        if total_length >= self.min_text_length:
            return True, f"文本长度符合要求（{total_length}个中文字符）"
        else:
            return False, f"文本长度不足，需要至少{self.min_text_length}个中文字符，当前{total_length}个"
    
    def validate_image_path(self, image_path: Path) -> Tuple[bool, str]:
        """
        验证图像路径和格式
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            (是否通过, 错误信息)
        """
        if not isinstance(image_path, Path):
            image_path = Path(image_path)
        
        # 检查文件是否存在
        if not image_path.exists():
            return False, f"图像文件不存在: {image_path}"
        
        # 检查文件格式
        suffix = image_path.suffix.lower()
        if suffix not in self.allowed_formats:
            return False, f"不支持的图像格式: {suffix}，允许的格式: {self.allowed_formats}"
        
        # 检查文件大小
        file_size = image_path.stat().st_size
        if file_size == 0:
            return False, "图像文件大小为0"
        
        return True, f"图像文件有效: {image_path}"
    
    def validate_comic_structure(self, comic_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证连环画数据结构
        
        Args:
            comic_data: 连环画数据字典
            
        Returns:
            (是否通过, 错误信息列表)
        """
        errors = []
        
        # 检查必要字段
        required_fields = ["comic_info", "images", "metadata"]
        for field in required_fields:
            if field not in comic_data:
                errors.append(f"缺少必要字段: {field}")
        
        if errors:
            return False, errors
        
        # 检查comic_info字段
        comic_info = comic_data["comic_info"]
        required_info_fields = ["id", "title", "theme", "total_images"]
        for field in required_info_fields:
            if field not in comic_info or not comic_info[field]:
                errors.append(f"comic_info缺少字段: {field}")
        
        # 检查images字段
        images = comic_data.get("images", [])
        if not isinstance(images, list):
            errors.append("images字段必须是列表")
        elif len(images) < 6:
            errors.append(f"连环画图片数量不足6张，当前{len(images)}张")
        
        return len(errors) == 0, errors
    
    def get_validation_summary(self, validation_results: List[Tuple[bool, str]]) -> Dict[str, Any]:
        """
        获取验证结果摘要
        
        Args:
            validation_results: 验证结果列表
            
        Returns:
            验证摘要字典
        """
        total = len(validation_results)
        passed = sum(1 for result, _ in validation_results if result)
        failed = total - passed
        
        return {
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": failed,
            "pass_rate": round(passed / total * 100, 2) if total > 0 else 0,
            "status": QUALITY_CHECKS["PASSED"] if failed == 0 else QUALITY_CHECKS["FAILED"]
        }


if __name__ == "__main__":
    # 测试验证器
    validator = DataValidator()
    
    # 测试文本验证
    text = "这是一个测试文本，包含中文字符。"
    result, message = validator.validate_text_length(text)
    print(f"文本验证: {result} - {message}")
    
    # 测试图像路径验证（需要实际文件）
    # test_image = Path("test.jpg")
    # result, message = validator.validate_image_path(test_image)
    # print(f"图像验证: {result} - {message}")