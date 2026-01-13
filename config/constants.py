"""
常量定义文件
包含项目中使用到的常量值
"""

# 文件相关常量
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
ANNOTATION_FILE_NAME = "annotations.json"
META_FILE_NAME = "meta.json"

# 数据质量检查常量
QUALITY_CHECKS = {
    "PASSED": "passed",
    "FAILED": "failed",
    "PARTIAL": "partial"
}

# 爬虫相关常量
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# 小红书API相关常量（示例，需要根据实际分析调整）
XHS_API = {
    "search_url": "https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/search/notes",
    "detail_url": "https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/note/{note_id}",
}

# 数据采集状态
STATUS = {
    "PENDING": "pending",
    "PROCESSING": "processing",
    "COMPLETED": "completed",
    "FAILED": "failed",
}

# 错误码
ERROR_CODES = {
    "SUCCESS": 0,
    "NETWORK_ERROR": 1001,
    "PARSER_ERROR": 1002,
    "STORAGE_ERROR": 1003,
    "VALIDATION_ERROR": 1004,
    "IMAGE_ERROR": 1005,
    "TEXT_ERROR": 1006,
}

# 数据格式模板
DATA_TEMPLATE = {
    "comic_info": {
        "id": "",
        "title": "",
        "theme": "",
        "source_url": "",
        "crawl_time": "",
        "total_images": 0,
        "quality_check": "",
        "status": ""
    },
    "images": [],
    "tags": [],
    "metadata": {
        "version": "1.0",
        "created_at": "",
        "updated_at": "",
        "data_source": "xiaohongshu"
    }
}