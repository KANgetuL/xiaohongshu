#!/usr/bin/env python3
"""
快速测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.crawler.selenium_handler import SeleniumHandler
from src.utils.logger import setup_logger


def quick_test():
    """快速测试"""
    print("快速测试小红书爬虫")
    print("=" * 50)
    
    # 初始化日志
    logger = setup_logger("quick_test", log_level="DEBUG")
    
    # 创建Selenium处理器（显示浏览器界面）
    print("启动浏览器...")
    handler = SeleniumHandler(headless=False)
    
    try:
        # 测试直接搜索
        keyword = "外卖翻车"
        print(f"\n1. 测试搜索: {keyword}")
        
        source = handler.search_xiaohongshu_direct(keyword, max_scrolls=1)
        
        if source:
            print("✓ 搜索成功")
            print(f"  页面标题: {handler.driver.title}")
            
            # 保存页面源代码供调试
            with open("test_search_page.html", "w", encoding="utf-8") as f:
                f.write(source[:5000])  # 只保存前5000字符
            print("  页面源代码已保存到: test_search_page.html")
            
            # 提取图片URL
            image_urls = handler.extract_image_urls()
            print(f"  提取到 {len(image_urls)} 张图片")
            
            if image_urls:
                print(f"  第一张图片: {image_urls[0][:80]}...")
        else:
            print("✗ 搜索失败")
        
        input("\n按Enter键继续测试笔记页面...")
        
        # 测试笔记页面（使用已知的笔记ID）
        print("\n2. 测试笔记页面")
        test_note_id = "6587b9c2000000001f01f6a1"  # 这是一个示例ID，实际可能需要替换
        print(f"  尝试访问笔记: {test_note_id}")
        
        note_source = handler.get_note_page_direct(test_note_id)
        
        if note_source:
            print("✓ 笔记页面访问成功")
            print(f"  页面标题: {handler.driver.title}")
            
            # 保存页面源代码
            with open("test_note_page.html", "w", encoding="utf-8") as f:
                f.write(note_source[:5000])
            print("  笔记页面源代码已保存到: test_note_page.html")
        else:
            print("✗ 笔记页面访问失败")
            print("  这可能是因为笔记ID无效或需要登录")
        
        print("\n✓ 测试完成")
        
    except Exception as e:
        print(f"\n✗ 测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        input("\n按Enter键关闭浏览器...")
        handler.close()
        print("✓ 浏览器已关闭")


if __name__ == "__main__":
    quick_test()