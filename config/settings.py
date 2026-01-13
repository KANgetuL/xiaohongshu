"""
小红书连环画爬取项目配置文件
包含爬虫设置、代理配置、数据过滤规则等
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
COMICS_DIR = PROCESSED_DATA_DIR / "comics"
LOG_DIR = DATA_DIR / "logs"

# 爬虫设置
CRAWLER_SETTINGS = {
    "target_theme": "外卖/点餐翻车",  # 目标主题
    "search_keywords": ["外卖翻车", "点餐翻车", "外卖漫画", "点餐漫画"],  # 搜索关键词
    "concurrent_requests": 3,  # 并发请求数（避免被封）
    "request_delay": 2,  # 请求延迟（秒）
    "timeout": 30,  # 请求超时时间
    "max_scroll_attempts": 5,  # 最大滚动次数（用于加载更多内容）
    "scroll_pause_time": 2,  # 滚动后暂停时间（秒）
}

# Selenium浏览器设置
SELENIUM_SETTINGS = {
    "use_selenium": True,  # 是否使用Selenium
    "browser": "chrome",  # 浏览器类型：chrome, firefox, edge
    "headless": True,  # 是否无头模式（不显示浏览器界面）
    "window_size": "1920,1080",  # 浏览器窗口大小
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "implicit_wait": 10,  # 隐式等待时间（秒）
    "explicit_wait": 15,  # 显式等待时间（秒）
    "download_images": True,  # 是否下载图片
    "save_screenshots": True,  # 是否保存截图（用于调试）
}

# 请求重试策略
RETRY_SETTINGS = {
    "max_retries": 3,  # 最大重试次数
    "retry_delay": 5,  # 重试延迟（秒）
    "retry_codes": [500, 502, 503, 504, 408, 429],  # 触发重试的状态码
}

# 代理设置（如果需要）
PROXY_SETTINGS = {
    "enabled": False,  # 默认禁用代理
    "proxy_list": [],  # 代理列表
    "rotate_proxy": True,  # 是否轮换代理
}

# 数据过滤规则
FILTER_RULES = {
    "min_image_width": 500,  # 最小图像宽度
    "min_image_height": 500,  # 最小图像高度
    "min_text_length": 10,   # 最小文本长度（中文字符）
    "allowed_image_formats": [".jpg", ".jpeg", ".png", ".webp"],  # 允许的图像格式
}

# 数据存储设置
STORAGE_SETTINGS = {
    "max_comics_per_theme": 100,  # 每个主题最大连环画数量
    "images_per_comic": 6,        # 每个连环画图片数量
    "batch_size": 10,             # 批量处理大小
}

# 标签配置
TAGS = {
    "primary_tags": ["外卖", "点餐", "翻车", "吃啥", "漫画"],
    "secondary_tags": ["外卖小哥", "美食", "吐槽", "搞笑", "日常"],
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",  # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": LOG_DIR / "crawler.log",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,  # 保留5个备份文件
}

# 创建必要的目录
def create_directories():
    """创建项目所需的目录结构"""
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        COMICS_DIR,
        LOG_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

# 运行创建目录
if __name__ == "__main__":
    create_directories()

# 反爬虫设置
ANTI_CRAWL_SETTINGS = {
    "max_retries_per_page": 3,  # 每个页面最大重试次数
    "retry_delay": 5,  # 重试延迟（秒）
    "human_behavior_delay": [0.5, 2],  # 人类行为延迟范围（秒）
    "page_load_timeout": 30,  # 页面加载超时时间
    "randomize_requests": True,  # 是否随机化请求
    "use_proxies": False,  # 是否使用代理
}