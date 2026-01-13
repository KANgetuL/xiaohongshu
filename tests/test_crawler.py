#!/usr/bin/env python3
"""
测试爬虫脚本
用于快速测试爬虫功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.crawler.request_handler import RequestHandler
from src.crawler.parser import XHSParser
from src.utils.logger import setup_logger


def test_request_handler():
    """测试请求处理器"""
    print("测试请求处理器...")
    
    handler = RequestHandler(use_proxy=False)
    
    # 测试请求
    test_url = "https://www.baidu.com"
    success, response, message = handler.make_request(test_url)
    
    print(f"请求结果: {success}")
    print(f"状态码: {response.status_code if response else 'N/A'}")
    print(f"消息: {message}")
    
    handler.close()
    return success


def test_parser():
    """测试解析器"""
    print("\n测试解析器...")
    
    parser = XHSParser()
    
    # 测试URL解析
    test_url = "https://www.xiaohongshu.com/explore/1234567890abcdef"
    note_id = parser._extract_note_id_from_url(test_url)
    print(f"URL解析测试: {note_id}")
    
    # 测试主题过滤
    test_note = {
        'title': '外卖翻车记',
        'content': '今天点的外卖太难吃了',
        'tags': ['外卖', '翻车', '美食']
    }
    
    is_match = parser.filter_by_theme(test_note, "外卖/点餐翻车")
    print(f"主题过滤测试: {is_match}")
    
    return True


def main():
    """主测试函数"""
    print("小红书爬虫模块测试")
    print("=" * 50)
    
    # 初始化日志
    logger = setup_logger("test", log_level="DEBUG")
    logger.info("开始测试爬虫模块")
    
    # 运行测试
    try:
        test_request_handler()
        test_parser()
        
        print("\n所有测试完成!")
        logger.info("测试完成")
        
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
        logger.error(f"测试失败: {str(e)}")


if __name__ == "__main__":
    main()