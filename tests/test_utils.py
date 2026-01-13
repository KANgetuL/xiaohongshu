"""
工具模块测试文件
"""

import unittest
import tempfile
from pathlib import Path
import json

from src.utils.validator import DataValidator
from src.utils.helper import (
    generate_id,
    format_timestamp,
    safe_json_dump,
    safe_json_load,
    clean_filename
)


class TestDataValidator(unittest.TestCase):
    """测试数据验证器"""
    
    def setUp(self):
        self.validator = DataValidator()
    
    def test_validate_text_length(self):
        # 测试足够长的文本
        text = "这是一个包含超过十个中文字符的测试文本。"
        result, message = self.validator.validate_text_length(text)
        self.assertTrue(result)
        
        # 测试长度不足的文本
        text = "短文本"
        result, message = self.validator.validate_text_length(text)
        self.assertFalse(result)
        
        # 测试空文本
        result, message = self.validator.validate_text_length("")
        self.assertFalse(result)


class TestHelperFunctions(unittest.TestCase):
    """测试辅助函数"""
    
    def test_generate_id(self):
        id1 = generate_id("test")
        id2 = generate_id("test")
        
        # 确保ID以正确的前缀开始
        self.assertTrue(id1.startswith("test_"))
        
        # 确保两个ID不同
        self.assertNotEqual(id1, id2)
    
    def test_format_timestamp(self):
        timestamp = 1609459200  # 2021-01-01 00:00:00
        formatted = format_timestamp(timestamp)
        
        # 检查格式
        self.assertRegex(formatted, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
    
    def test_safe_json_operations(self):
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # 测试保存数据
            test_data = {"name": "test", "value": 123}
            success = safe_json_dump(test_data, temp_path)
            self.assertTrue(success)
            
            # 测试加载数据
            loaded_data = safe_json_load(temp_path)
            self.assertEqual(loaded_data, test_data)
            
            # 测试加载不存在的文件
            nonexistent = Path("/nonexistent/file.json")
            loaded = safe_json_load(nonexistent)
            self.assertIsNone(loaded)
            
        finally:
            # 清理临时文件
            if temp_path.exists():
                temp_path.unlink()
    
    def test_clean_filename(self):
        # 测试清理非法字符
        dirty_name = 'test<>:"/\\|?*file.jpg'
        clean_name = clean_filename(dirty_name)
        
        # 检查是否包含非法字符
        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in illegal_chars:
            self.assertNotIn(char, clean_name)


if __name__ == "__main__":
    unittest.main()