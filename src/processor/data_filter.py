"""
数据过滤模块
根据规则过滤不符合要求的数据
"""

from typing import List, Dict, Any, Tuple
from pathlib import Path
from PIL import Image

from config.settings import FILTER_RULES
from src.utils.logger import setup_logger
from src.utils.validator import DataValidator


class DataFilter:
    """数据过滤器"""
    
    def __init__(self):
        self.logger = setup_logger("data_filter")
        self.validator = DataValidator()
        
        # 过滤规则
        self.min_width = FILTER_RULES["min_image_width"]
        self.min_height = FILTER_RULES["min_image_height"]
        self.min_text_length = FILTER_RULES["min_text_length"]
    
    def filter_comic(self, comic_data: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        过滤连环画数据
        
        Args:
            comic_data: 连环画数据
            
        Returns:
            (是否通过, 错误信息列表, 更新后的数据)
        """
        errors = []
        warnings = []
        
        # 验证数据结构
        is_valid, struct_errors = self.validator.validate_comic_structure(comic_data)
        if not is_valid:
            errors.extend(struct_errors)
            return False, errors, comic_data
        
        # 验证图片
        images = comic_data.get("images", [])
        if len(images) < 6:
            errors.append(f"图片数量不足6张，当前{len(images)}张")
        
        valid_images = []
        for i, img_info in enumerate(images):
            img_path = Path(img_info.get("path", ""))
            
            # 验证图片路径
            is_valid_path, path_error = self.validator.validate_image_path(img_path)
            if not is_valid_path:
                errors.append(f"图片{i+1}: {path_error}")
                continue
            
            # 检查分辨率
            try:
                with Image.open(img_path) as img:
                    width, height = img.size
                    
                    img_info["resolution"] = {
                        "width": width,
                        "height": height
                    }
                    
                    # 检查分辨率是否达标
                    if width < self.min_width or height < self.min_height:
                        warnings.append(f"图片{i+1}分辨率较低: {width}x{height}")
                    else:
                        img_info["resolution_check"] = "passed"
                    
                    valid_images.append(img_info)
                    
            except Exception as e:
                errors.append(f"图片{i+1}无法打开: {str(e)}")
        
        # 验证文本
        # 检查连环画标题
        title = comic_data["comic_info"].get("title", "")
        if title:
            is_valid_title, title_error = self.validator.validate_text_length(title)
            if not is_valid_title:
                warnings.append(f"标题{title_error}")
        
        # 检查图片描述
        for i, img_info in enumerate(valid_images):
            caption = img_info.get("caption", "")
            if caption:
                is_valid_caption, caption_error = self.validator.validate_text_length(caption)
                if not is_valid_caption:
                    warnings.append(f"图片{i+1}描述{caption_error}")
        
        # 更新数据
        filtered_data = comic_data.copy()
        filtered_data["images"] = valid_images
        
        # 更新质量检查状态
        quality_status = "passed" if len(errors) == 0 else "failed"
        filtered_data["comic_info"]["quality_check"] = quality_status
        
        # 添加警告信息
        if warnings:
            filtered_data["comic_info"]["warnings"] = warnings
        
        # 返回结果
        all_messages = errors + warnings
        passed = len(errors) == 0
        
        return passed, all_messages, filtered_data
    
    def batch_filter(self, comics_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        批量过滤连环画数据
        
        Args:
            comics_data: 连环画数据列表
            
        Returns:
            (通过的数据列表, 未通过的数据列表)
        """
        passed_comics = []
        failed_comics = []
        
        self.logger.info(f"开始批量过滤 {len(comics_data)} 个连环画")
        
        for comic_data in comics_data:
            passed, messages, filtered_data = self.filter_comic(comic_data)
            
            if passed:
                passed_comics.append(filtered_data)
                self.logger.debug(f"连环画通过过滤: {filtered_data['comic_info']['id']}")
            else:
                failed_comics.append({
                    "data": comic_data,
                    "errors": messages,
                    "comic_id": comic_data["comic_info"]["id"]
                })
                self.logger.warning(f"连环画未通过过滤: {comic_data['comic_info']['id']}, 错误: {messages}")
        
        self.logger.info(f"过滤完成: {len(passed_comics)}个通过, {len(failed_comics)}个未通过")
        
        return passed_comics, failed_comics


if __name__ == "__main__":
    # 测试数据过滤器
    filter = DataFilter()
    
    # 创建测试数据
    test_comic = {
        "comic_info": {
            "id": "test_comic_001",
            "title": "外卖翻车测试漫画",
            "theme": "外卖/点餐翻车",
            "quality_check": "pending"
        },
        "images": [
            {
                "filename": "test_image.jpg",
                "path": "test_data/test_image.jpg",  # 需要实际文件测试
                "caption": "这是一个测试图片描述，超过十个中文字符。"
            }
        ]
    }
    
    # 测试过滤（需要实际图片文件）
    # passed, messages, filtered = filter.filter_comic(test_comic)
    # print(f"过滤结果: {passed}")
    # print(f"消息: {messages}")