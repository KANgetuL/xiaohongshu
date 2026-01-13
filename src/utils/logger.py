"""
日志工具模块
提供统一的日志记录功能
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from config.settings import LOG_CONFIG


def setup_logger(
    name: str = "xhs_crawler",
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    设置并返回logger实例
    """
    # 创建logger
    logger = logging.getLogger(name)
    
    # 设置日志级别
    level = log_level or LOG_CONFIG["level"]
    logger.setLevel(getattr(logging, level.upper()))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建控制台handler - 修复Windows控制台编码问题
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # 修复Windows控制台编码问题
    try:
        # 尝试使用UTF-8编码
        import sys
        if sys.platform == "win32":
            import io
            console_handler.stream = io.TextIOWrapper(
                console_handler.stream.buffer, 
                encoding='utf-8', 
                errors='replace'
            )
    except:
        pass
    
    # 创建文件handler
    log_file = log_file or LOG_CONFIG["file_path"]
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=LOG_CONFIG["max_file_size"],
        backupCount=LOG_CONFIG["backup_count"],
        encoding='utf-8'  # 确保文件使用UTF-8编码
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    
    # 创建formatter
    formatter = logging.Formatter(LOG_CONFIG["format"])
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 添加handler到logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# 创建默认logger实例
default_logger = setup_logger()


if __name__ == "__main__":
    # 测试日志功能
    logger = setup_logger("test_logger", "DEBUG")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")