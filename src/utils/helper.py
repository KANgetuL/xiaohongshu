"""
辅助工具函数模块
提供各种通用工具函数
"""

import json
import hashlib
import os
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from config.constants import ERROR_CODES, STATUS


def generate_id(prefix: str = "comic") -> str:
    """
    生成唯一ID
    
    Args:
        prefix: ID前缀
        
    Returns:
        唯一ID字符串
    """
    timestamp = int(time.time() * 1000)
    random_num = random.randint(1000, 9999)
    return f"{prefix}_{timestamp}_{random_num}"


def calculate_md5(content: bytes) -> str:
    """
    计算MD5哈希值
    
    Args:
        content: 字节内容
        
    Returns:
        MD5哈希字符串
    """
    return hashlib.md5(content).hexdigest()


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """
    格式化时间戳为字符串
    
    Args:
        timestamp: Unix时间戳，如果为None则使用当前时间
        
    Returns:
        格式化后的时间字符串
    """
    if timestamp is None:
        timestamp = time.time()
    
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def safe_json_dump(data: Any, filepath: Path, indent: int = 2) -> bool:
    """
    安全地将数据保存为JSON文件
    
    Args:
        data: 要保存的数据
        filepath: 文件路径
        indent: JSON缩进
        
    Returns:
        是否成功
    """
    try:
        # 确保目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        
        return True
    except Exception as e:
        print(f"保存JSON文件失败: {e}")
        return False


def safe_json_load(filepath: Path) -> Optional[Any]:
    """
    安全地从JSON文件加载数据
    
    Args:
        filepath: 文件路径
        
    Returns:
        加载的数据，失败返回None
    """
    try:
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载JSON文件失败: {e}")
        return None


def extract_domain(url: str) -> str:
    """
    从URL中提取域名
    
    Args:
        url: URL字符串
        
    Returns:
        域名
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return ""


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    将列表分割成指定大小的块
    
    Args:
        lst: 原始列表
        chunk_size: 每个块的大小
        
    Returns:
        分割后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def create_response(
    success: bool = True,
    code: int = ERROR_CODES["SUCCESS"],
    message: str = "",
    data: Any = None
) -> Dict[str, Any]:
    """
    创建标准响应格式
    
    Args:
        success: 是否成功
        code: 错误码
        message: 消息
        data: 数据
        
    Returns:
        响应字典
    """
    return {
        "success": success,
        "code": code,
        "message": message,
        "data": data,
        "timestamp": time.time()
    }


def clean_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除非法字符
    illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    
    # 限制长度
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename


if __name__ == "__main__":
    # 测试工具函数
    print(f"生成的ID: {generate_id()}")
    print(f"当前时间: {format_timestamp()}")
    
    # 测试响应创建
    response = create_response(message="测试成功", data={"test": "data"})
    print(f"响应: {json.dumps(response, indent=2)}")